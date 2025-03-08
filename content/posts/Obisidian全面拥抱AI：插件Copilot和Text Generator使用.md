---
title: Obisidian全面拥抱AI：插件Copilot和Text Generator使用
date: 2025-03-08
slug: /obisidian-copilot-and-text-generator
tags:
  - obisidian
---

>[!abstract]
>全面AI浪潮来了！你的Obisidian仓库还没有接入AI吗？推荐两个插件，轻松让你的笔记库全面接入大模型（Deepseek、ChatGPT、Gemini……你原先用什么，就可以接入什么），把自己本地的文件库变成个人知识库，让AI帮你生成笔记的一句话摘要，还有更多玩法等待探索～


#  Copilot

当需要根据特定垂类内容进行深度分析时，经常会用到知识库，与单纯使用 AI 相比，使用自己选择的内容和材料，有如下好处：

  1. 使用自己的知识库，可以让内容更符合个人认知，也能使用过程中的反馈帮助梳理自己的内容。
  2. 更贴合个人场景，更加垂直


Obisidian 插件 Copilot ，可以直接基于你本地的内容仓库生成知识库，然后直接基于整个内容仓库（Vault）或者单文件做问答交互。

## 1 . Obisidian 安装 Copilot 插件

设置-第三方插件（需先关闭安全模式）。

![image.png](https://images.ygria.site/2025/02/8eb0c94e5df230cbd22d762918f4ce7f.png)

## 2. 配置模型

在设置-Model 中配置使用的模型（需要两个模型：Chat Models （对话模型）和 Embedding Models


![image.png](https://images.ygria.site/2025/03/a058836d4b1a65c17b77d51d4c3278cf.png)


-  在火山引擎/硅基流动/谷歌 AI Studio……等 AI 开放平台，配置推理节点，或使用免费开放的大模型，获取 API 地址和 Key
-  配置两个模型（==往下滚动配置 Embedding 模型，注意不要配错位置了！==）
- 配置时可以点击 `verify` 验证配置的地址是否有效
Chat Model
![image.png](https://images.ygria.site/2025/03/0c1e7c193b12f8b1c83341d97c61200d.png)

如果使用的模型在默认列表中，直接填上 key 就可以了。否则可以添加使用 OpenAI Format 协议的任意自定义模型。

Embedding Models：我使用的是 BAAI/bge-m3

![image.png](https://images.ygria.site/2025/03/f38385d448fd19545357a32fc6f77ef0.png)
-  在 Basic-general 中配置使用的模型
![image.png](https://images.ygria.site/2025/03/72cb7cb9b2287b7e0b05ac6e8890c2a6.png)
> [!example]
> 如果你使用了第三方模型接入平台，也可以配置到 Copilot 里。下面给出硅基流动和火山引擎的配置方法。
### 配置硅基流动中的模型

**第一步**：登入硅基流动

https://cloud.siliconflow.cn/models

模型广场-搜索模型名称



![image.png](https://images.ygria.site/2025/03/535e1f61f05c742ff397944d3526f446.png)

**第二步**：点击卡片，展开详情，点击复制按钮复制模型名称

![image.png](https://images.ygria.site/2025/03/b012152e6fa9e6f42e68eb7c7a699afd.png)



**第三步**：配置 API 调用的密钥

![image.png](https://images.ygria.site/2025/03/a3c06375922328c5f522ac188a4d8c55.png)

如果已有密钥，直接复制。没有的话点击新建密钥。

**第四步**：在 Copilot 插件的设置中配置

按如下图填写并配置。Model Name 就是第二步中复制的。Display Name 可以自己填，后续在其它选项中可以选择。 Provider 选 OpenAI Format，Base Url 请求基础地址： `https://api.siliconflow.cn/v1` ，API Key 是第三步中生成的。填写完成后，点击“Verify”，右上角弹出 Model Verify Successfu 表明验证成功。

![image.png](https://images.ygria.site/2025/03/acd27e8404bfabe594c307ba4cf932b5.png)

### 配置火山引擎

> [!tip]
> 火山引擎速度很快，而且提供了免费额度。

**第一步**：登入火山引擎-火山方舟

https://console.volcengine.com/ark/

**第二步**： 按照如图顺序，创建在线推理节点

【在线推理】- 【自定义推理接入点】-【创建推理接入点】

![image.png](https://images.ygria.site/2025/03/07600a661f832b8b0e9bc325f3fc6ac8.png)


**第三步**： 选择模型，点击确认接入

![image.png](https://images.ygria.site/2025/03/192514369ae8764ecbf520dc9ea25ecc.png)



**第四步**： 点击选择 API Key，创建或选择，并复制 API Key 的值


![image.png](https://images.ygria.site/2025/03/f86adf068d9f485f8d54bde5b67a16bc.png)


**第五步**：在 Obsidian Copilot 插件中配置

注意：Model Name 填写的是 `ep-` 开头，BASE URL 填写 `https://ark.cn-beijing.volces.com/api/v3/chat/completions` 。其余配置步骤与硅基流动相同。

![image.png](https://images.ygria.site/2025/03/49462ee68d9b4fea475670f4af665d47.png)

## 3. 使用

点击左侧的图标开始使用

![image.png](https://images.ygria.site/2025/03/4e143503bc6e9c654c344cf2b91032d0.png)

可以切换到 vault QA ，与全库对话

![image.png](https://images.ygria.site/2025/03/91055245f15e637cb1bf784425fff2d1.png)



![image.png](https://images.ygria.site/2025/03/db51478199c500ed584f519bd4ac59eb.png)

![image.png](https://images.ygria.site/2025/03/ed1835afceb5ccf459e3d52f9c924124.png)

回答时，是根据本库内的文件内容，整合出了一份说明。可以根据这些说明去增补关联链接、合理化文件结构，或者用它来更好地检索材料，完成观点提炼和内容输出。

AI 提供了另一个视角去查看自己写下或收藏的内容，也能帮助个人思考的系统化、结构化！

#  Text Generator


> [!abstract]
> 想要为我的文章快速生成简介、关键词，好用来 SEO 或填写文章简介。**Obsidian Text Generator 插件**（推荐 ✅，支持 OpenAI 兼容 API）。

## **步骤 1：安装 Obsidian Text Generator 插件**

1. 在 Obsidian **Settings > Community Plugins** 里搜索 `Obsidian Text Generator`，安装。
2.  （如需使用 Deepseek）进入 **Settings > Text Generator > API Settings**，选择 **Use OpenAI Compatible API**。 填入 API 地址和 Key
3. 或者直接选择内置的模型，并填写 API key

## **步骤 2：使用**

点击图标生成文本。

![image.png](https://images.ygria.site/2025/03/48d494ab291a17e6004468d83b2e0f43.png)


### 自定义提示词

可在配置 `Custom Instruction` 中写自定义提示词，比如我给的提示词就是“一句话总结笔记”。AI 在概括信息方面表现优越。

![image.png](https://images.ygria.site/2025/03/4e4f5a1b51364fb1f0529bf89be3b07e.png)

## 效果演示

小手一点，立刻生成了当前笔记的摘要。

![演示效果.gif](https://images.ygria.site/2025/03/4ff1efda7aacd8a3d810fa67cc7a691a.gif)



也支持配置兼容OpenAI协议的接口哟～注意，硅基流动的路径要配置成`https://api.siliconflow.cn/v1/chat/completions` 

推荐大家用Gemini，速度很快。但对网络环境要求较高。

还有什么玩法，欢迎大家分享～
