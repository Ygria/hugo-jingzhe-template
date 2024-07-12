驱动：Hugo https://gohugo.io/

模板来源： https://github.com/koobai/blog

原作者主页：https://koobai.com/

在此基础上做了一些小改动，版权归原作者所有。
# 第1步：Fork项目

![image.png](https://images.ygria.site/2024/07/7fae3fb5a16ce01deef59999da4d98dd.png)

点击右上角Fork。

# 第2步：修改配置（必做）

## 1.修改Github Action变量

### 豆瓣标记同步

####  获取Douban用户名

获取你的豆瓣用户名，不知道用户名是啥，可以打开豆瓣网页版，切到个人主页

![image.png](https://images.ygria.site/2024/07/62b415d178188d48d9501b8373ade2a6.png)
#### 在Github的Secrets中添加变量

打开你fork的工程，依次点击Settings->Secrets and variables->New repository secret

![image.png](https://images.ygria.site/2024/07/9136ab4bd662783077bd41097524451b.png)

修改为你的豆瓣账号即可。

## 2. 配置修改

1. 打开根目录下的Hugo博客配置文件
2. 修改baseURL为你部署博客的地址（注意等号后的空格。）


![image.png](https://images.ygria.site/2024/07/c6cd8a07e87af32c9f0b120e89418d41.png)


# 第3步：静态托管

以CloudFlare托管为例：

1.登录CloudFlare控制台 https://dash.cloudflare.com/
![413216eba6f5cd931980cb9c73b0a88.png](https://images.ygria.site/2024/07/19291b290d12ac06aa7c7f4d9ca9c75a.png)

2. 在Workers & Pages 页签下，创建一个Page
![image.png](https://images.ygria.site/2024/07/c32f8f336733c945cfd950d700a0ea15.png)


2. 选择 Connect to Git，并授权Github

![image.png](https://images.ygria.site/2024/07/1bf7574bbf3e2ee39136e376c5bd0210.png)

3.选择Fork的项目，并在Frameworks中选择Hugo，其他均保持默认。


![413216eba6f5cd931980cb9c73b0a88.png](https://images.ygria.site/2024/07/19291b290d12ac06aa7c7f4d9ca9c75a.png)

如此可以完成部署。
