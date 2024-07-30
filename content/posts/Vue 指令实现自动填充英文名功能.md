---
title: Vue 指令实现自动填充英文名功能
date:  2021-05-21 
slug: vue-func
tags:
- 编程
- 前端
- Vuejs
---

- 背景：应用系统中存在多个创建实体表单，表单填写时，在填写中文名称后，要填写对应的英文名作为标识或数据库查询索引。
- 需求：**填写中文名的同时，系统自动生成英文名并填充到表单中，辅助用户操作，节约操作时间。**
# 实现效果
![转全拼](https://img-blog.csdnimg.cn/img_convert/28c3278af86760a4e9fa3a04588173b9.gif)

![转英文（伪）](https://img-blog.csdnimg.cn/img_convert/85a002b82a346a8bd03fd6d9f3161673.gif)




#  方案调研
对需求进行分析后，对于如何将中文名翻译成英文字符串，调研以下方案：
-  调用翻译引擎
优点：翻译准确，对于短句也能翻译
缺点：部署难度大，需要捆绑翻译引擎
- 调用开放API（谷歌翻译/百度翻译等）
优点：能完成翻译功能
缺点：可能需要付费/开发者帐号等，需要集成成本，需要私有化部署版本时（无法连接外网）可能无法实现
- 使用音译插件（参考：https://github.com/dzcpy/transliteration）
优点：轻量，集成简单，有一定可扩展性，可离线
缺点：无法翻译，只能音译（会将“你好”翻译成“ni_hao”而不是“hello"），使标识的可读性和语义性下降。

以上三种仅为中转英的方法不同，均可实现功能。本次方案暂使用第三种。
 # 实现方案
- 分析：该功能需要增加到多个表单中，如果为每个需要添加的组件都增加相应逻辑，侵入性较强，也不好维护。
- 逻辑提炼：
1. 为中文名的输入框绑定监听事件，监听输入，取得该input框输入的值
2. 将第一步中获得的中文值转化成英文字符串
3. 将英文字符串写入到英文名输入框中
思路： 为表单添加`vue`自定义指令，通过取子节点（根据虚拟节点层级，`vnode`的子级）的方法，获取到需要操作的dom元素，再在指令逻辑中进行逻辑处理。

# 代码实现
## 指令定义
- 定义`v-transliterate `指令（vue自定义指令的定义和使用可参考官方文档，此处不做赘述）
- `transliterate.js`
```javascript
import { transliterate as tr, slugify } from 'transliteration'
export default {
  inserted(el, binding, vnode) {
    let sourceInputEl = vnode.componentInstance.$children.find(item => item.prop === 'name').$children[1].$el.children[0]
    let targetInputEl = vnode.componentInstance.$children.find(item => item.prop === 'key').$children[1].$el.children[0]

    let isFirstInput = true;

    sourceInputEl.addEventListener('keyup', () => {
      // 判断当前标识是否已填写，若已填写，则不再根据中文名称生成
      let isEmpty = !targetInputEl.value;

      if (isEmpty || !isFirstInput) {
    // 一定延迟处理，用户使用几乎无感知
        setTimeout(() => {
          let transValue = slugify(sourceInputEl.value, { separator: '_' });
          let inputEvt = new InputEvent('input', {
            inputType: 'insertText',
            data: transValue,
            dataTransfer: null,
            isComposing: false
          });
          targetInputEl.value = transValue;
          targetInputEl.dispatchEvent(inputEvt);
          isFirstInput = false;

        }, 500);
      }
    })

  }
}
```
##  注意事项 
1、transValue的生成可根据前面所说的不同方案，更改生成的方法。
2、两个input 元素是根据prop来筛选的，代码中硬编码为”name“ -中文名 和”key“ 英文名，可根据需求调整，也可以根据指令方法入参的binding赋值。由于本项目中所有表单prop都是固定的，所以没有写相应逻辑。
3、`keyup`事件可根据需求更改为`blur`事件，对于调用后台api获值，可考虑改为blur，降低频繁请求。
4、执行` targetInputEl.value = transValue;`  后，页面上显示已经改变，但点击保存表单时仍然会触发空值校验，怀疑是因为该赋值没有刷新到虚拟节点的model中，故而使用 `targetInputEl.dispatchEvent(inputEvt);`方法模拟输入事件，触发值的刷新。
5、`isEmpty`  空值校验，避免用户在填写表单时先填写了英文名，再填写中文名时，英文名被覆盖。逻辑一般限定标识生成后就不允许修改，该方法也规避了修改时的英文名跟着中文名修改的问题。
6、使用`transliterate `可定义配置字典，实现常用中-英单词的翻译，但仍然无法替代翻译引擎。配置逻辑参考github上的README即可。
`slugify.config({ replace: [['世界','world'],['你好','hello']] });`

## 指令使用

需要用该功能的地方，在表单元素增加该指令即可。
![指令使用](https://img-blog.csdnimg.cn/img_convert/fa9079117854ffa7932e6bde2dfd9665.png)

# 总结
以上就是实现全过程，如果有更好的实现方法，请留言告诉我哦~

