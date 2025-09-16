---
title: obsidian发布数字花园：沉淀个人知识库
date: 2024-08-23
slug: obsidian-digital-garden
tags:
  - obsidian
image: https://images.ygria.site/2024/08/93b7b55b36fff0a7bd1f6b72e7286469.png
icon: 🏡
---


# “卡片盒”和双链笔记，及我所实践的知识库工作流

## 1.卡片盒和第二大脑


起因是看到这篇文章：[# 把信息交给未来的自己——构建你的第二大脑 ](https://www.mrhuangtalk.com/posts/BulidYourSecondBrian/)，文章的开头就切中了我的痛点：


> 你有没有经历过：读了一本书，投入数小时的脑力劳动来理解它所呈现的想法。 读完这本书时，你会感觉自己获得了宝贵的知识体系。但是然后呢？你可能会尝试应用本书推荐的基于科学的方法，却发现它并不像你想象的那么清晰。 你可能会尝试改变饮食、锻炼、交流或工作的方式，相信习惯的力量。但随后生活的日常需求又回来了，你忘记了最初是什么激励你。
> - 之后你可能放弃了，将所有书籍都贴上浪费时间的标签。
> - 也有可能你认为这只是没能记住阅读的所有内容的问题，之后就致力于研究各类花哨的记忆技术。
> - 你还有可能变成了「信息狂」，强迫自己喂饱无数的书籍、文章和课程，希望能坚持下去。
> 
> 其实你之前做的很好，这些方法都非常有用，也非常重要，造成这些结果的原因，仅仅是你**没有在正好需要的时候读到。**

> 你现在正在阅读时间管理技巧，但它们可能只会在两年后有用。你现在正在和一个潜在客户谈论他的目标和挑战，但你真正可以使用这些信息的时间是明年他竞标一份新的巨额合同时。现在对学习知识的挑战不是获取它，在我们的数字世界中，你可以随时获取几乎任何知识。

> 
> 现在**真正的挑战在于确认哪些知识值得获取，然后构建一个系统，通过时间将它们推送到未来最适用、最需要的时候。** 在那时，你可以把这些知识直接应用于面临的困难和挑战。在那时，你不用再担心怎么去保存、记住、理解这些知识，你只需要直接应用它们，当你用它们解决一个真正的问题时，书本知识已经变成了经验知识。经验知识是你永远随身携带的东西。
> 所以，**我们需要一个外部的、集成的数字存储库，用于存储你所学的东西，以及它们来自哪里。它是一个存储和检索系统，将知识点打包成离散的数据包，这些离散的数据包可以在未来任意时间点供我们使用。**
> 
> - 这个储存和检索系统就是**第二大脑**，一套便捷高效的**笔记系统**。

我每天沉溺在过量的信息流中，阅读、观影、听播客、刷短视频，但似乎并没有留下些什么。知识引起我片刻的惊喜和瞩目，紧接着就被我抛到脑后，再次遇到也只是最熟悉的陌生人。

将知识拆解、碎片化，将它们按照自己的审美和习惯，整理成一套电子、可多设备同步、可存储、可检索的系统——知识库的模型并不总是树形结构，而更贴近网状。

**卡片盒笔记法** https://zettelkasten.de/introduction/zh/：

> - **卡片盒笔记系统**：英文/德语 Zettelkasten，将笔记相互连接形成一个网状结构的超文本笔记系统，它是一个工具，是你的伙伴。
> - **卡片盒笔记法**：英文 Zettelkasten Method，建立卢曼笔记系统用到的的一些具体方法
> - **笔记卡片**：英文/德语 Zettel，原指一张用来记录笔记的小纸片，现指使用卢曼笔记法记录的一条单独的笔记
> - **想法**：英文 Thought，卢曼笔记法要求**每条笔记只记录一个 thought**，thought 在中文中含义非常丰富，可以是一个术语、概念、理论、看法、点子，突然的灵感等等，这些在本文中统称为“想法”
> - **思想之网**：英文 Web of Thought，由各种想法互相连接形成的网络，卢曼笔记系统就是一张思想之网
> - **链接**：英文 Link，名词，指代每条笔记的 ID
> - **连接**：英文 Link/Connect，动词，指将一条笔记与另一条笔记连接起来的动作/操作
> 

## 2.我的实践

我决定立刻按照这篇文章给出的方法进行实践。在信息流的规整中，我使用了[马林康大佬](https://github.com/malinkang)提供的项目Podcast2Notion、Weread2Notion等，这些项目将会自动将我微信阅读记录及划线内容、播客收听及转写出的文本内容同步到我的Notion中：


![image.png](https://images.ygria.site/2024/08/7d50360f948f4415a13b504d1155282b.png)


其他网页收藏内容，通过Save2Notion浏览器插件向Notion同步。


这里将留存大量我待整理的内容。

obsidian就是能做网状笔记的最佳利器，它打开速度极快，开源、免费、完全本地，可以通过丰富的插件拓展功能。
我采用Github作为同步方案：天生就适合文本同步的方法，也能追踪到之前编辑的版本。


我会将这些笔记逐步整理到我的obsidian知识库的Note文件夹，尽可能保留原文和原始链接，再在Summary文件夹下写下自己的感悟，两者通过双链进行关联。

我得承认这是一项非常考验耐心的工作，可能一开始做出的笔记很拙劣、并没什么创见、甚至有错误，也没有做到拆分粒度足够细、逻辑关联正确。但每次做一点，也许有一天能够构成我的思想之网。

例图：我为《情绪》一书做的笔记。

![image.png](https://images.ygria.site/2024/08/61e9e52ee78fbac72133aacdbad0ddd3.png)


# Digital Garden发布我的数字花园

[数字花园地址：Ygria‘s Digital Garden](https://digital-garden.ygria.site/) 

效果预览：

![image.png](https://images.ygria.site/2024/08/93b7b55b36fff0a7bd1f6b72e7286469.png)



## 1. 安装Digital Garden插件

点击obsidian左下角设置⚙️，在设置页面打开Community Plugin，搜索Digital Garden插件安装并启用。


![image.png](https://images.ygria.site/2024/08/9ea0392b10c848a2dfe247f8137e26d2.png)

## 2. 配置和发布

### 准备Github仓库（公有和私有均可）
 
 
 在github中新建私人仓库，并生成token  

新建仓库（记住**仓库名称①**）  
![image.png](https://cdn.jsdelivr.net/gh/Ygria/Pictures@main/20240417110652.png)  
Github 右上角-个人头像-setting  
![image.png](https://cdn.jsdelivr.net/gh/Ygria/Pictures@main/20240417110804.png)  
  
  
  
点击”developer settings “-”Token（classic）“  
  
![image.png](https://cdn.jsdelivr.net/gh/Ygria/Pictures@main/20240417110834.png)  
选择无过期时间，并给repo权限。  
![image.png](https://cdn.jsdelivr.net/gh/Ygria/Pictures@main/20240417111350.png)  
拉到最下，生成token，并复制**token值②**  

将①和②的值填写到插件配置中。

![image.png](https://images.ygria.site/2024/08/1f883e3f68d5e92bc4b21b6b143f0511.png)


### Default Note Setting

参考文档，可以全部打开。
 

![image.png](https://images.ygria.site/2024/08/84f010d04274cbec4b804bf8071e679f.png)

### **样式主题设置**

可以选取社区中的主题

![image.png](https://images.ygria.site/2024/08/58e080cd91e8fe7dcaa766021bfde81f.png)


### 首页和其他页面

编写想要设置为首页的Markdown文件，在Front Matter中加入dg-home:true和dg-publish:true。
其他配置需要发布的页面配置dg-publish:true和dg-path，注意dg-path不能重复，否则构建会报错。

**发布首页：**

![image.png](https://images.ygria.site/2024/08/2b10398cbd66ce549508fce98f49fab5.png)

**发布页面：**

![image.png](https://images.ygria.site/2024/08/59e0c75781f1e79ec6b334d72b1c78f7.png)

点击Digital Garden插件提供的导航按钮，可以进行可视化的发布

![image.png](https://images.ygria.site/2024/08/87f0a7f54c7fe80b63f7603a2bd3b26c.png)


发布之后，已将内容同步到创建好的Github仓库，配置Vercel和Cloudflare Pages构建均可。我使用的是Cloudflare  Pages构建。

### 构建发布

在Cloudflare Dashboard新建一个Page，并配置Github仓库和构建指令即可。
![image.png](https://images.ygria.site/2024/08/eb5e3376817eb5e2e5ab51dc8acf61db.png)


#### 建议关闭自动构建

由于每次单文件的修改都会产生一次Commit，建议取消自动构建，使用Webhook触发构建。

![image.png](https://images.ygria.site/2024/08/87ad636c47e7ab48735975a4dc8d586b.png)

#### 使用Webhook触发构建

![image.png](https://images.ygria.site/2024/08/fbb41a2f6eecbcb9aab820750d522047.png)

可以本地通过curl或postman等客户端软件触发，也可以将webhook配置到其他工作流中。

至此完成数字花园的发布。

## 3. 样式自定义

可以将上文中所说的Github仓库Clone到本地进行样式调试和开发。使用`npm run start` 指令启动项目。
将自定义样式放`src/site/styles/user/custom-style.scss`中。

我因为本机网络环境问题，拉不到Github上的主题文件，将配置中THEME的地址改成可访问到的CDN地址即可。

![image.png](https://images.ygria.site/2024/08/f6903c2a84035767e5b7a7411f414347.png)


