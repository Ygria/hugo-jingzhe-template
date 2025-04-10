---
title: 0成本，使用Github Action做一个外语PDF翻译工作流
date: 2025-04-10
slug: /pdf-translate
---
> [!abstract]
> 看纯英文PDF太费劲，不想用别人的网站或插件，机翻质量差、速度慢、容易卡死，用浏览器插件大PDF容易失败。
不如自己手搓一个工作流来做翻译，只需要往文件夹里一丢，提交到Github仓库，Action工作流会自动触发，自动翻译，翻完了也是自动上传到Github 仓库里。

>效果预览：出来的结果是一个双语，一个纯汉语，可以打开双语的对照着看，阅读速度大大提升，翻译得有瑕疵也可以看原文澄清歧义。下图是翻译了谷歌新出的提示词工程白皮书

![image.png](https://images.ygria.site/2025/04/7daf0284d1c6aebb66930b8cdfbf4dbc.png)

## PDFMathTranslate

`python` 语言的 `pdf2zh`库，支持多种语种，翻译的同时会保持原有的段落格式，支持传入文件夹，支持多种大语言模型接入。默认的机器翻译的质量很差，必须接入大模型翻译或专有翻译服务。

> [!question] 默认谷歌的翻译，把“摘要”翻译成了“抽象的”，翻译质量较差
> 
![image.png](https://images.ygria.site/2025/04/2d52dcffe74ef9c5b5e18bc7694c8ac0.png)

[PDFMathTranslate](https://github.com/Byaidu/PDFMathTranslate)

[PDFMathTranslate 支持的Service](https://github.com/Byaidu/PDFMathTranslate/blob/main/docs/ADVANCED.md#services)

支持的服务如下表

![image.png](https://images.ygria.site/2025/04/b35c509b217c586d8024132802593a6c.png)
![image.png](https://images.ygria.site/2025/04/e8c99565a11f5340981a9055eb1d3fc2.png)

可以看到，支持了非常多的AI模型和AI开放平台。我试了DeepL、Gemini、Qwen/Qwen2.5-7B-Instruct和Deepseek V3，感觉DeepSeek V3表现较好。

使用方法是通过`-s`指定服务，并将参数的`Value`写入到环境变量中。以OPEN_AI举例，Windows环境下用`$env:OPENAI_API_KEY=`指定，Mac环境用`export OPENAI_API_KEY=`指定，同时支持传入自定义的提示词等。

> [!hint]
> 如果有其他语种的翻译输入/输出需求，也可以通过-li和-lo指定，但需要使用的翻译服务能够支持。


## 搭建工作流

新建Github项目，在`.github/workflows`文件夹下新建`.yaml`文件，写入如下配置内容即可。

```yaml
name: Translate PDF with Python
on:
  push:
    paths:
      - 'papers/*.pdf'
  workflow_dispatch:
jobs:
  convert:
    runs-on: ubuntu-latest
    env:
      SILICON_API_KEY: ${{ secrets.SILICON_API_KEY }}
      SILICON_MODEL: ${{ secrets.SILICON_MODEL }}
    steps:
      - name: Checkout Repository
        uses: actions/checkout@v3
      - name: Set up Python 3.12
        uses: actions/setup-python@v5
        with:
          python-version: 3.12
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install pdf2zh
      - name: Translate all PDFs in papers/
        run: |
          mkdir -p translation_output archive
          pdf2zh --dir papers/ -o translation_output -s silicon
          mv papers/*.pdf archive/
      - name: Commit and Push Translated Files + Archived PDFs
        run: |
          git config --global user.name "github-actions[bot]"
          git config --global user.email "github-actions[bot]@users.noreply.github.com"

          git add translation_output/*.pdf archive/*.pdf
          
          # Stash changes to ensure no conflict when pulling
          git stash || echo "No local changes to stash"

          git commit -m "Auto translate PDF and archive originals" || echo "No changes to commit"

          # Pull with rebase to avoid conflicts
          git pull origin main --rebase || exit 1

          # Apply the stashed changes and commit them
          git stash pop || echo "No changes to apply from stash"

          # Add any unstaged changes from the stash
          git add .

          # Commit and Push
          git commit -m "Reapply stashed changes" || echo "No changes to commit"

          # Retry push if failed
          for i in 1 2 3; do
            git push origin main && break
            echo "Push failed, retrying in 5 seconds... ($i)"
            sleep 5
            git pull origin main --rebase || break
          done
```

### 触发

我设定的触发条件是在papers/文件夹中提交了pdf文件时触发。这样只要把文件放到papers文件夹下并提交，就会自动运行。增加workflow_dispatch:是也支持手动触发调试。可根据需求，更改为webhook触发、其他工作流触发或者定时触发等。

### 环境变量

在 `/settings/secrets/actions` 中可配置使用的Key和模型。

使用硅基流动的API，可以选用多种模型。实测跑一份几十页的PDF大概花费赠送余额1毛多，没有注册的朋友欢迎点下方链接，使用我的邀请码注册，你我都可以获赠赠送余额十四元～ 

[点击注册硅基流动](https://cloud.siliconflow.cn/i/PcNzNO65)

使劲测试消耗了两元巨款⬇️

![image.png](https://images.ygria.site/2025/04/50d3dbd9fd36d4353c492d774f1312cb.png)

![image.png](https://images.ygria.site/2025/04/4ca1f7bd7333af2589a67751072b149f.png)

### 执行

执行过程就是安装python环境、安装依赖、命令行执行。将执行出的pdf文件放到`translation_output` 文件夹中，将已翻译好的pdf挪到 `archive`文件夹中。

> [!hint]
> 注意最好在`papers`文件夹下放一个后缀不是pdf文件的文件做占位，不然pdf被挪走后，空文件夹会被自动删掉 。我是放了一个名字就叫placeholder的无后缀空文件做占位。

### 翻译结果提交到库

由于翻译可能执行的时间很长，过程中可能库内文件发生了变更，再做提交时就会发生冲突。

所以提交前并先stash当前内容，再做一次拉取，拉取库内最新的文件，再提交。避免因为冲突，导致文件提交失败。

# 使用

使用起来很简单，就是把需要翻译的文件放到papers文件夹下，提交到github上。等一段时间（过程较长，大的pdf可能要四五十分钟甚至一个多小时，不过都是自动、在云端完成的）翻译完成了，再拉取一下，可以看到翻译结果已经放到translation_output文件夹下啦。

可以翻译书籍、论文等等～

![image.png](https://images.ygria.site/2025/04/2d2aa600e0d89f04f7bb93ee2614afce.png)
![image.png](https://images.ygria.site/2025/04/99f4134b33446ea31b4eae7eafaeddc4.png)


