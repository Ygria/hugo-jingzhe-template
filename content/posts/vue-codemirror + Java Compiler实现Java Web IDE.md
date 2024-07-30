---
title: vue-codemirror + Java Compiler实现Java Web IDE
date:  2020-05-23 17:02:00
slug: web-ide
tags:
- 编程
---


# 背景
>最近同事告诉我一个很有趣的需求：让用户（应用场景中，一般为其他开发者）自己填入**Java代码片段**，代码片段的内容为已经规定好的模板类的**继承类**，实现模板类定义的方法。我们的项目要实现动态编译代码片段，存储代码片段和用户操作记录的映射关系，并能够在业务中载入代码片段执行。

这有点像我们提供一个模板模式的架构，只不过模板类的实现类由外部接口填入代码片段动态实现。相较让其他开发者直接参与项目开发，无疑：

1. 降低了侵入风险
2. 向其他开发者隐藏了大部分实现
3. 降低操作难度和开发门槛
4. 便于管理 

……
这相当于要实现一个简单的在线Java开发环境，提供基础的代码填写、编译和保存的功能。
# 效果演示
![切换主题](https://upload-images.jianshu.io/upload_images/6810620-031e296dac25d5c4.gif?imageMogr2/auto-orient/strip)

![联动填写类名](https://upload-images.jianshu.io/upload_images/6810620-304fdf364d8713a2.gif?imageMogr2/auto-orient/strip)

![测试编译](https://upload-images.jianshu.io/upload_images/6810620-fd427cfe187231e9.gif?imageMogr2/auto-orient/strip)


基于`vue-codemirror`和`Java Compiler`的动态编译，实现了上述需求，目前完成的Web端IDE主要功能点包括：
- 页面展示Java代码块（代码高亮，有行号、可自动补全括号等）
- 从服务端获取模板类代码，并提供示例
- 实时动态编译并获取编译结果（通过/失败 todo:返回编译错误信息)
- 将输入字符串加载成Java Class
以及小的功能点：自动缩进、补全括号、切换主题、联动填写类名等等。
下面给出涉及到的技术和实现方法。
--- 
# CodeMirror
CodeMirror是一个JS库，可以支持实现有丰富的附加功能和多种语言支持。我们项目的前端使用Vue框架，可以很方便地集成并使用CodeMirror提供的插件，实现我们的在线IDE多种特性。
参考：[CodeMirror官网](https://codemirror.net/)
## 引入
安装依赖：`  "vue-codemirror": "^4.0.6"`
在`src`目录下的`main.js`中引入：
```javascript
import VueCodeMirror from 'vue-codemirror'
import 'codemirror/lib/codemirror.css'
Vue.use(VueCodeMirror)
```
## 使用
新建组件`JavaIDE.vue`
```vue
<template>
    <codemirror ref="codeMirrorEditor" :value="code" :options="cmOptions" @changes="onChange">
  </codemirror>
  </template>  
  <script>
      import codemirror from "codemirror/lib/codemirror";
      require("codemirror/mode/clike/clike.js");
      require("codemirror/addon/edit/closebrackets.js");
      components: {
          codemirror;
      }
      export default{
          data(){
              return{
                code: "",
                cmOptions:{
                    mode: "text/x-java",  //Java语言
                    theme: "darcula", // 默认主题
                    autofocus: true,  
                    lineNumbers: true,   //显示行号
                    smartIndent: true, // 自动缩进
                    autoCloseBrackets: true// 自动补全括号
                }
              }
          }
  </script>
```
组件化地使用它，我们可以方便地操作它绑定的值（code）和其他附加选项（cmOption)。
在组件创建时为code赋值，即可实现加载模板代码。
> 根据官网，我们可以直接使用CodeMirror的默认构造函数，也可以提供一个`textarea DOM`元素作为构造CodeMirror对象的参数。

可以使用`readOnly`参数将代码块设置为只读。

### 联动填写类名功能
希望实现：在上面顶栏中填写类名，在代码中联动填写。
实现方式： 使用正则匹配替换代码片段，再进行替换
使用相同的方法，也可以实现动态补全类名等功能 
>参考更多[JavaScript的正则表达式](https://www.runoob.com/js/js-regexp.html)

为输入框加上监听函数`@input="changeClassName"`
```javascript
 changeClassName(className) {
    var reg = new RegExp(/public class .*? extends ActionParamBuilder/);
    this.code = this.code.replace(reg,
                    "public class " + className + " extends ActionParamBuilder"
   );
 }
```
### 切换主题
引入主题`css`样式文件
```
 import "codemirror/theme/eclipse.css";
 import "codemirror/theme/darcula.css";
 import "codemirror/theme/blackboard.css";
``` 
使用String数组定义支持的主题，并使用 `Element-UI`提供的`Select`组件支持主题切换：
```
<el-select v-model="cmOptions.theme" placeholder="切换主题" @change="changeTheme">
          <span slot="prefix">
             <el-tooltip content="更换主题">
              <a-icon type="skin" style="fontSize:16px;line-height=50px;"/>
      </el-tooltip>
      </span>
 <el-option v-for="(item,index) in supportThemes" :key="index" :label="item" :value="item">
   </el-option>
</el-select>
```
* 使用`slot`实现在选择器中嵌入图标，并支持`tooltip`功能，使工具栏更加紧凑。 `slot`意为插槽，是封装好的组件预留的可以自定义的空间，我们可以使用`slot = ""`把DOM元素置入到组件内部，非常灵活。
### 样式覆写
使用`!important`关键字覆盖原有CodeMirror样式。注意，将该样式放在全局而不是局部`scoped`样式表中。
```
.CodeMirror {
     height: 500px !important;
 }
```
# JavaCompiler
不用将传入的代码保存成`.java`文件写入磁盘，直接就可以使用`JavaCompiler`工具对字符串进行编译。
> 为了实现实时动态编译功能，我搜索了关于如何将字符串编译成class的方法，还看了一些动态代理的实现思路。后来看到这一篇：[
Java运行时动态生成class的方法](https://www.liaoxuefeng.com/article/1080190250181920)，发现这就是我想要的！

使用Java SDK（since 1.6）提供的JavaCompiler工具。该工具提供编译方法：
```java
  CompilationTask getTask(Writer out,
                            JavaFileManager fileManager,
                            DiagnosticListener<? super JavaFileObject> diagnosticListener,
                            Iterable<String> options,
                            Iterable<String> classes,
                            Iterable<? extends JavaFileObject> compilationUnits);
```
* `JavaFileManager` 
自定义`MemoryJavaFileManager`，继承`ForwardingJavaFileManager<JavaFileManager>`，实现从内存字符串中读取JavaFileObject
重点是下面这个方法：
```java
	JavaFileObject makeStringSource(String name, String code) {
		return new MemoryInputJavaFileObject(name, code);
	}
	static class MemoryInputJavaFileObject extends SimpleJavaFileObject {
		final String code;
		MemoryInputJavaFileObject(String name, String code) {
			super(URI.create("string:///" + name), Kind.SOURCE);
			this.code = code;
		}
		@Override
		public CharBuffer getCharContent(boolean ignoreEncodingErrors) {
			return CharBuffer.wrap(code);
		}
	}
```
- `options`，可选参数列表，可以**增加外部Jar包依赖**
因为我们所需要编译的代码里依赖的类来源于外部的Jar包，所以需要将这些Jar包使用`option`将这些依赖加进去。这一步踩了坑，因为之前没用过，不知道怎么写……最后终于找到了正确的写法：
`List<String> optionList =Arrays.asList("-extdirs",extLib);`
`extLib`是外部jar包的路径（目录地址）。可以使用路径分隔符填入多个路径。
- `DiagnosticListener` 诊断信息监听
加入诊断信息监听器，我们可以拿到编译错误信息，把这些信息反馈给前端，实现实时编译并报错的功能。
`DiagnosticCollector diagnosticCollector = new DiagnosticCollector();`
- `JavaFileObject` 待编译的Java对象，调用自定义类`MemoryJavaFileManager` 的`makeStringSource`方法。可以传入一组编译单元。
完整方法如下：
```
public Map<String, byte[]> compile(String fileName, String source,String extLib) throws IOException {
		try (MemoryJavaFileManager manager = new MemoryJavaFileManager(stdManager)) {
			JavaFileObject javaFileObject = manager.makeStringSource(fileName, source);    
            // 传入诊断监听器 size和传入的javaObject相同
            DiagnosticCollector diagnosticCollector = new DiagnosticCollector();
			List<String> optionList =Arrays.asList("-extdirs",extLib);
			CompilationTask task = compiler.getTask(null, manager,diagnosticCollector, optionList, null, Arrays.asList(javaFileObject));
			Boolean result = task.call();
			if (result == null || !result.booleanValue()) {
				throw new RuntimeException("Compilation failed.");
			}
			return manager.getClassBytes();
		}
	}
```
调用代码：
```
 Map<String, byte[]> results = javaStringCompiler.compile(className + ".java", CODE_TO_COMPILE, libDir);
```

# 自定义ClassLoader
> 参考[《Java编程的逻辑》](https://book.douban.com/subject/30133440/)中24.5中内容，我们可以使用自定义的`ClassLoader`来加载用户代码片段，成为可调用的Class对象。
- 继承`URLClassLoader`
- 重写`findClass`方法
```java
class MemoryClassLoader extends URLClassLoader {

	// class name to class bytes:
	Map<String, byte[]> classBytes = new HashMap<String, byte[]>();

	public MemoryClassLoader(Map<String, byte[]> classBytes) {
		super(new URL[0], MemoryClassLoader.class.getClassLoader());
		this.classBytes.putAll(classBytes);
	}

	@Override
	protected Class<?> findClass(String name) throws ClassNotFoundException {
		byte[] buf = classBytes.get(name);
		if (buf == null) {
			return super.findClass(name);
		}
		classBytes.remove(name);
		return defineClass(name, buf, 0, buf.length);
	}

}
```
自定义类加载器有如下好处：
- 可以自定义读取class文件字节码方法和形式，如：从内存中、指定jar包中，或从数据库/网络读取等
- 实现隔离，可以实现使用同一个类的不同版本
- 实现热部署，动态更新类的内容



# 总结
本篇中主要涉及知识点:
-  `vue-codemirror`集成和使用
- `JavaCompiler`的使用
- `JavaScript`正则和`Vue`中的插槽（`slot`）
- 自定义`ClassLoader`实现动态加载
