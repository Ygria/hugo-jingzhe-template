---
title: 建站小记：迁移域名DNS到CloudFlare
date: 2024-06-30
tags: ['建站','工具']
description: 'CloudFlare使用和建站配置'
icon: 🏗️
---

CloudFlare一直有赛博菩萨之称，据说用它做DNS解析服务又快又好又免费，还能防DDOS攻击，并且可以提供页面访问统计功能。
正好我博客网页打开略卡顿，所以决定将自己的DNS解析迁移到CloudFlare。


# 1.登录CF控制台，添加自己的域名
![image.png](https://cdn.jsdelivr.net/gh/Ygria/Pictures@main/20240630232345.png)


如上图所示，这里的截图是我已经配置好了的。
# 2. 登录原域名服务商账号，并添加CF DNS解析服务

一般来说，在哪里买的域名，就会用哪个服务商提供的DNS解析服务。
我的域名是从西部数据购买的。登录该网站，并进入域名管理。
将DNS解析改为自定义解析，并输入CF提供的两个解析服务器。
![image.png](https://cdn.jsdelivr.net/gh/Ygria/Pictures@main/20240630233346.png)
注意如果有DNSSEC设置，需要关闭。
配置完成后保存即可。

# 3. 解决重定向问题
保存DNS配置后，等待2-24H DNS刷新。
如出现网页访问反复重定向问题，需要到SSL/TLS标签下，将模式选为Strict即可解决。

![image.png](https://cdn.jsdelivr.net/gh/Ygria/Pictures@main/20240630233944.png)

# 4. 完成
现在可以到CF的控制台看到博客的访问情况啦，是不是很不错呢～
![image.png](https://cdn.jsdelivr.net/gh/Ygria/Pictures@main/20240630234128.png)
