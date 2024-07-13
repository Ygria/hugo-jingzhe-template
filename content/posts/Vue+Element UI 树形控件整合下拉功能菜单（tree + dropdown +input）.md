---
title: Vue+Element UI 树形控件整合下拉功能菜单（tree + dropdown +input）
date:  2020-08-08
tags:
- 编程
- 前端
---


这篇博客主要介绍树形控件的两个小小的功能：
- 下拉菜单
- 输入过滤框

以CSS样式为主，也会涉及到Vue组件和element组件的使用。

对于没有层级的数据，我们可以使用表格或卡片来展示。要展示或建立层级关系，就一定会用到树形组件了。
使用Vue + Element UI，构建出最基本的树如下图所示：
![最简单的树结构](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy82ODEwNjIwLTkyMGUwZTA5MDJmOTMyM2YucG5n?x-oss-process=image/format,png)
现在我们就要在这个基础上进行改造，使页面更加符合我们的交互场景。

#  一、下拉菜单
将下拉菜单嵌到树节点中，使操作更加简便、紧凑。
## 效果演示
效果如图：
- 图示1：悬浮在树节点状态
![悬浮在树节点状态](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy82ODEwNjIwLTE0NGI2ZDJmOGYzMWM0ODgucG5n?x-oss-process=image/format,png)
- 图示2：点击三个点图标状态
![点击三个点图标状态](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy82ODEwNjIwLWMxMzFmMmExNDBjZTk4NTYucG5n?x-oss-process=image/format,png)



- 图示3： 选中并选择菜单
![下拉菜单效果](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy82ODEwNjIwLTdmOGY5MzA5MGU5OGQ5ZWEucG5n?x-oss-process=image/format,png)

如上，当鼠标悬浮在树节点上时，出现竖着的三个小点，点击时弹出下拉菜单，显示可以对树节点进行的操作。
## 实现步骤
### 1、使用插槽（`slot`） + 子组件
- 父组件（含有树形控件）模板代码
```html
 <el-tree :data="resourceTree" :ref="tree" node-key="id"  size="small"
                :highlight-current="true" :check-on-click-node="true" >
                <span class="custom-tree-node" slot-scope="{ node, data }">
                    <div class="custom-tree-node-wrapper">
                        <span class="custom-tree-node-label">
                            {{ node.label }}
                        </span>
                        <span class="operate-btns">                
                            <dot-dropdown  :events="dropMenuEvents" :data="{node,data}" @addNode="addNode" />
                        </span>
                    </div>
                </span>
            </el-tree>
```
###  2、 DotDropdown 下拉框代码
很多树形结构都会使用该下拉框，所以定义组件，方便复用。
```html
<template>
    <el-dropdown trigger="click" class="custom-tree-menu" size="small">
        <i class="el-icon-more rotate " />
        <el-dropdown-menu slot="dropdown">
            <el-dropdown-item v-for='(item,index) in events' :key="index" :divided="index >0" @click.native="clickMenu(item)">
                {{item.label}}
            </el-dropdown-item>
        </el-dropdown-menu>
    </el-dropdown>
</template>
<script>
export default {
  props: {
    events: {
      type: Array,
      default: function() {
        return [
          {
            label: '新建同级',
            funcName: 'addNode'
          },
          {
            label: '编辑',
            funcName: 'editNode'
          },
          {
            label: '删除',
            funcName: 'deleteNode'
          }
        ]
      }
    },
    // 注入数据
    data: {
      type: Object
    }
  },
  methods: {
    clickMenu(item) {
      this.$emit(item.funcName, this.data)
    }
  }
}
```
模板代码很简单，是一个点击触发的下拉菜单组件（`trigger="click"`），菜单循环props中传入的events属性，data为从父组件拿到的数据，定义了菜单和菜单的事件（方法名称），当点击菜单（`@click.native`）时，触发：
```javascript
this.$emit(item.funcName, this.data)
```
容易看出，数据和实现方法都是父组件的，该子组件只做了转发。
###  3、 父组件使用子组件
引入和注册子组件，并定义好对应的方法即可。下面给出使用示例：
```html
<span class="operate-btns">
          <dot-dropdown v-if="data.type === 1" :events="dropMenuEvents" :data="{node,data}"/>
          <dot-dropdown v-if="data.type === 2" :events="sysDropMenuEvents" :data="{node,data}" @addNode="addResource" />
 </span>
```
根据数据节点的类型，注入不同的`events`属性，显示不同的下拉框菜单。（常用场景：根节点不可删除、不可编辑，只能新增子级，叶子节点可以新增同级和子级）。
在父组件中的data中定义:
```
sysDropMenuEvents: [{ label: '新增资源', funcName: 'addNode' }],

dropMenuEvents: [
      { label: '新建同级', funcName: 'addPeerNode' },
      { label: '新建子级', funcName: 'addNode' },
      { label: '分配操作', funcName: 'distributeAction' },
      { label: '编辑', funcName: 'editNode' },
      { label: '删除', funcName: 'removeNode' }
 ]
```
父组件编写实际功能方法：
```js
// 打开新增资源弹窗
    addResource({ node, data }) {
      ...
    }
```
> 父组件注入data时，将树节点插槽中的node和data都注入了进去（`:data="{node,data}"`），在使用时也可以用过同样的大括号+属性名的方式拿到对应的属性，这里体现了ES6解构赋值的特性。
### 4、父组件样式
父组件中，树节点的样式：
```css3
 .el-tree-node__content {
      position: relative;
      .operate-btns {
          position: absolute;
          right: 2px;
          display: none;
      }
      // 鼠标悬停时，展示
      &:hover,
      :focus-within {
          .operate-btns {
              display: inline;
          }
      }
  }
 }
```
- 子绝对，父相对，使操作按钮靠贴边显示
- 无状态时不显示，hover或内部元素被激活时显示（`:hover :focus-within`）
### 5、子组件样式
![最终效果](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy82ODEwNjIwLWQyMWRhNmE4ZjU0YzcxNDQucG5n?x-oss-process=image/format,png)
- 旋转图标
原本的图标使用的是element UI提供的 `<i class="el-icon-more" />`，是横着的点点点↓
![原本的图标](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy82ODEwNjIwLTNhNzA5Njg1ZWI2OGY5OWQucG5n?x-oss-process=image/format,png)

图标有点小，颜色也不喜欢。改下字体让它变大一点。这里注意需要修改的是元素的before伪类:
```
 .el-icon-more:before {
      content: "\E794";
      color: #c0c4cc;
      font-size: 20px;
}
```

加一个`transform`将它旋转90°，悬停时鼠标样式为`pointer`:
```
.rotate {
      cursor: pointer;
      margin-left: 5px;
      transform: rotate(90deg);
 }
```
点击时，增加圆形半透明的灰色背景：
```
.rotate:focus {
      width: 20px;
      height: 20px;
      border-radius: 4em;
      background-color: rgba(130, 132, 138, 0.2);
}
```
至此，下拉全部完成。
除了用在树节点中，也可以用在表格中。
# 输入过滤框
`el-tree`提供了过滤方法，使用`:filter-node-method="filterNode"`属性即可。这里主要分享样式：
效果：
![非激活状态](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy82ODEwNjIwLWU0NTIzMjFiODk0NGIzOWIucG5n?x-oss-process=image/format,png)

![激活输入框状态](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy82ODEwNjIwLTQwNmFkNzZlY2Y5MGYyM2IucG5n?x-oss-process=image/format,png)

模板代码：
```html
<div class="filter-input">
    <el-input placeholder="输入资源名称进行过滤" v-model="filterText" size="small" prefix-icon="el-icon-search">
       </el-input>
</div>
```

- 去掉输入框上、左右边框和圆角，并两侧留出10px边距
```
 .el-input__inner,.el-input-group__prepend{
      width: calc(100% - 20px);
      margin:0 10px;
      height: 40px;
      border-top:none;
      border-width: 0 0 1px;
      border-radius:0;
    }
```
- 调整搜索图标大小、颜色和粗细，并稍微调整位置：
```
    .el-input__prefix{
      .el-input__icon{
        margin-right: 15px;
        display: inline-block;
      }
      font-size:18px;
    }
```
> 此时点击输入框，只有下边变蓝色，希望图标的样式也随之更改。
只有`input`被触发了`focus`事件，`icon`感知不到，`:focus`伪类不满足需求了。我们可以使用`:focus-within`伪类，加在`icon`和`input`共同的父类上。
```
.el-input:focus-within{
      .el-icon-search:before {
         color: #3c6eff;
         font-weight: bold;
      }
    }
```
至此完成。
 # 总结
没写前端之前以为前端只是展示从后端拿到的数据，但现在觉得，前端作为面向用户的直接门面，承担了绝大部分交互体验优化的任务。
合理的布局和样式能避免用户的无效操作，体验的优化是一个漫长而细致的过程，可能需要仔细打磨，才能做出好用的产品。



