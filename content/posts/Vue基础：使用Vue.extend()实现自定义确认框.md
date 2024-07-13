---
title: Vue基础：使用Vue.extend()实现自定义确认框
date:  2020-04-28 17:02:00
tags:
- 编程
- 前端
---




# 问题背景
前端交互中经常使用确认框。在删除、修改等操作时，调用后端接口之前，先跳出弹框显示提示信息，提示用户确认，避免用户误操作。
项目中全局引入了Element，提供了一套模态对话框组件，用于消息提示、确认消息、提交内容，使用起来也非常简便。


以下来自于element官网文档：
> 如果你完整引入了 Element，它会为` Vue.prototype `添加如下全局方法：  `$msgbox`, `$alert`, `$confirm` 和` $prompt`。因此在` Vue instance `中可以采用本页面中的方式调用 MessageBox。

代码范例：
```javascript
 
 this.$confirm("此操作将永久删除该文件, 是否继续?", "提示", {
                    confirmButtonText: "确定",
                    cancelButtonText: "取消",
                    type: "warning"
                })
                    .then(() => {
                        this.$message({ type: "success", message: "删除成功!" });
                    })
                    .catch(() => {
                        this.$message({ type: "info", message: "已取消删除" });
                    });
```
Element允许复写样式，如果全局都需要，则可以进行写在全局自定义样式单中，覆盖掉原有样式。
**当Element提供的默认组件不能满足需求时，需要思考一下如何实现？**

# 实现尝试
## 在单组件内部实现确认框

在组件内定义一个对话框，使用时将dialog显示为可见，点击确认时调用方法，点击取消/关闭时将dialog设置为不可见。
在当前页面只需要一个确认框的时候，dialog的标题、内容、确认时调用的方法（`@click = "handler"`）都可以写死。

* 怎么修改对话框内容？
当页面上有多个不同方法均需要对话框确认，那么el-dialog对应的数据是变动的，使用 `v-model`指令绑定一个confirmDialog对象，在触发对话框时，实时修改该对话框所显示的内容，以及按钮对应的方法。
```html
<el-dialog width="600px" :title="confirmDialog.title" :visible.sync="confirmDialog.show">
                <span>{{ confirmDialog.message }}</span>
                <div slot="footer" class="dialog-footer">
                    <el-button @click="confirmDialog.show = false">
                        取 消
                    </el-button>
                    <el-button type="primary" @click="confirmDialog.handler">
                        确 定
                    </el-button>
                </div>
            </el-dialog>

<el-button @click = ""></el-button>
```
script中方法：
```javascript
           deleteFile() {
                this.confirmDialog.title = "删除";
                this.confirmDialog.message = "确认删除文件吗？";
                this.confirmDialog.handler = this.doDeleteFile;
                this.confirmDialog.show = true;
            },
            doDeleteFile() {
                // 删除文件方法
            }
```
* 公有部分抽取
在上述实现中，我们使用多个不同方法去操作同一对象，并且每个操作都需要两个方法实现，第一个方法用来修改confirmDialog的值，第二个方法用来监听确认按钮的点击事件，执行操作。
很容易得出，第一个方法是每个操作都类似的，可以复用的，弹窗HTML代码和样式代码也是共用的，我们将公有的部分独立成组件，就避免了重复工作。
##  如何抽取？
由上一节，我们容易得出，需要抽取的是确认框的DOM，样式，以及数据对象。

### 为什么使用extend
> 上一章总结了子组件如何抽取，并介绍了在父组件中如何使用子组件，使用方法为：
在父组件中引入并注册子组件，在父组件中传入数据，为子组件的prop赋值，并在父组件中控制子组件的显示。

使用父子组件 +局部注册，无需关注子组件的创建，相对来说比较简单。但是有时也会遇到问题：
* 子组件的模板都是事先定义好的，如果我要从接口动态渲染组件模板怎么办？
* 子组件都是在父组件内定义好的位置渲染，假如想要在JS代码中灵活调用，在任意地方渲染怎么办？
这时就轮到`Vue.extend()`出场了。
##  Vue.extend()
`Vue.extend()`是 `Vue`框架提供的全局api，查阅官网文档，相关说明如下：![vue.extend()接口说明](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy82ODEwNjIwLTJhNWM3NDc3NWRiNjY5NmMucG5n?x-oss-process=image/format,png)

> 类比Java，可以将定义好的组件看成一个**模板类**，使用Vue.extend()生成该模板类的继承子类。模板类中提供了默认的变量（模板、样式、变量等），并定义了方法，在js代码中可以继承并覆盖父类的变量和方法。Vue.extend()中接收的参数相当于子类的构造参数。

容易得出，我们需要传入的是对话框绑定的数据模型（data），以及点击确认后执行的方法。
* Promise
参考Element的做法，使用`ES6`中的`Promise`对象封装构造函数的返回，能使代码更加简洁。

# 代码实现
```javascript
import Vue from 'vue';
import confirm from '../Comfirm.vue';
let confirmConstructor = Vue.extend(confirm);
let theConfirm = function (content) {
    return new Promise((res, rej) => {
        //promise封装，ok执行resolve，no执行rejectlet
        let confirmDom = new confirmConstructor({
            el: document.createElement('div')
        })
        document.body.appendChild(confirmDom.$el); //new一个对象，然后插入body里面
        confirmDom.content = content; //为了使confirm的扩展性更强，这个采用对象的方式传入，所有的字段都可以根据需求自定义
        confirmDom.ok = function () {
            res()
            confirmDom.isShow = false
        }
        confirmDom.close = function () {
            rej()
            confirmDom.isShow = false
        }

    })
}
export default theConfirm;
```
Confirm.vue
```
<template>
    <!-- 自定义确认弹窗样式 -->
    <el-dialog width="600px" :title="content.title" :visible.sync="content.show" v-if="isShow">
        <span>{{ content.message }}</span>
        <div slot="footer" class="dialog-footer">
            <el-button @click="close">
                取 消
            </el-button>
            <el-button type="primary" @click="ok">
                确 定
            </el-button>
        </div>
    </el-dialog>

</template>

<script>
    export default {
        data() {
            return {
                // 弹窗内容
                isShow: true,
                content: {
                    title: "",
                    message: "",
                    data: "",
                    show: false
                }
            };
        },
        methods: {
            close() {
              
            },
            ok() {
   
            }
        }
    };
</script>

<style>
</style>
```
在main.js中引入
```javascript
import confirm from '@/confirm.js' 
Vue.prototype.$confirm = confirm;
```
在任意方法中使用
```
 this.$confirm({ title: "删除", message: "确认删除该文件吗？", show: true })
                    .then(() => {
                        //用户点击确认后执行

                    })
                    .catch(() => {
                    // 取消或关闭
                });
            }
```
# 总结
本篇主要涉及知识点：
* `Vue.prototype` 为`Vue`实例添加方法
* `Vue.extend()`使用方法
* `Promise`对象的定义和使用
可复用，易扩展，易维护，是我们编程过程中应当时刻注意的原则。












