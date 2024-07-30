---
title: CICD Jenkins & Gitlab集成 WebHook触发构建
slug: how-to-use-jenkins3
date: 2020-06-06 
tags:
- 编程
- 运维
---


在上一篇博客中，我们学习了`Jenkins`的搭建和插件+流水线的基本使用方法，`Jenkins`极大地提升了部署效率。
最近想学习一下如何集成`GitLab webhook`，实现进一步解放双手，目标：
- 推送（`git push`）触发构建
- 推送到指定分支触发构建
- 根据`commit`的文件，结合`mvn -pl `指令，实现部分增量构建，并记录`commit`信息

推送事件也可以换成`Tag push events`、`Merge request events`等其他触发条件，根据需要自由选择。
# 基础实现
使用`Gitlab Hook Plugin`，并在Jenkins和GitLab中分别配置。

## 下载并配置插件
![image.png](https://cdn.jsdelivr.net/gh/Ygria/Pictures@main/20240417153252.png)


![image.png](https://cdn.jsdelivr.net/gh/Ygria/Pictures@main/20240417153238.png)

## 在`GitLab`中配置
![image.png](https://cdn.jsdelivr.net/gh/Ygria/Pictures@main/20240417153303.png)


![image.png](https://cdn.jsdelivr.net/gh/Ygria/Pictures@main/20240417153312.png)


![image.png](https://cdn.jsdelivr.net/gh/Ygria/Pictures@main/20240417153324.png)



![image.png](https://cdn.jsdelivr.net/gh/Ygria/Pictures@main/20240417153333.png)


**至此，目标中的前两条，推送构建和推送到指定分支构建实现！**
# 进阶实现
从上述过程，我们也可以看出，`WebHook`的本质就是从`GitLab`发了一条请求，`Jenkins`配置了一个终端地址（`endpoint`）来接收，从而实现了两个步骤的串联。
这个请求实质上就是一条`HTTP POST`请求。
相信接触过服务互相调用的小伙伴们都不陌生。有了请求体，我们自然可以拿到自己想要的东西，进行进一步的处理了。
![image.png](https://cdn.jsdelivr.net/gh/Ygria/Pictures@main/20240417153344.png)


## Jenkins插件:Generic WebHook Trigger Pugin
![image.png](https://cdn.jsdelivr.net/gh/Ygria/Pictures@main/20240417153354.png)

从插件简介来看，支持接收任何一个`HTTP`请求，当然也包括接收`GitLab`发送的请求。
### 在`Jenkins Job`中配置接收地址
![image.png](https://cdn.jsdelivr.net/gh/Ygria/Pictures@main/20240417153403.png)

### 配置鉴权token
![image.png](https://cdn.jsdelivr.net/gh/Ygria/Pictures@main/20240417153413.png)


我直接使用`admin`帐号创建，在发送请求时需要携带此token。
### GitLab配置
在Gitlab中的配置与上文相同，格式为：
`http://admin:${token}@${JENKINS_IP}:${PORT}/generic-webhook-trigger/invoke`
填上刚刚配置生成的`token`和自己的`Jenkins`地址和端口即可。
同样可以使用自带的测试来测试连接，返回200成功。
- 如果返回`404`，看配置的地址是否有误
- 返回`403`，查看权限配置是否有误
**至此，连接建立成功！**

# 编写流水线脚本

关于如何使用声明式流水线，上一次的博客已有所介绍。这里主要说明如何加入触发器语法。
## 流水线触发器语法
![image.png](https://cdn.jsdelivr.net/gh/Ygria/Pictures@main/20240417153423.png)

要从请求体中拿到所需要的参数，可以通过配置获取JSONPath参数实现。

在流水线中加入下列语句，**即可当作变量在流水线脚本中使用。**

```groovy
 triggers {
        GenericTrigger(
            genericVariables: [
              [key: 'branch', value: '$.ref'],
              [key:'commitText', value:'$.commits']
            ],
            causeString: 'Triggered on $branch' ,
            printContributedVariables: false,
            printPostContent: false
        )
    }
```
- 序列化JSON
要想在pipeline脚本中将字符串反序列化成JSON对象，可以引入 `Pipeline Utility Step`插件，该插件提供了一些工具方法。
![image.png](https://cdn.jsdelivr.net/gh/Ygria/Pictures@main/20240417153442.png)



```groovy
def commits = readJSON text: commitText
```
> 流水线脚本使用`Groovy`语言，该语言基于`Java`编写，也集成了一些有趣的特性。在IDEA中编写只需要配置`Groovy Library`即可。

## 核心方法
- 根据commits，定义patternMap，匹配到指定正则文件格式，构建指定组件。

```groovy
    def modifiedFile = [];
    for (commit in commits) {
            modifiedFile.addAll(commit.getAt("added").findAll())
            modifiedFile.addAll(commit.getAt("modified").findAll())
            modifiedFile.addAll(commit.getAt("removed").findAll())
        }

        def buildComponents = new HashSet();
        def patternMap = ['mark-engine-manager/.*': 'manager', 'mark-tools/.*': 'web','mark-engine-dm/.*':'dm','mark-engine-web/.*':'web',
        'mark-engine-uc/.*':'uc','mark-engine-gateway/.*':'gateway'];
//遍历所有修改了的文件
        for (file in modifiedFile) {
            for(entry in patternMap.entrySet()){
                if (file ==~ entry.key) {
                    buildComponents << entry.value;
                }
            }
        }
```
- 根据需要构建的组件，拼接`maven`构建指令。
```groovy
String mvnCmd = 'mvn clean install -Dmaven.test.skip=true'
for(component in buildComponents){
      mvnCmd = mvnCmd + ' -pl mark-engine-'+component+',';
}                    
```
**经过调试和测试push，三个目标全部完成。**
# 总结
**一切都是代码**，CICD当然也可以使用代码实现。经过实践我们可以探索出Jenkins更多有趣的玩法。