---
title: ChatGPT支持MCP！什么是MCP，怎么用？
date: 2025-03-27
slug: /model-context- protocol
---
今天Sam Altman（OpenAI CEO）宣布ChatGPT即将支持MCP。有趣的是，推特热评是：什么是MCP？为什么现在很多人都在谈论MCP？
![image.png](https://images.ygria.site/2025/03/667032a731114d8a60879c4a1822a2f3.png)

![image.png](https://images.ygria.site/2025/03/e7b193f133e2cebb718178ff761d72a6.png)


> [!abstract] 简述
> MCP，即Model Context Protocol：模型上下文协议，为AI如何查找、连接和使用外部工具制定明确的规则，无论是查询数据库、执行命令等。MCP让信息孤岛有了联结的可能。
> MCP具有动态发现的特性：AI代理自动检测可用的MCP服务和功能，无需硬编码集成，这和Coze、Dify等编排工具相比，更为解耦和便捷。
>


# 从天气查询开始

让我们通过一个实际例子来举例MCP怎么用，和有什么用：

> 当我向大模型提问，合肥天气如何？我明天该穿什么衣服？

![image.png](https://images.ygria.site/2025/03/41830b3b36c677f96f389d88fa3d0e85.png)

可以看到，AI无法直接访问实时天气数据，只能给出操作指导，实际的操作需要人来参与完成。

## 配置MCP Server

最新版本的Cherry Studio （`v1.1.10` ）已支持MCP能力。我们可以配置一个高德地图的MCP Server。

打开`https://mcp.so/server/amap-maps/amap` , 复制右上角框中的url。


![image.png](https://images.ygria.site/2025/03/d82d5f93f54b3749cb3254ffdd6abfb8.png)

可以点击编辑图标，填入自己的高德开放平台的Key。

![image.png](https://images.ygria.site/2025/03/b49ecf57b6d70dc31c31627146be654d.png)




在Cherry Studio 设置-MCP 服务器中添加。

![image.png](https://images.ygria.site/2025/03/a9611e4e7f3f784738a91c650c55da6a.png)


选择SSE，填入url。也可以直接编辑并粘贴进JSON。

![image.png](https://images.ygria.site/2025/03/2ced4b622d6648f33cc9bf4ed62e9d7b.png)



如果能启用成功，则说明MCP服务已成功添加！之后就可以使用了。如果报错，请检查网络，或在mcp.so网页上先测试高德地图的API key是否能正常使用。


## 对话时使用

注意，需要选择带有工具调用功能的模型，带着橙色小扳手的就是。如果模型本身支持，但没有显示，可以点击⚙️编辑模型，设置-更多设置打开。
![image.png](https://images.ygria.site/2025/03/7b6a274a889b9d9c78f439383c2ba9bd.png)



![image.png](https://images.ygria.site/2025/03/58d588e4aafc42bd56a37764444184c2.png)

在对话框下方，点击MCP服务器图标，打开MCP服务。如果没有这个图标，切换带工具🔧功能的模型。


![image.png](https://images.ygria.site/2025/03/9adc33cc3e1c669d31d170d0c7c0017a.png)

## 提问示例

这时再提问，可以看到模型会调用高德地图的借口，查询合肥的天气，并根据天气，给出穿衣建议。

![image.png](https://images.ygria.site/2025/03/1fda5eeaee717f3c8df6ce620668fbd4.png)


有了这样的工具，大模型能做的事情一下就扩展了，我可以让它基于天气，来为我制定更精准、详细的旅行计划。

展开工具调用的详情，可以看到调用函数的返回。

![image.png](https://images.ygria.site/2025/03/92b27d3667b69ffdd6e756ec6b93f7fd.png)


## 有趣的应用

### Fetch

配置fetch MCP，遇到网页，就不用再截图或把内容复制给AI了，直接告诉它链接，它可以自己去试图获取链接的内容。

![image.png](https://images.ygria.site/2025/03/0e9c1ae1b8b4de170c1d44d4df4f0e33.png)

看到有人直接把figma设计稿的公开链接发给AI，AI就可以直接生成对应的前端页面了。又节约了时间～
当然，也会翻车，不少网站有反爬机制。

![image.png](https://images.ygria.site/2025/03/ba3f0777d7b120b064089f7f5186afd0.png)


### PostgreSQL： 超简易ChatToDB

PostgreSQL是一个开源的关系型数据库，它也提供了官方的MCP服务。正好我有一个数据库专门用来存自己的账本，只需要填入连接字符串，就可以直接执行query，让大模型访问我的数据库并做数据分析了！

![image.png](https://images.ygria.site/2025/03/ad4a8c11a73070794abffdeb1dca674a.png)

填入连接串，点击Connect。最好直接在页面上测试一下数据能不能正常拿到。

![image.png](https://images.ygria.site/2025/03/49e345007d32dad5f7bf7855f784a5a9.png)

测试方法：切到Tools，展开query，填入SQL并尝试执行。


![image.png](https://images.ygria.site/2025/03/14c5d4c5ed60f23e02d63757dfe83fc0.png)

现在，我可以和AI讨论，让它生成SQL，并直接执行，基于执行结果给出分析。如果要做数据分析，这节约了非常多的代码量，并能实时动态调整查询条件、查询范围，并直接根据结果输出分析报告、分析图表等。

> [!question] 我遇到的问题
> 但在这里，我遇到了问题，几轮对话后，可能是上下文丢失，工具调用并不能稳定触发，我使用的Gemini2.5开始胡编乱造数据，并在我再三要求之下，也没有再去实际查询数据库。同样的话术、同样的模型，有时候也会不调用工具就直接回答。不知道未来会不会有强制触发工具调用的功能。
> ![image.png](https://images.ygria.site/2025/03/1e43fc52535e34265ee39a46850beb43.png)


### 不仅能读，也能写

以上举例都是读，而MCP不仅能读，也能写！
当前最广为流传的通过MCP调用Blender，就是可以通过自然语言，直接控制Blender 3D建模软件进行建模。



https://www.bilibili.com/video/BV1thQPYfEYC/?spm_id_from=333.337.search-card.all.click&vd_source=5698df189d4600a1af2f2cedad918af1

#  总结

## MCP与编排引擎的区别

没有MCP，LLM只能通过人为指定的方式来访问数据，并且业务一旦变更或拓展，都需要重新编排流程，一百个新功能需要一百个新的流程。

> [!cite] 
> MCP 本身并不是一个“代理框架”，而是充当代理的标准化集成层。MCP 完全是关于操作部分，具体来说，它为代理提供了一种标准化的方式来执行涉及外部数据或工具的操作。它提供了以安全、结构化的方式将 AI 代理连接到外部世界的管道。如果没有 MCP（或类似的东西），每次代理需要在现实世界中执行某项操作时（无论是获取文件、查询数据库还是调用 API），开发人员都必须连接自定义集成或使用临时解决方案。这就像建造一个机器人，但必须定制每根手指来抓取不同的物体，这既繁琐又不可扩展。ref：[[https://huggingface.co/blog/Kseniase/mcp#so-what-is-mcp-and-how-does-it-work]]

而有了MCP，相当于LLM有了多个访问外部的工具箱，大模型自己决定需要使用什么工具，而且完全是解耦的：可以任意更换需要使用的大模型，也可以不停迭代可以提供给大模型的工具箱。

除了软件层的数据接口，MCP还能与物联网设备、传感器、操作系统功能进行交互，也许未来人人都是钢铁侠，每个人都可以拥有一个贴心的AI管家，全方面地照顾人的起居和生活。

## MCP存在的疑问

目前看来，MCP是大势所趋，越来越多的软件宣布支持，社区热度也越来越高，也许这就是AI落地应用的最终答案。

当然，MCP目前存在不稳定、可能有数据泄露隐患等风险。这也是未来我们需要面对的挑战。

可以使用Cloudflare提供的框架（注意必须是付费用户），封装并发布自己的MCP服务。我相信应该会有更多的框架出来，所有想拥抱AI的方向都存在着巨大的应用前景。

## 我的展望

MCP有可能颠覆当前的客户端-服务端架构，未来也许前端（也就是客户端）只需要做自然语言的输入（也许加上多模态，比如语音输入等），后端只需要封装符合MCP的原子能力，二者通过大模型来作为中介。

想象一下，以后各类设计、工程软件都支持了MCP，以后修图、剪辑、编曲、建模、做实验都不再需要动手，而只需要动动嘴皮子，向AI表达意图，所有需要动手的工作都可以交给大模型和机器人来进行……

未来世界的工作模式将会是什么样呢？非常期待！
