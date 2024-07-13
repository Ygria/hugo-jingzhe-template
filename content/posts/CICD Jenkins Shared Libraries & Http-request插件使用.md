---
title: CICD Jenkins Shared Libraries & Http-request插件使用

date: 2021-11-23 
tags:
- 编程
- 运维
---



> 前篇：
1、Jenkins的搭建和简介：https://www.jianshu.com/p/ca4886e11720
2、Jenkins Gitlab集成，使用WebHook触发构建：https://www.jianshu.com/p/ca4886e11720

之前我搭建的开发环境的Jenkins，经过一年多时间的积累和组内使用，已经为二十多个项目提供了部署运维环境。在需要快速迭代部署的时候，Jenkins的规范化和自动化执行节约了大量的时间成本。

# 目前存在问题
1、搭建流水线时，大部分步骤和代码都是可以复用的，但没有复用的方法，不得不进行大段代码的复制粘贴。
2、代码部署到托管平台逻辑未能解耦，如果托管平台变更，目前所有存量脚本都需要变更。
3、调用HTTP接口的脚本都使用`shell`中的`curl`指令实现，存在较多的转义字符和参数拼接，代码可读性较低，不容易维护，并且很容易出错，接口的请求结果也需要自己处理。

经过调研，使用了公用共享库（ `Shared Libraries` ）和`http-request`插件，完美解决了这些问题。
# Shared Libraries 配置和使用
## 配置
进入Jenkins首页后，点击左侧【系统管理】；
![image.png](https://cdn.jsdelivr.net/gh/Ygria/Pictures@main/20240417152626.png)


搜索“Global pipeline Libraries”，找到共享仓库配置。

配置的地址是gitlab上的代码仓库，方便公用脚本的版本管理和维护。
![image.png](https://cdn.jsdelivr.net/gh/Ygria/Pictures@main/20240417152637.png)

## 脚本编写
编写规范和目录结构，参考：https://www.jenkins.io/zh/doc/book/pipeline/shared-libraries/
以下为简单的使用示范：
1、在脚本代码仓库中，添加：`src/deploy/DeployHelper.groovy`
```groovy
def hello() {
    echo "Hello World!!!!"
}
```
2、在流水线脚本中，头部增加引入：
```groovy
@Library('SharedLibraries')
import deploy.DeployHelper
```
在流水线脚本中使用：
```java
script {
    DeployHelper deployHelper = new DeployHelper()
    deployHelper.hello()   
}
```
优点：
1、可以灵活使用Jenkins中已经安装的插件，不需要另外的依赖。
2、不需要另外给脚本授权（原本脚本在sandbox中执行，使用部分groovy公共类库时需要另外的授权。）

# http-request
在脚本内部声明式地调用HTTP接口。
[https://www.jenkins.io/doc/pipeline/steps/http_request/](https://www.jenkins.io/doc/pipeline/steps/http_request/)
使用该插件要求的Jenkins版本较高，进行了升级。由于之前配置了清华镜像，无法自动升级，选择去官网下载了安装包后，替换Jenkins内安装包，之后重启即可。
http-request使用较为简单，下面给出两个比较特别的范例：
1、上传文件（注意：multipartName 为文件参数的名称）
```groovy
 def uploadBuildFile = httpRequest contentType: 'APPLICATION_OCTETSTREAM',
            httpMode: 'POST',
            consoleLogResponseBody: true,
            customHeaders: [[name: 'Authorization', value: "basic ${token}"]],
            url: "http://${ip}/upload/${repoName}",
            uploadFile: "${filepath}",
            multipartName: "files"
```
2、参数payload为`JSONArray`：

```groovy
import groovy.json.JsonOutput
def restartResponse = httpRequest contentType: 'APPLICATION_JSON',
            httpMode: 'POST',
            consoleLogResponseBody: true,
            url: "http://${ip}/status/reboot",
            customHeaders: [[name: 'Authorization', value: "basic ${token}"]],
            requestBody: JsonOutput.toJson([[a: "${ip}", b: ["${serverEndpoint}"]]])
```
 值得注意的是，requestBody对应的参数，如果是JSONObject对应的JSONString，插件内部会自动进行反序列化，而如果是JSONArray，需要使用JsonOutput进行反序列化，不然会报参数错误。
# 小结
使用共享脚本库，进一步提高了运维效率，尽量避免重复的劳动，降低了脚本的维护成本。
Jenkins的灵活、易于拓展可以给我们的工作带来很多方便，使用起来也是非常的有意思~