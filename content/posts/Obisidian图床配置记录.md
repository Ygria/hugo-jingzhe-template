---
title: Obisdian图床配置（Markdown格式笔记均适用）
date: 2024-04-17
tags: ["工具"]
slug: obsidian-picbed
image: https://cdn.jsdelivr.net/gh/Ygria/Pictures@main/20240417110652.png
---

  参考： https://blog.mingo99.top/article/picbed/picgo  
  
  
  
## 1.  在github中新建私人仓库，并生成token  
  
新建仓库（记住**仓库名称①**）  
![image.png](https://cdn.jsdelivr.net/gh/Ygria/Pictures@main/20240417110652.png)  
Github 右上角-个人头像-setting  
![image.png](https://cdn.jsdelivr.net/gh/Ygria/Pictures@main/20240417110804.png)  
  
  
  
点击”developer settings “-”Token（classic）“  
  
![image.png](https://cdn.jsdelivr.net/gh/Ygria/Pictures@main/20240417110834.png)  
选择无过期时间，并给repo权限。  
![image.png](https://cdn.jsdelivr.net/gh/Ygria/Pictures@main/20240417111350.png)  
拉到最下，生成token，并复制**token值②**  
  
## 2. 下载Picgo并配置  
 访问项目Github网址，在**下载安装**中找到对应的下载地址，安装系统安装包。  
[GitHub - Molunerfinn/PicGo: :rocket:A simple & beautiful tool for pictures uploading built by vue-cli-electron-builder](https://github.com/Molunerfinn/PicGo?tab=readme-ov-file)  
  
仓库名：github个人账户名 + 仓库名（上一步中的①）  
分支名：仓库中存在的分支名，默认为main  
token：上一步中的②  
  
![image.png](https://cdn.jsdelivr.net/gh/Ygria/Pictures@main/20240417103934.png)  
  
  
  
## 3. Obisidian插件配置 - 下载社区插件 Image auto upload Plugin （社区插件）  
![image.png](https://cdn.jsdelivr.net/gh/Ygria/Pictures@main/20240417104408.png)  
  
下载后无需配置，打开插件。  
## 4.使用  
使用起来很简单，直接向obsidian中粘贴文件，会自动上传到图床，并插入图片链接。