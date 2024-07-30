---
title: Java | 记录基于CAS登录模块的几个安全问题的解决
slug: cas-problem
date: 2021-12-12
tags:
- 编程
- 后端
---

手头的项目的登录模块，基本都是集成了部门内封装出的基于CAS的中心鉴权组件，在安全扫描中暴露了一些问题，有些是因为没有合理的使用这一开源框架导致的，有的是通用的问题，在此记录问题和解决方案。
1、密码明文传输问题
2、页面无验证码、无登录防抖，易被暴力破解问题
3、开放重定向问题

# 密码明文传输
## 问题描述
用户输入的密码，虽然在页面的输入框中显示为“*****”，却在接口层面通过明文传输，易被抓包工具捕获。
## 解决思路
使用`RSA`非对称加密，前端对密码进行加密，后端解密后，再与数据库存储的凭证进行比对。
## 代码实现
### 前端
前端是在CAS项目中的casLoginView中进行改造，使用JavaScript (JQuery)  + HTML + CSS；
1、 改造登录结构代码 - 将原有的登录表单中的按钮进行隐藏，增加一个用于点击的登录按钮；
```html
  <form id = "fm1">
    <input id="username" name="username" class="input_user_name"
                           tabindex="1" placeholder="请输入用户名称" accesskey="n" type="text" value=""
                           maxlength="30" autocomplete="false">
    <input id="password" name="" class="input_password" tabindex="2"
                           placeholder="请输入登录密码" accesskey="p" type="password" value=""
                           maxlength="28" autocomplete="off">
     <input id="login_normal1" class="login-button" name="submit"
               accesskey="l"
               value="登 录" tabindex="3" type="button">
     <input id="login_normal" style="display: none"
               name="submit" accesskey="l"
               value="登 录" tabindex="3" type="submit">
</form>
```
注意，需要将原有的密码输入框input的name属性置为空字符串，或删去该属性，否则提交时会提交一个密文和一个明文。
2、引入用于加密的JS
下载JS，放在common/js目录下，并在页面引入。
```html
<script src="common/js/jsencrypt.min.js" type="text/javascript"></script>
```
3、登录逻辑改造
原先登录是触发了表单提交后，浏览器自带的`post`事件，将原有按钮进行隐藏，监听显示出来的登录按钮的点击事件。
可以使用回车监听方法，禁用原有回车登录方法，或也调用加密密码后提交的逻辑。
```javascript
<script type="text/javascript">
    $(document).ready(function(){
        if (window.top.location !== self.location) {
            top.location.replace(self.location);
        }
        $("#login_normal1").click( function() {
            if(!checkSubmit()){
                return
            }
            // 登陆验证之前，对密码进行加密处理
            const password = encrypt($('#password').val())
            $('#login_normal')
                .attr('name', "password")
                .attr('value', password)
            $('#login_normal').click()

        });
    });
    function encrypt(password) {
        var encrypt = new JSEncrypt()
          // 此处需要填入自己生成的密钥。
        encrypt.setPublicKey(``);
        return encrypt.encrypt(password);
    }
    function checkSubmit() {
        var username = $("#username").val().trim();
        var password = $("#password").val().trim();

        if (username == ''||username==null) {
            $('#username').focus();
            $('#msg1').html('请输入用户名！');
            return false;
        }
        if (password == ''||password==null) {
            $('#password').focus();
            $('#msg1').html('请输入密码！');
            return false;
        }
        return true;

    }
}
</script>
```
### 后端
后端仅需要在验证密码之前，对加密后的密码进行解密即可。
下面给出解密方法示例：
```java
private String decrypt(String password) throws Exception {
 BASE64Decoder base64Decoder = new BASE64Decoder();
    byte[] keyByte = base64Decoder.decodeBuffer(");
    PKCS8EncodedKeySpec keySpec = new PKCS8EncodedKeySpec(keyByte);
    KeyFactory keyFactory = KeyFactory.getInstance("RSA");
    RSAPrivateKey privateKey = (RSAPrivateKey)keyFactory.generatePrivate(keySpec);
    byte[] dataByte = base64Decoder.decodeBuffer(password);
    Cipher cipher = Cipher.getInstance("RSA");
    cipher.init(Cipher.DECRYPT_MODE, privateKey);
    byte[] result = cipher.doFinal(dataByte);
    return new String(result);
}
```
# 添加验证码
## 后端改造
集成验证码，对于后端来说没什么难度。引入`easy-captcha`或其他依赖；
```xml
<dependency>
   <groupId>com.github.whvcse</groupId>
    <artifactId>easy-captcha</artifactId>
    <version>1.6.2</version>
</dependency>
```
接口暴露：
```java
import com.wf.captcha.utils.CaptchaUtil;

@GetMapping("/capcha/code")
public void captchaCode(HttpServletRequest request,HttpServletResponse response) throws Exception {
    CaptchaUtil.out(request, response);
}

@GetMapping("/captcha/check")
public ResponseEntity<String> captchaCode(@RequestParam String code, HttpServletRequest request) throws Exception {
  boolean success = false;
  if (CaptchaUtil.ver(code, request)) {
      success = true;
  }
  CaptchaUtil.clear(request);
  String successStr =  success ? "ok" : "error";
  System.out.println("验证码验证结果 = "  + successStr);
  return ResponseEntity.ok(successStr);
}


```
## 前端改造

![image.png](https://cdn.jsdelivr.net/gh/Ygria/Pictures@main/20240417143825.png)


1、对前端登录页面稍加改造；可以进行样式的自定义适配。
```html
 <div class="input-p captcha">
   <div class="input__prepend captcha"></div>
    <input id="captcha" name=""
           class="captcha" tabindex="3"
           placeholder="请输入验证码" accesskey="p"
           maxlength="4" autocomplete="off">
    <img id="cimg"
         src=""
         title="看不清？点击更换另一个。" />
</div>
```
2、增加进入页面后，请求验证码、校验验证码、点击更换验证码等交互逻辑
```javascript
<script type="text/javascript">
    $(document).ready(function(){
        if (window.top.location !== self.location) {
            top.location.replace(self.location);
        }
        $("#login_normal1").click( function() {
            if(!checkSubmit()){
                return
            }
            // 验证码验证失败
            if(!validateCaptcha()){
                return;
            }
            // 登陆验证之前，对密码进行加密处理
            const password = encrypt($('#password').val())
            $('#login_normal')
                .attr('name', "password")
                .attr('value', password)
            $('#login_normal').click()

        });

        $("#cimg").click(function(){
            initCaptcha()
        })
        initCaptcha();
    });

    //
    function initCaptcha(){
        var _codeImage = $('#cimg');
        var rand = Math.random();
        var url = '/captcha/code?rand=' + rand;
        _codeImage.attr("src", url);
    }
    // 对验证码进行验证
    function validateCaptcha(){
        var isValid = false
        $.ajax({
            url: '/captcha/check?code=' + $('#captcha').val(),
            type: 'GET',
            async:false,
            success: function(data) {
                if (data) {
                    if(data === 'ok'){
                        isValid =  true
                    }else {
                        $('#msg1').html('验证码输入错误，请重新输入！');
                        //密码验证失败后，重新请求验证码
                        initCaptcha()
                        isValid =  false
                    }
                }
            }
        })
        return isValid
    }
    function checkSubmit() {
        var username = $("#username").val().trim();
        var password = $("#password").val().trim();
        var captcha = $("#captcha").val().trim();
        if (username > '' && password > '' && captcha > '') {
            $('#msg1').html("");
            return true;
        }
        else {
            if(!username || !password){
                $('#msg1').html('请输入您的用户名和密码');
            }else {
                $('#msg1').html('请输入验证码');
            }

            return false;
        }
    }
</script>
```
可以看到，在用户触发登录动作时，先校验了验证码是否合法，再去调用后台登录接口，这样可以一定程度上避免被暴力破解。
# 开放重定向问题
>  开放重定向问题的定义：https://www.wangan.com/articles/1132

简而言之，就是在我们服务的登录、登出地址中，将原本的服务地址${MY_SERVICE}替换成其他，也可以被CAS后端转发跳转。

```properties
http://${CAS}/cas/login?service=http://${MY_SERVICE}
http://${CAS}/cas/logout?service=http://${MY_SERVICE}
```


而经过排除和阅读CAS文档，发现是在我们配置认证客户端定义JSON时，将所有的serviceId都配成可以通配所有网址导致的！
```json
{
  "@class" : "org.apereo.cas.services.RegexRegisteredService", 
  "serviceId" : "^(https|imaps|http)://.*",
  "name" : "",
  "id" : 1000,
  "description" : "",
  "evaluationOrder" : 1,
  "theme": ""
}
```
容易得出，`serviceId`的值是一个正则表达式，仅当能匹配到正则时，才会进行跳转，不然会显示出：
![image.png](https://cdn.jsdelivr.net/gh/Ygria/Pictures@main/20240417143906.png)

根据官网的建议，应该将`serviceId`配置得越精确越好，配置成具体的网址，就能避免重定向到其他网站的问题了。
那么问题又来了，在进行部署之前，我们可能并不知道这个网址。如果已经进行了代码打包，就改不了这个配好的网址了，有什么办法从外部数据源或配置文件中读取呢？这样更改了其他服务的部署地址，CAS不需要重新打包，如果可以读取到动态的数据源，CAS组件甚至不用重启。
查阅官网：https://apereo.github.io/cas/5.3.x/planning/Getting-Started.html
关于Service的管理中，我们可以看到多种存储方案：
![image.png](https://cdn.jsdelivr.net/gh/Ygria/Pictures@main/20240417143925.png)


借助配置 + 内存管理方案，可以实现服务的动态配置。
给出我的实现代码：
```java
    @Value("${supportServiceId}")
    private String supportServiceId;


    @Bean
    public List inMemoryRegisteredServices() {
        final List services = new ArrayList<>();
        final RegexRegisteredService service = new RegexRegisteredService();
        service.setServiceId(supportServiceId);
        service.setName("moss");
        service.setId(1L);
        service.setTheme("moss");
        service.setDescription("MOSS2.0语义化系统");
        service.setEvaluationOrder(1);
        services.add(service);
        return services;
    }

```
这样就可以从CAS的服务配置中读取，当然也可以配置一个服务列表。需要将原有的`JSON`配置删去。
# 小结
分享了几个改造的方法，需要在现有的框架下进行尽量小的改动，后续可以考虑提取成通用的JS代码，降低其他服务的改造成本。



