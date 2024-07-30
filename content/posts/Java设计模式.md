---
title: Java设计模式
date: 2018-06-10
slug: java-design-pattern
tags:
- 编程
---

# 定义









基本概念：保证一个类仅有一个实例，并提供一个访问它的全局访问点
# 懒汉式
```java
public class Singleton {
	//持有私有的单例对象，防止被引用。赋值为null，目的是实现延迟加载
	private static Singleton instance = null;
	//私有的构造方法，防止被实例化
	private Singleton() {}
	//1：懒汉式，静态工程方法，创建实例
	public static Singleton getInstance() {
		if (intsatnce == null) {
        	instance = new Singleton();
		}
        return instance;
    }
}

```
调用：
```java
Singleton.getInstance().method();
```
优点：延迟加载（需要的时候才去加载），适合单线程操作
缺点：线程不安全。在多线程中很容易出现不同步的情况（如在数据库对象进行频繁读写时）

# 双重线程检查模式
```java
public class 