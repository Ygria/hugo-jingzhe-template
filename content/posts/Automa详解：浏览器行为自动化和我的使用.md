---
title: Automa详解：浏览器行为自动化和我的使用
date: 2025-01-05
slug: /use-automa
---
> [!abstract] 简述
> 一个可以录制、自定义浏览器行为、通过可视化工具定义Workflow的浏览器插件。可以理解成浏览器的RPA机器人，也有点像直接对浏览器上的行为进行编程，可以**打开Tab、切换Tab、输入/抓取文本、点击按钮、批量下载、批量操作等等。**
> 吸引我的点： UI优美*（一看就是有UI和UX打磨过的），功能强大，使用看上去很简便。**对于流程（Workflow）、“块”（Block）、“线”（Line）的概念定义也值得学习，条件区块中的‘AND’和‘OR’设计也值得拆解**
> 
> 我用它做了一个把自己小红书无人点赞的笔记批量隐藏掉的功能。（官方没有提供，搜索了一下感觉有类似需求的人还蛮多的，之后还可以拓展条件为阅读量低的等等。）
> 除此之外，还做了一个复制微信读书Cookie到Github Action变量的功能。我使用的Weread2Notion项目会使用Github Action跑脚本，每天把我的阅读记录同步到Notion中，但有时候Cookie会失效。手动更新麻烦而且容易出错。使用Automa可以轻松地自动化这一系列操作。
> 用它还可以执行更多、更复杂的RPA功能，值得探索～
> 

使用的感受是**非常强悍**，设计好流程，完全可以使用自动化的工作流来代替琐碎、重复、**跨越多个网站**的工作。一切可重复性的操作交给机器来执行，既节约时间，又减少出错。看到不少人已经将它运用到运营工作中了。
# 如何开始

## 前往Automa官网，下载并安装

https://www.automa.site/

![image.png](https://images.ygria.site/2025/01/19edc312c4de99e823d1c2ed5d6cef6a.png)


### 打开插件（可能因为安全策略，浏览器会自动关闭它。记得打开）

![image.png](https://images.ygria.site/2025/01/348157b49894ec7825e41f1ea0858df9.png)


### 从右上角点击插件图标，开始使用

![image.png](https://images.ygria.site/2025/01/e874028fa8fb5ef35f0adf9f83e3e0f3.png)


值得注意的是原本的录制⏺️按钮无法再直接从插件弹窗中快速触发了，得从Dashboard中触发。

点击🏠图标，进入Dashboard，可以进行Workflow的编排。也可以直接使用Marketplace中别人已经编排好的流程。


## 基础概念学习

每一个自动化行为是一个Workflow（工作流）。工作流由**块（Block）**和线（Line）构成。


> [!quote] Automa 中有六类块
> - **General**: Perform a general action in the workflow, like making an HTTP request or executing another workflow.  
>     **常规**：在工作流中执行常规操作，例如发出 HTTP 请求或执行另一个工作流。
> - **Browser**: To control the browser.  
>     **浏览器**：控制浏览器。
> - **Web Interaction**: To interact with the active tab of the workflow. Before using blocks in this category, you need to use a [New Tab](https://docs.automa.site/blocks/new-tab.html) or [Active Tab](https://docs.automa.site/blocks/active-tab.html) block.  
>     **Web 交互**：与工作流程的活动选项卡进行交互。在使用此类别中的块之前，您需要使用[新选项卡](https://docs.automa.site/blocks/new-tab.html)或[活动选项卡](https://docs.automa.site/blocks/active-tab.html)块。
> - **Control Flow**: Add logic to the workflow.  
>     **控制流程**：向工作流程添加逻辑。
> - **Online Services**: Services that integrate with Automa.  
>     **在线服务**：与 Automa 集成的服务。
> - **Data**: Modify or manipulate workflow variables or tables.  
>     **数据**：修改或操作工作流程变量或表格。


支持的配置项：
1⃣️ 执行的操作
2⃣️错误处理 

> [!quote] 块执行支持如下错误处理：
>
> -  **1. Enable**: Enable the error handler for the block  
>     **Enable** ：启用块的错误处理程序
> - **2. Retry action**: retry the block execution if an error occurs on the block  
>     **重试操作**：如果块上发生错误，则重试块执行
> - **3. Throw error**: if selected, the block will throw an error  
>     **抛出错误**：如果选择，该块将抛出错误
> - **4. Continue flow**: if selected, the workflow execution will continue  
>     **继续流程**：如果选择，工作流程将继续执行
> - **5. Execute fallback**: if selected, the workflow will continue to the block that connects to the fallback output  
>     **执行回退**：如果选择，工作流程将继续到连接到回退输出的块
> - **6.Insert data**: insert data into the [table](https://docs.automa.site/workflow/table.html) or [variable](https://docs.automa.site/workflow/variables.html)   (个人理解： 为人工操作或者后续其他操作留下空间)
>     **插入数据**：将数据插入[表](https://docs.automa.site/workflow/table.html)或[变量](https://docs.automa.site/workflow/variables.html)中

> [!quote] 块之间通过Line来连接。
>  可以进行线的连接、删除、自定义外观等。
  

> [!note] 我认为有趣的特性
> 
> 1. Trigger - ContextMenu -  selectionText
> 将Trigger配置为Context Menu类型，并支持将选中的文本作为变量，触发工作流。
> 2. 后台运行
> 将“set active tab”取消，让其在后台运行
> 
> 3. **节点支持写JavaScript代码！**
> 通过内置 automa 函数，读取网页内容、读写变量
> 
> 4. **条件与循环、各种条件对应的路径定义**
> 
> 5. 可以读取CSS元素的Attribute Value
> 

##  看视频，学基础操作和应用场景（官方示例）

https://www.automa.site/tutorials

官方给出的4个教程视频挺不错的，加起来不到一个小时，强烈推荐观看。下面是我总结的示例场景。


> [!example] 右键选择内容，翻译并从页面alert
> 1⃣️触发器 Trigger 设置成Context Menu，支持将选中的文本作为变量输入到后续块中
> 2⃣️ New Tab 打开谷歌翻译页面
> 3⃣️ Form 块，输入内容，等待，获取结果
> 4⃣️ Javascript 块，alert结果

有了“沉浸式翻译”插件，翻译选中内容不再是刚需，但举一反三，我们完全可以做到：选中内容-发送给AI-获取结果-回显到网页上，或者发送摘录的内容到自己的笔记中。


> [!example] 谷歌搜索小猫咪，并逐个保存查询到的元素
> 1⃣️打开谷歌图像搜索页面
> 2⃣️ Form - 文本域输入，Press Key -  Search
> 3⃣️ Loop  - 根据CSS 选择元素来Loop （注意：条件区块的其他块，也应该连接到**Loop Break点中！）**
> 4⃣️通过“下载”区块，下载图片。

快速出爬虫，这比Python代码还要简单不少，唯一要考虑的可能是别被反爬机制反制了。

> [!example] 做一个WhatsUp 聊天机器人Bot
> 1⃣️打开聊天页面
> 2⃣️ Loop 聊天窗口
> 3⃣️  根据CSS属性做Condition，如果最后一条信息是hello，则进行回复“Hello Again”
> 4⃣️ Trigger 是定时触发，并使用fixed Delay

> [!example] 读取谷歌Sheet中的内容，批量发送邮件
> 1⃣️将Google Sheet的权限分享给Automa账号
> 2⃣️ Loop Google Sheet数据（可以Preview）
> 3⃣️ 打开邮件页面，Form 块 - 填写收件人、内容、发件人信息，并点击发送。

很适合运用到运营等工作领域中。由于工作流中支持接入HTTP请求和自定义的数据源，我们可以结合AIGC，做批量生成内容后的批量发布、批量运营。唯一风险点就是可能会被平台风控（很多时候不出批量功能不是不能，而是不想）。


# 我的工作流

## 1.批量隐藏小红书笔记

地址： https://automa.site/workflow/POI-3SORQwrGRdFXIHsGt

![image.png](https://images.ygria.site/2025/01/9af89736f10cbb9d1a713efdf8186027.png)


### 思路讲解

1. 打开小红书笔记管理页面

![image.png](https://images.ygria.site/2025/01/15dc405436aa64dbc0ebf16a04aadf35.png)

2. 遍历元素，将上限设置得比较高，并设置Load More Elements（重要！页面默认懒加载，只加载前10条）

![image.png](https://images.ygria.site/2025/01/32d5164e56498c8c3d87a81836807201.png)


3. 获取笔记的“喜欢”数据（通过CSS选择器读取）

使用Automa提供的元素选择器进行拾取。值得注意的是，要将拾取到的路径中的父元素路径替换成 {{ loopData.notes }} ，这样每次读取的都是当前循环到的这条笔记的“喜欢”数量。同理也能拿到阅读量、评论、收藏、分享数据。


![image.png](https://images.ygria.site/2025/01/9d5afebe1d1556bfe3d7084fec625a6a.png)


![image.png](https://images.ygria.site/2025/01/9f98a9e8da98bf496b7bf08dc67bfccd.png)
4. 根据自定条件判断

这里的交互设计很优秀。我们可以看到它的AND 和OR条件是如何设计的：

![image.png](https://images.ygria.site/2025/01/2e694bb786efd9fbcee704c4b459507e.png)

我这里只设置了一个条件，就是——没有人点赞。（可以自己调整）

![image.png](https://images.ygria.site/2025/01/66b4683c8f85c31c5aae4f3f81d28a58.png)
条件块支持多个Path，可以理解成不是if else而是switch case。注意在循环内，每个path都应该链接到循环断点。


5.  符合条件的编辑权限成“仅自己可见”
![image.png](https://images.ygria.site/2025/01/2a9ad99594e1f88e3b3d41b0dac5c426.png)

没什么好说的，都是使用录制功能完成的。

6. 下拉，强制列表刷新（不然读不到元素！）
每次遍历后都强制滚动页面，让页面元素加载

![image.png](https://images.ygria.site/2025/01/bdb94428acbff2890ad519d4e2d152e6.png)

递增是勾上的，不然是每次都滚动到同个位置。

7. 循环结束

亲测可用～

## 2. 复制微信读书Cookie到Github Action变量

地址： https://automa.site/workflow/-runB5_moAYmllnUe_7Vr

![image.png](https://images.ygria.site/2025/01/c91b7af1c037df803f6fe0186d3531f9.png)


这个工作流相对来说更简单，唯一值得说的可能是需要配置一个全局数据，这样可以让别人也能用。

![image.png](https://images.ygria.site/2025/01/58f5e7293bd08e4cf35d74bc2a98a648.png)


1. 打开微信读书（需要是登录好的）
2. Javascript代码块，读取Cookie，并放到变量里去

![image.png](https://images.ygria.site/2025/01/f1d74749c442f5d0f355cde9f97bf3cd.png)

3. 打开Github Action Variable配置页面

地址形如：

https://github.com/{{globalData.githubName}}/weread2notion-pro/settings/secrets/actions/WEREAD_COOKIE

这里就是globalData的作用了。

![image.png](https://images.ygria.site/2025/01/260a581857271926a80ad6619d0f34fc.png)


页面是这样的

4. 使用Form 填写变量值

![image.png](https://images.ygria.site/2025/01/2eb04466055482eb62ad5f10c4a3a93c.png)


6. 点击提交

我的工作流做到这里就停了，接下来会让你填写密码确认。当然可以也把密码填写一并做进去，看个人的偏好了～


# 总结

Automa的设计思路和交互都很棒！虽然可能出于安全的考虑（这玩意让爬虫又好写了很多），有被封禁的风险，但它带来的效率提升的前景是毋庸置疑的。

自动化一向让我痴迷。一切可以抽象出来的操作，最后都可以交给自动化来执行～只要花一次配置的时间，就可以一直使用，并且减少出错的可能，何乐而不为呢？
