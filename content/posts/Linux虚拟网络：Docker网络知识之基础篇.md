---
title: Linux虚拟网络：Docker网络知识之基础篇
slug: learn-linux-network
date: 2020-06-30
tags:
- 编程
---




我们在工作中应用了docker容器化技术，服务的部署、维护和扩展都方便了很多。然而，近期在私有化部署过程中，由于不同服务器环境的复杂多变，常常遇到网络方面的问题，现象为容器服务运行正常，但宿主机、容器之间网络不通。
本篇博客旨在总结：
- Linux虚拟网络及docker网络的基础知识
- 遇到网络问题时排查问题思路
- 常用指令和工具的使用

以上三部分作为之后的参考，本篇文章也将会在日后实践过程中逐渐补充。本篇为第一篇，主要介绍基础知识


# Linux网络虚拟化基础
## Network Namespace
> 网络命名空间，是Linux 2.6.x内核版本之后提供的功能，主要用于资源的隔离。namespace是实现网络虚拟化的重要功能，使用它，一个Linux系统可以抽象出多个网络子系统，各个子系统都有自己独立的网卡、路由表、iptables、协议栈等网络资源。不管是虚拟机还是容器，运行时仿佛自己都在独立的网络中。

`ip netns`命令用于完成对ns的各种操作，`ip netns exec`子命令用于在namespace执行指令。


## Veth Pair（Virtual Ethernet Pair）
> 成对虚拟设备端口。它总是成对出现，一端连着协议栈，一端彼此连着。从其中一个端口发出的数据包，可以直接出现在与它对应的另一个端口上，即使它们在不同的namespace中。

![Veth Pair功能：在不同的ns中通信](https://upload-images.jianshu.io/upload_images/6810620-8187694f1d4d7dd2.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)
如上图，一对veth-pair直接将两个namespace连接在一起。

- 使用如下图所示命令，测试veth pair功能
![测试使用veth pair连通两个namespace](https://upload-images.jianshu.io/upload_images/6810620-88e4ef5d99f13359.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)


## Bridge 网桥
veth pair打破了Network Namespace的限制，实现了不同Network Namespace之间的通信。但是veth pair的局限性也很明显，只能实现两个网络接口的通信。
Linux中引入网桥来实现多个网络接口之间的通信，可以将一台机器上的若干接口连通起来。在OSI网络模型中，网桥属于数据链路层。

![网桥连通多个端口示意图](https://upload-images.jianshu.io/upload_images/6810620-8b57f92a2c1941ce.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

和网桥相关的操作使用命令`brctl`，需要先安装`bridge-utils`工具包。安装指令：
`yum install bridge-utils`
## iptables/Netfilter
请参考：[iptables详解（1）：iptables概念](http://www.zsythink.net/archives/1199)

# Docker网络基础
Docker支持四种网络模式：host模式，container模式，none模式和bridge模式。默认使用的是桥接模式。
使用`docker network ls`指令可以查看到宿主机上所有的Docker网络：
![当前宿主机所有的docker网络](https://upload-images.jianshu.io/upload_images/6810620-1986bf9ba4a3a090.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)



## Bridge 桥接模式
> Docker在启动时，默认会自动创建网桥设备docker0，Docker在运行时，守护进程通过docker0为docker的容器提供网络通信服务。
当Docker启动容器时，会创建一对Veth Pair，并将其中一个veth网络设备附加到网桥docker0，另一个加入容器的network namespace中。

根据上一节中关于网桥的定义，我们很容易画出示意图：

![Docker网桥模型](https://upload-images.jianshu.io/upload_images/6810620-9d869758c007bf38.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

由上图可得，容器可以通过网桥互相通信。如果不想使用默认的网桥设备，也可以在启动docker daemon的时候使用`
--bridge==BRIDGE`参数指定其他网桥。
然而这还不够，Docker容器还需要与外网进行相互通信。这里涉及到NAT相关知识。


> - NAT 
网络地址转换，就是替换IP报文头部的地址信息。NAT通常部署在一个组织的网络出口位置，通过将内部网络IP地址替换为出口的IP地址，提供公网可达性和上层协议的链接地址。（[请参考：NAT相关科普](https://www.zhihu.com/question/31332694)）
> - SNAT  
源地址转换即内网地址向外访问时，发起访问的内网ip地址转换为指定的ip地址（可指定具体的服务以及相应的端口或端口范围），这可以使内网中使用保留ip地址的主机访问外部网络，即内网的多部主机可以通过一个有效的公网ip地址访问外部网络。



使用`iptables -t nat -vnL`指令查看宿主机NAT表。

![宿主机iptables表部分截图](https://upload-images.jianshu.io/upload_images/6810620-2a4faa72585b3bb5.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

查看规则：
`2051  125K MASQUERADE  all  --  *      !docker0  172.17.0.0/16        0.0.0.0/0 `
这条规则就关系着Docker容器与外界的通信，含义为将源地址为172.17.0.0/16的数据包（就是docker容器中发出的数据），如果不是从docker0网卡发出时，做SNAT转换，将IP包的源地址替换为相应网卡的地址。
对于外界来说，从docker容器内发出的请求，和宿主机发出的请求相同。

外界想要访问Docker容器的服务呢？
在启动docker容器时，我们使用 `-p`参数指定端口，这时其实是在iptables中添加了规则，如下图所示：


![宿主机iptables表部分截图](https://upload-images.jianshu.io/upload_images/6810620-440166ee3f148b3a.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

DNAT规则，将发送到宿主机的流量转发到真正提供服务的容器IP端口上。

## host模式
Docker容器与宿主机使用相同的网络环境，直接使用宿主机的IP和端口及其他网络设备。这样虽然避免了很多桥接带来的网络问题，但同时也容易造成网络环境的混淆和冲突，比如端口被占用等。不推荐。

## container
指定与某一容器共享网络。

## none
不配置任何网络。
### --link
docker容器之间还可以通过`--link`阐述进行通信，当提供服务的容器只希望个别容器能够访问时，我们可以使用该指令，提供更为高效、安全的连接方式。

# 小结
对Linux虚拟网络基础知识的简单学习后，有助于理清楚下一步排查问题思路。
下一篇博客将介绍目前遇到问题时的排查思路和解决方案，并列举一些常用工具。