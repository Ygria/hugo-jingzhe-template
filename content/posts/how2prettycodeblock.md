---
title: Hugo博客美化：更美观代码块生成，支持复制和导出图片
date: 2024-07-21 22:13:33 +0800
slug: prettier-codeblock
icon: 🪄
tags:
  - 建站
  - 编程
---

实现效果： [博客美化：代码块美化示例 - Ygria's Blog](https://ygria.site/prettier-codeblock-demo/)

![my-image (14).png](https://images.ygria.site/2024/07/adb5bf3140f5cbdc6bd90fb48f1a6996.png)

![my-image (24).png](https://images.ygria.site/2024/07/cf3233e35929ac0bd8d3f1d22031986e.png)

偶然看到ray.so的开源工具网站：[Create beautiful images of your code](https://www.ray.so/)，提供了非常漂亮的代码图片生成功能，支持一系列主题，并能对代码块进行高亮、添加背景并导出成图片。

![image.png](https://images.ygria.site/2024/07/e081fa9eb92ffce80c80d17a175ea1b6.png)


正好最近在折腾我的Hugo静态博客，索性就把这个功能集成了进来。配合Hugo官方提供的render-codeblock hook，可以无痛兼容之前的博客文章。
# Hugo render code hook


参考Hugo博客官方给出的文档： [Code block render hooks | Hugo](https://gohugo.io/render-hooks/code-blocks/)，我们可以劫持Markdown文件生成html的过程，用自己的代码段代替。

在主题文件夹下（如果没有主题，则在根目录下），新建文件`render-codeblock.html`(注意文件名一定不能弄错，否则会无法解析到)
```{title="render-codeblock"  mode="dark" nobackground = "true" }
your-hugo-site/
├── themes/
   └── themename/
       ├── layouts/
          └── _default/
                  └── _markup/
                      └── render-codeblock.html

```

在配置文件中，添加：
```toml
# Hugo 解析文档的配置
[markup]
  # 语法高亮设置 (https://gohugo.io/content-management/syntax-highlighting)
  [markup.highlight]
    noClasses = false
```
这样我们就可以编写自己的渲染逻辑了。

# render-codeblock模版结构

通过检查元素，容易得到页面结构为：

```{title="render-code-template"  mode="dark" nobackground = "true" }
wrapper 最外层）
├── background（根据传入参数，判断是否显示）
├──  window（代码窗口）
       ├──  header 
        │   └── controls 仿apple窗口的三个圆点
        │   └──  fileName 文件名
        │  └── 操作button，支持复制代码和导出图片
        └──   code（代码块） 

```
在这个页面可以通过`.Type`拿到传入的语言（即写markdown语法时，\`\`\`后紧邻的声明）,并能通过类似于\`\`\`{title="rust demo" theme="candy" mode="dark" padding="16"}语法，传入attribute map并在模版代码中解析。通过这种方法，我们能够更灵活地应用代码块并渲染不同的样式。



# 自定义高亮

## 主题声明

通过查看ray.so源码得知使用了[shiki](https://shiki.style/) 进行高亮，并自定义了若干主题。在assets/js下新建一个名为hightlighter.js的文件
并导入shiki：
```javascript
import { getHighlighter } from 'https://esm.sh/shiki@1.0.0'
```
需要将这个js文件引入到Hugo模版代码中。由于使用了import语法，需要声明type = "module"
```go
{{ $hightlightJS := resources.Get "js/hightlight.js" | resources.Minify | resources.Fingerprint }}
<script src="{{ $hightlightJS.Permalink }}" defer type = "module"></script>
```


将ray.so中声明的主题列表THEMES拷贝过来(在`app/(navigation)/(code)/store/themes.ts`中：)

![image.png](https://images.ygria.site/2024/07/2f30abdcad1324e0bcb5a60232a07b02.png)

通过阅读源码，得知是通过动态替换CSS Variable的值来渲染主题的，因此我们只需要声明一个主题，即css-variables主题。

```javascript
const shikiTheme = createCssVariablesTheme({
  name: "css-variables",
  variablePrefix: "--ray-",
  variableDefaults: {},
  fontStyle: true,
});
```
该主题通过读取当前作用域内的CSS Variables的值进行代码高亮。

## 声明用于高亮的hightlighter

使用单例，声明hightlighter。这里我做了单例声明，这样如果页面上有很多代码块，可以避免重复创建多次，并预先将页面上所有代码块使用的语言遍历出来，获取hightlighter。
```javascript
const ShikiHightlighter = (function () {
  let highlight = null;
  async function init(languages) {
    // Singleton 初始化代码
    highlight = await getHighlighter({
      langs: languages,
      themes: [shikiTheme]
    })
    return highlight
  }

  return {
    getInstance: function (languages) {
      if (!highlight) {
        highlight = init(languages);
      }
      return highlight;
    }
  };
})();

// after dom loaded
document.querySelectorAll('[id^="code-id-"]').forEach(element => {
    console.log(element.dataset.language); 
    languages.add(element.dataset.language)
});
var highlighter = await ShikiHightlighter.getInstance(Array.from(languages));
```
## 页面加载后，执行高亮逻辑
在render-codeblock.html中，将读入的属性放到html元素的CSS属性内，再通过CSS选择器和属性进行获取。格式为`data-*`的属性，可以直接通过`element.dataset.*`的方式来获取，很方便。
根据传入的theme和mode（light或dark），可以从THEMES对象里拿到CSS Varible属性，将这个属性赋到code wrapper上，这样高亮出的效果就和变量一致了。
```javascript{padding=16}
document.addEventListener("DOMContentLoaded", async function () {
  const codeblocks = document.querySelectorAll(".code-wrapper");
  // 如果有，则调用hightlight
  if (codeblocks) {
    const languages= new Set();
    document.querySelectorAll('[id^="code-id-"]').forEach(element => {
      console.log(element.dataset.language); 
      languages.add(element.dataset.language)
    });
    var highlighter = await ShikiHightlighter.getInstance(Array.from(languages));
    codeblocks.forEach(async codeblock => {
      try {
        const codeElement = codeblock.querySelector('[id^="code-"]')
        const code = codeElement.textContent;
        const language = codeElement.dataset.language;
        const variables = THEMES[codeElement.dataset.theme]['syntax'][codeblock.dataset.theme]
        const styleVariables = Object.keys(variables).map(key => `${key}: ${variables[key]};`).join(' ');
        codeblock.style = styleVariables;
        console.log("data-language :" + language); // 输出: "python"
         // 使用shiki进行代码高亮
        const highlightedCode = await highlighter.codeToHtml(code, {
          lang: language,
          theme: "css-variables"
        })
        codeElement.innerHTML = highlightedCode;
      } catch (error) {
        console.error("hightlight failed...", error)
      }
    })
  }
}
)
```

## header、bg、padding及样式背景图片
均使用Attribute传入，通过CSS实现。
值得一提的是darkmode的写法,通过变量的形式，变化变量颜色。这样样式就不用写两遍了～
```scss
:root {
    --ray-highlight-hover: rgba(0, 0, 0, 0.05);
    --ray-highlight: rgba(0, 0, 0, 0.1);
    --ray-highlight-border: transparent;
    --line-number: rgba(0, 0, 0, 0.2);
  }
  
  [data-theme="dark"] {
    --frame-highlight-border: rgba(255, 255, 255, 0.3);
    --ray-highlight-hover: rgba(255, 255, 255, 0.05);
    --ray-highlight: rgba(255, 255, 255, 0.1);
    --line-number: rgba(255, 255, 255, 0.2);
  }
  .window {
        display: flex;
        box-shadow: 0 0 0 1px var(--frame-highlight-border), 0 0 0 1.5px var(--frame-shadow-border), 0 2.8px 2.2px rgba(0, 0, 0, 0.034), 0 6.7px 5.3px rgba(0, 0, 0, 0.048), 0 12.5px 10px rgba(0, 0, 0, 0.06), 0 22.3px 17.9px rgba(0, 0, 0, 0.072), 0 41.8px 33.4px rgba(0, 0, 0, 0.086), 0 100px 80px rgba(0, 0, 0, 0.12);
        background: var(--frame-background);       
    }
```

# 其他功能

## 复制代码
逻辑：在header中加入两个元素，一个图标为复制，一个为复制成功(隐藏)。监听按钮点击事件，点击后，向剪贴板写入文本，并将复制按钮隐藏，显示复制成功按钮。
三秒后，重新显示复制按钮。

```html
<button id="copyButton-{{ $id }}">
    <svg class="lucide lucide-copy" />
</button>
<button id="copySuccess-{{ $id }}" style="display: none;" >
    <svg class="lucide lucide-clipboard-check" />
</button>
```
```javascript
const copyButton = codeblock.querySelector('[id^="copyButton-"]');
const copySuccess = document.querySelector('[id^="copySuccess-"]')
//  复制代码
copyButton.addEventListener("click", () => {
    navigator.clipboard.writeText(code)
    copyButton.style.display = 'none';

    copySuccess.style.display = "block"
    setTimeout(() => {
    copyButton.style.display = 'block';
    copySuccess.style.display = "none"
    }, 3000)
})
```

## 导出图片
使用html2canvas库。需在baseof.html中引入：
```html
<script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
```
为了美观，导出时将复制、导出等按钮隐藏了，等下载好了再显示。
```javascript
// 导出成图片
const controlButtons = codeblock.querySelector('[id^="controls-button-"]');
const exportImageButton = codeblock.querySelector('[id^="exportImage-"]');
exportImageButton.addEventListener("click", async () => {
    { {/*  const wrapper = document.querySelector()  */ } }
    controlButtons.style.visibility = 'hidden';
    html2canvas(codeblock).then(canvas => {
    // 添加 canvas 到 body，可选
    { {/*  document.body.appendChild(canvas);  */ } }

    // 保存为图片
    var img = canvas.toDataURL("image/png");

    // 创建一个链接元素用于下载
    var link = document.createElement('a');
    link.download = 'my-image.png';
    link.href = img;
    link.click();
    controlButtons.style.visibility = 'visible';
    });
})
```
# 总结
通过看源码，学习到了很多关于CSS变量的知识。原生HTML、JS、CSS也是很强大的～框架能做，原生基本也能做。
