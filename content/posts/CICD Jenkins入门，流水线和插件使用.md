---
title: CICD：Jenkins入门，流水线和插件使用

date: 2020-05-14 
tags:
- 编程
- 运维
---
最近，我们使用的开发服务器被回收了，换了一台新的服务器，CI/CD平台需要重新搭建。
我的运维能力一直薄弱，所以借此机会学习了一番如何使用Jenkins进行持续集成开发和部署，实践并踩了一些坑，在此记录一下。

# 引言

 ## 假如没有CI/CD平台
 想要部署到服务器，我们需要本地打包上传至服务器，或上传源码至服务器上打包，覆盖原来的安装包，进行部署。

当所需要部署的只是一个jar包或者只是一个服务，并且代码不经常更新，这样是可以的。但是开发过程中，更常见的是代码经常迭代更新，并且项目中有多个组件。
这带来了大量的机械重复劳动，打包、上传、构建、测试、发布，如果都由人工操作，很容易混淆代码版本、不易跟踪异常。如果代码有多个分支版本，需要应对多个测试/生产环境，劳动量会指数级别飙升，到人无法承受的地步。
而Jenkins提供了解决方案，使我们可以一劳永逸地应对部署。

# Jenkins可以做什么
它的流水线操作正如其名，将机械的工作流程提炼出来，重复执行，可以定义成定时操作，可以定义触发条件，可以填写参数，可以写入控制语句。
代替我们完成：
1、拉取源码至服务器（与代码管理平台直接集成，可集成gitlab/svn等）
2、打包源码（可选择使用maven、nodeJS等等打包工具）
3、测试
4、准备环境
5、发布
总之，一切需要的工作，都可以定义成流水线里的一个流程。



# Jenkins搭建与配置

本次安装的Jenkins是Jenkins中文社区提供的中文镜像版，不仅做了汉化，Jenkins可以灵活使用的1500多个插件也提供了国内的镜像地址，安装只需要一条docker指令。

## 1、环境准备
1、查看系统版本，预留空间和Jenkins运行端口
2、安装docker

## 2、快速开始
- 创建容器

```bash
docker run -d -v /jenkins_home:/var/jenkins_home -u 0 -p 8786:8080  --name jenkins jenkinszh/jenkins-zh
```

**指令解释：**
`-d`： 后台运行
`-v`：将Jenkins主目录挂在出来
`-u 0` ：将系统用户传入（0为root用户），避免一些权限问题
`-p` ：指定映射到宿主机的端口，如果8786端口被占用也可以使用其他端口
`--name`：指定运行容器名称为jenkins
`jenkinszh/jenkins-zh` Jenkins中文社区提供的镜像名称，docker会检测本地有无该镜像，如果没有，会自动拉取。

* `docker logs jenkins ` 查看日志

运行之后，访问宿主机ip+ 8786（指定端口），看到Jenkins初始页面。
![image.png](https://cdn.jsdelivr.net/gh/Ygria/Pictures@main/20240417152739.png)





Jenkins创建成功！

## 3、初始化

稍微等待之后，自动跳转至管理员登录页面。
![image.png](https://cdn.jsdelivr.net/gh/Ygria/Pictures@main/20240417152753.png)


[index.html](..%2F..%2F..%2Ftravel-trace%2Findex.html)
创建容器时我们已经将该目录挂载到宿主机了，所以可以直接访问映射出的文件：
  `cat /jenkins_home/secrets/initialAdminPassword`
  
  也可以使用`docker exec`指令访问容器内文件:
  `docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword` 
输入密码，登陆进入新手入门页面。

![image.png](https://cdn.jsdelivr.net/gh/Ygria/Pictures@main/20240417152811.png)


选择安装推荐插件。
如果有安装失败的，可以点击继续，直接跳过，进入Jenkins管理页面，等待后续使用时再进行安装。

![image.png](https://cdn.jsdelivr.net/gh/Ygria/Pictures@main/20240417152823.png)
## 4、新建声明式流水线

点击左侧新建item，可以创建新的任务，如下图所示。

![image.png](https://cdn.jsdelivr.net/gh/Ygria/Pictures@main/20240417152841.png)


选择流水线。

现在就可以创建流水线，用于部署正在开发的项目了。

## 5、常用流水线 + 工具 +插件 使用及配置

流水线语法请参考：

[如何使用声明式流水线](
http://jenkins-zh.cn/wechat/articles/2020/05/2020-05-08-how-to-use-the-jenkins-declarative-pipeline/)
可以使用Jenkins自带的流水线语句生成工具来辅助编写：

![image.png](https://cdn.jsdelivr.net/gh/Ygria/Pictures@main/20240417152856.png)



插件和其他配置均为可选，根据使用需求灵活安装。
在此记录一些插件/工具，并给出它们在流水线脚本中的使用范例。
### 一、集成git/gitlab
* 配置凭据用于登陆验证gitlab
![image.png](https://cdn.jsdelivr.net/gh/Ygria/Pictures@main/20240417152911.png)

* 参考语法
```groovy
steps {
	git branch: 'dev', credentialsId: '***', url: 'https://git.***.git'
}
```
将创建好的凭据填入。


### 二、maven/nodeJS等构建工具使用
 * 工具安装和配置
 在全局工具配置中配置NodeJS和Maven
![image.png](https://cdn.jsdelivr.net/gh/Ygria/Pictures@main/20240417152931.png)



* 使用maven打包
```groovy
steps {
    script {
     sh "mvn clean install -Dmaven.test.skip=true -Plinux"
    }
}

```
* 使用`ln -s`指令支持脚本中运行
若执行时报错无mvn指令（或npm、cnpm等），说明jenkins在/usr/local/bin目录下没有找到相应的指令。可以通过建立软连接方式实现支持。
![image.png](https://cdn.jsdelivr.net/gh/Ygria/Pictures@main/20240417152952.png)

可以将宿主机的工具包直接放入挂载目录，进行映射，也可以在工具配置中选择自动下载，在Jenkins内中再次安装。

### 三、连接其他机器/执行脚本
* 容器内
直接使用下列流水线语言格式即可。
```groovy
 script {
     sh "***"
    }
```
* 执行宿主机内脚本
（1）挂载进入容器内部
缺点：若脚本运行环境和操作内容是宿主机文件，该方法无法实现。
（2）使用ssh
* 语句使用
开启免密校验，使用` sh "ssh -o StrictHostKeyChecking=no -l root ${IP} '****'"`格式的指令。
注意指令格式为双引号内套单引号，单引号内为希望在宿主机执行的指令
* 插件使用
- **SSH Pipeline Step**
根据示例，可得，事先添加好凭据之后，很容易在指定ip上（包括宿主机）执行文件传输、脚本执行等操作。
```groovy
def host = [:]
host.name = "host"
host.host = ""
host.allowAnyHosts = true
 
node {
    withCredentials([usernamePassword(credentialsId: '', passwordVariable: 'password', usernameVariable: 'userName')]) {
        host.user = userName
        host.password = password
        stage("SSH Steps Rocks!") {
            writeFile file: 'test.sh', text: 'ls'
            sshCommand remote: host, command: 'for i in {1..5}; do echo -n \"Loop \$i \"; date ; sleep 1; done'
            sshScript remote: host, script: 'test.sh'
            sshPut remote: host, from: 'test.sh', into: '.'
            sshGet remote: host, from: 'test.sh', into: 'test_new.sh', override: true
            sshRemove remote: host, path: 'test.sh'
        }
    }
}
```
构建结果
![image.png](https://cdn.jsdelivr.net/gh/Ygria/Pictures@main/20240417153012.png)






- **Publish Over SSH**
![image.png](https://cdn.jsdelivr.net/gh/Ygria/Pictures@main/20240417153033.png)

在Jenkins管理/系统管理/PublishOverSSH的相关配置中配置所需要的宿主机IP、用户、密码等等信息
![image.png](https://cdn.jsdelivr.net/gh/Ygria/Pictures@main/20240417153042.png)

可以在展开的高级设置中配置SSH服务器。
查看[Publish-Over-Server 插件说明]([https://plugins.jenkins.io/publish-over-ssh/](https://plugins.jenkins.io/publish-over-ssh/)
)获取高级用法。







### 四、集成docker
因为我们的Jenkins服务是作为docker容器运行的，所以需要在容器内调用docker命令。
容器内调用docker命令有两种：
* DinD（Docker in Docker）（不推荐）
容器内部再安装一个Docker应用。但是这种方法不推荐，参考：[使用 Docker-in-Docker 来运行 CI 或集成测试环境？三思！](https://zhuanlan.zhihu.com/p/27208085)


* **DooD（Docker-outside-of-Docker）（推荐）**
> 原理说明：
> Docker采用的是Client/Server架构，我们常用的docker命令只是docker client，通过该命令行执行命令的时候，实际是通过client与docker engine通信。
>默认情况下，Docker的守护进程会生成一个socket（`/var/run/docker.sock`）文件来进行本地进程通信，智是UNIX域套接字，可以通过文件系统（而非网络地址）进行寻址访问。

根据上述原理，我们可以通过挂载宿主机socket文件进入Jenkins，使Jenkins可以使用宿主机docker命令。
* **直接使用第四点中的SSH用法执行：** 
```
 sshCommand remote: host, command: 'docker *** '
```





### 五、生成归档文件
示例：
```groovy
pipeline {
    
    agent any

 stages {
     
     stage("build"){
         steps{
             sh 'touch archive.jar'
         }
         
     }
     
     stage('archive') {  
            steps {
                archiveArtifacts artifacts: 'archive.jar', fingerprint: true 
            }
    }}
}
```
在build过程中生成归档文件，在archive过程中归档。
![image.png](https://cdn.jsdelivr.net/gh/Ygria/Pictures@main/20240417153056.png)


在此页面上可以直接下载归档好的文件。


# 其他（待补充）
1、配置时区
打开系统管理/命令行，运行：
`System.setProperty('org.apache.commons.jelly.tags.fmt.timeZone', 'Asia/Shanghai')`
