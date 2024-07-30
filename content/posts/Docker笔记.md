---
title: Docker笔记
date: 2018-09-10
slug: docker-notes
tags:
  - 运维
---

# 常用指令

```docker images``` 列出本地 docker 镜像 
```docker ps -a``` 	列出所有正在运行的容器 
```docker stop containerID```	停止容器
```docker start containerID```	开始容器
```sudo docker exec -it containerID /bin/bash```  	进入容器内
```linux --mount``` 	 挂载 Unix 文件系统（ Unix File System ）之外的文件，或使用 Volume 数据卷。


容器互联：

推荐将容器加入自定义的Docker网络，连接多个容器，或使用```--link``` 指令。

# 定义

基于Linux内核和 LXC (Linux Container) 技术，对进程进行封装和隔离，属于操作系统层面的虚拟化技术，在容器的基础上，进行了进一步的封装，从文件系统、网络互联到进程隔离等等，极大的简化了容器的创建和维护。

# 优势

相较于传统的虚拟机技术，docker 具有更加轻量级、易于管理和并发的特点。

**与传统虚拟机比较**

| 特性    | 容器        | 虚拟机   |
| ----- | --------- | ----- |
| 启动    | 秒级        | 分钟级   |
| 硬盘使用  | 一般为MB     | 一般为GB |
| 性能    | 接近原生      | 弱于    |
| 系统支持量 | 单机支持上千个容器 | 一般几十个 |

# Docker 基本概念：

+ 镜像（ Image ）
+ 容器 （ Container ）
+ 仓库 （ Repository ）


## 镜像

使用pull指令，可以拉取 DockerHub 中的开源镜像到本地使用。
docker pull mysql
docker images 列出本地的镜像

### 定制镜像

使用 DockerFile

FROM scratch 
FROM指令为以什么为基础镜像，若为scratch意味着不以任何镜像为基础。



## 容器

容器之于镜像，如同实例之于类，创建容器，意为给镜像生成了一个实例。
> docker --name mysql -p 3306:3306 -d mysql
若不使用-d，容器会将输出的结果（STDOUT）打印到宿主机上。
如果使用了-d参数运行容器，容器会在后台运行，并不会在前台输出结果。若要看输出，可使用docker logs containerID指令进行查看。


## 仓库

在定制好个人的镜像后，可以搭建仓库进行存储。

