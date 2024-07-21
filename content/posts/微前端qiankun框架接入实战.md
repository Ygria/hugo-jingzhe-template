---
title: 微前端qiankun框架接入实战
date: 2021-08-26
tags:
  - 编程
  - 前端
---


# 背景
随着项目的演进，前端的业务架构也会变得更加庞大、复杂，并常常会出现需要模块复用的场景：
1、组件复用，例如统一的导航栏、侧边栏、路由权限处理逻辑等
2、模块级别复用，例如统一的用户管理模块、文档中心等
3、系统级别复用，总的系统由多个系统组合而成，不同的系统可能由不同的开发团队维护、使用不同的技术栈开发。

除了代码层面复用（复制粘贴），也需要更加完善的模块和系统复用方案。引入微前端，将代码根据业务逻辑划分至不同的项目之中进行维护，能够有效的降低维护难度，每个系统既可以独立运行、独立部署，也可以组合起来构成一个完整的系统，能够更快速地响应客户的需求。

----
之前页面嵌入都使用`iframe`，简捷易用，两行代码就可以搞定，但在加载速度方面略有些不尽人意。可以看这篇➡[Why Not Iframe](https://www.yuque.com/kuitos/gky7yw/gesexv)
听说隔壁项目组都已经用`qiankun`用的飞起了，我们必不能落后于人~于是在赶鸭子上架下，使用了`qiankun`进行了一次完整的实践。

# 实战步骤

##  什么是`qiankun`
[qiankun官方文档](https://qiankun.umijs.org/zh/guide)
> `qiankun`是基于`single-spa`的封装，可以参考：https://single-spa.js.org/ .
`single-spa`是一个将多个单页面应用聚合为一个整体应用的 `JavaScript` 微前端框架。 
我们每个前端项目最终都会被打包成一个单页应用，该应用以index.html为入口，在其中引入打包后的js和css文件。

## 前端代码改造
`qiankun`在逻辑上，将前端应用划分为主应用（又称为基座应用）和微应用，主应用拉取微应用打包后的js，并设置一定的规则来控制微应用的生命周期（装载、卸载等），微应用则要暴露出生命周期钩子函数，供主函数调用。

在主应用下安装依赖:

```javascript
npm i qiankun --save-dev
```
###  主应用改造
#### 1、改造入口文件

`mainApp/main.js`
```javascript
import { registerMicroApps, start } from "qiankun"
let msg = {
   // 传入子应用的内容
};

// 注册子应用
registerMicroApps(
    [
        {
            name: "turing-permission",
            entry: "//127.0.0.1:9527",
            //  指定子应用的挂载容器
            container: '#subApp',
            activeRule: "#/turing-permission",
            props: msg
        },
        {
            name: "turing-moss",
            entry: "//127.0.0.1:9528",
            //  指定子应用的挂载容器
            container: '#subApp',
            activeRule: "#/turing-moss",
            props: msg
        },
    ],

);

const request = url => { return fetch(url, { referrerPolicy: 'origin-when-cross-origin' }) };
start({ prefetch: true, sandbox: { experimentalStyleIsolation: true }, fetch: request });
```
说明：
参看[qiankunAPI说明文档](https://qiankun.umijs.org/zh/api)
- `registerMicroApps`方法接收子应用列表。 参数解释：
1、name - 子应用名称
2、entry - 主应用使用fetch请求，从该入口获取子应用的js、css等资源，注意该地址需要去掉协议（http/https）。部署到线上时，该地址可填写为部署地址IP + 端口 + /subApp的形式，使用nginx代理，后面说到部署时会给出示例。此处为本地开发时的地址。
3、container - 子应用挂载的DOM根节点。需要注意在子应用加载时，该DOM节点必须存在，否则会报子应用挂载失败错误
4、activeRule - 触发子应用挂载的条件。如果子应用使用的路由为hash模式，则需要加`#`，如果使用的是history 模式，则不需要加`#`。本次实战使用的路由模式均为hash模式（也是默认的模式）
该方法可以自定义方法实现
5、props： 可以定义主应用传入到子应用的值。可以将主应用的store和router都传过去。

- `start`方法
参考API文档进行配置。这里踩了一个坑，如果沙箱隔离配置为 `sandbox: { strictStyleIsolation: true }`,可能会导致element-UI组件样式被影响（下拉框挂到左上角）。
#### 2、通信
应用在鉴权中，用于同步登录状态和传递token（若使用同一个域下的Cookie来鉴权，此处可忽略）：
```
import qiankunActions from '@/store/qiankun'
//   登录成功后，获取到访问令牌
const { permissionList, accessToken } = await store.dispatch('user/getInfo')
qiankunActions.setGlobalState({ token: accessToken });
```
#### 3、提供子应用挂载的根节点
`App.vue`
```vue
<template>
    <div id="container" class="container">
        <head-top v-if="$route.name != 'Home'" />
        <router-view />
        <div  id="subApp" />
    </div>
</template>
```
注意：如果使用了<router-view/>，该节点需要与最高层级的<router-view>同级！


### 子应用改造
子应用无需安装qiankun依赖
#### 1、入口文件改造
`subApp/main.js`
```
let instance;
function render(props) {
  let container = props ? props.container : undefined;
  instance = new Vue({
    router,
    store,
    render: h => h(App),
  }).$mount(container ? container.querySelector('#app') : '#app');
}
if (!window.__POWERED_BY_QIANKUN__) {
  render();
}
export async function bootstrap() { 
}

export async function mount(props) {
  props.onGlobalStateChange((state, prevState) => {
    store.commit('user/SET_TOKEN', prevState.token)
  }, true);
  render(props);
}
export async function unmount() {
  console.log('[turing-permission] unmounted');
  instance.$destroy();
  instance = null;
}
```
从代码逻辑易得，在子应用中暴露出的mount钩子方法中执行了Vue的render方法。该方法根据传入的props（会将container传入），找到对应的dom节点，在该dom节点下插入子应用的模板代码，再执行Vue的mount方法。需要区分两个mount：一个是子应用的挂载，一个是Vue应用的挂载。
通过`window.__POWERED_BY_QIANKUN__`，可以判断是否是被嵌入在主应用中运行。
`props.onGlobalStateChange((state, prevState) => {
    store.commit('user/SET_TOKEN', prevState.token)
  }, true);`第二个参数是必须的，用于从主应用中获取到token。
#### 2、router改造
若使用history模式，`mode: 'history'`,需要增加`base: '/sub-app'`
`router/index.js`
```
const createRouter = () =>{
    // 微应用运用的路由是只读的，需要先进行全量的定义
    let actualRoutes = window.__POWERED_BY_QIANKUN__ ?constantRoutes.concat(asyncRoutes) : constantRoutes;
    let prefix = "/sub-app";
    //  若需要
    if(window.__POWERED_BY_QIANKUN__){
        actualRoutes.forEach(item => {
            item.path = prefix + item.path;
            item.redirect = prefix + item.redirect;
        })
    }

    return new Router({
        mode: 'hash',
        routes: actualRoutes
    });
}
const router = createRouter();
export default router
```
#### 3、打包地址改造
`vue.config.js`
```
const { name } =require(`./package`);
...
 configureWebpack: {
    name: name,
    resolve: {
      alias: {
        '@': resolve('src')
      }
    },
    output: {
      // 把子应用打包成 umd 库格式
      library: `${name}-[name]`,
      libraryTarget: 'umd',
      jsonpFunction: `webpackJsonp_${name}`,
    }
  },
```
新增`public-path.js`，并引入到`main.js`中
`src/public-path.js`
```
if (window.__POWERED_BY_QIANKUN__) {
  __webpack_public_path__ = window.__INJECTED_PUBLIC_PATH_BY_QIANKUN__;
}
```
#### 4、请求改造
1）baseUrl改造（方便之后的代理）
```
let baseURL = window.__POWERED_BY_QIANKUN__ ? '/turing-moss' + process.env.VUE_APP_BASE_API : process.env.VUE_APP_BASE_API
// 创建axios实例
const service = axios.create({
  baseURL: baseURL, // api的base_url
  timeout: 300000 // 请求超时时间
})

```
2) 鉴权请求头改造，适配改造后的鉴权方案
```
function createHeader(token, isformdata) {
  var contentType = isformdata ? 'multipart/form-data' : 'application/json'
  let headers = {
    'Content-Type': contentType,
    'time': new Date().getTime(),
    'salt': rdNum(6),
  }
  if (window.__POWERED_BY_QIANKUN__) {
    headers.Authorization = store.getters.token
    headers.useToken = true
  }
  return headers;
}
```
## 后端代码改造
主要是鉴权改造。
鉴权顺序：
用户在主应用登录➡主应用后端生成令牌传递给前端➡前端微应用共享该令牌，在请求微应用后端时携带➡微应用后端拿到令牌后，请求主应用接口，判断是否合法，并获取用户信息

原先的鉴权方案都是CAS鉴权。
### 主应用后端
#### 1、生成token，并在请求用户信息接口中返回给前端（使用OAuth2）
```
  UserDetails userDetails = domainUserDetailsService.createSpringSecurityUser(userInfoDTO);
                Authentication userAuth = new 
PreAuthenticatedAuthenticationToken(userDetails,userDetails.getPassword(),userDetails.getAuthorities());
String token = tokenProvider.createToken(userAuth,true);
```
#### 2、提供内部鉴权接口
```
   @GetMapping("/inner/tokenValid")
    AuthResp validToken(String token){
        System.out.println(token);
        if(tokenProvider.validateToken(token)){
            Authentication authentication = tokenProvider.getAuthentication(token);
            String accountName = authentication.getName();
            System.out.println(authentication);
            return AuthResp.builder().accountName(accountName)
                    .isAuth(true).build();
        }else{
            //  权限校验失败
            return AuthResp.builder().accountName("")
                    .isAuth(false).build();
        }
```
### 微应用后端
#### 定义优先级高于CasFilter的自定义过滤器进行鉴权
```
@Order(0)
@Slf4j
@Component
public class TokenAuthorFilter implements Filter {


    @Resource
    UserService userService;
    @Resource
    AuthClient authClient



    @Override
    public void doFilter(ServletRequest servletRequest, ServletResponse servletResponse, FilterChain filterChain)
        throws IOException, ServletException {
        String accessToken = ((RequestFacade) servletRequest).getHeader("Authorization");
        HttpSession session = ((RequestFacade) servletRequest).getSession();
        if(((RequestFacade) servletRequest).getHeader("useToken")!=null && ((RequestFacade) servletRequest).getHeader("useToken").equals("true")){
            log.info("进入微前端鉴权逻辑");
            if(StringUtils.isNotBlank(accessToken) && session.getAttribute(AbstractCasFilter.CONST_CAS_ASSERTION) == null) {
                // 能够获取到token
               AuthResp authResp = authClient.authToken(accessToken);
                if (authResp.getIsAuth()) {
                    String accountName = authResp.getAccountName();
                    Assertion assertion = new AssertionImpl(accountName);
                    session.setAttribute(AbstractCasFilter.CONST_CAS_ASSERTION, assertion);
                    // assertion 非空：从assertion中获取数据
                    log.debug("从permission获取当前用户信息，用户名称 = {}", accountName);
                    session.setAttribute(Constants.SESSION_KEY,userService.getUserFullyByAccountName(accountName));
                }else{
                    throw new RuntimeException("qiankun主应用鉴权失败！");
                }

            }
        }
        filterChain.doFilter(servletRequest,servletResponse);
    }

}
```
此处逻辑：识别到携带`useToken`头的请求（此处头的名称支持自定义），请求主应用的后台，进行token的合法性校验，通过则执行后续逻辑，不通过抛出异常，前端跳转主应用的登录页。
### 部署
将main.js中微应用的地址改为//${IP}/subApp的形式，使用nginx进行部署。
配置（配置到server 80或 443下（https）），将subAppIp设置为微服务的地址。
![nginx配置参考](https://img-blog.csdnimg.cn/img_convert/a79582d6e748fdd54a9ccc637682f4ae.png)

本地进行联调时，需要将proxyTable代理至微服务地址。
至此，接入完成。
