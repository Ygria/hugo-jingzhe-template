---
title: 博客美化：代码块美化测试
date: 2024-07-19 11:13:33 +0800
slug: test
icon: 🥳
tags:
  - 建站
  - 编程
---

1. 普通显示
什么也不传：

```
declare a=1
echo "$a"
exit
```

传入标题、语言等


```rust{title="layouts/_default/render-codeblock.html" theme="candy"}
declare a=1
echo "$a"
exit
```

黑暗模式：需要传递 mode = "dark"

```rust{title="layouts/_default/render-codeblock.html" theme="candy" mode="dark"}
declare a=1
echo "$a"
exit
```

2. 更换主题

## 1. ice
```javascript{title="layouts/_default/render-codeblock.html" theme="ice" }
import { Detail } from "@raycast/api";

export default function Command() {
  return <Detail markdown="Hello World" />;
}
```

## 2. breeze

```javascript{title="layouts/_default/render-codeblock.html" theme="breeze" }
import { Detail } from "@raycast/api";

export default function Command() {
  return <Detail markdown="Hello World" />;
}
```

## 3.Sand
```javascript{title="layouts/_default/render-codeblock.html" theme="sand" }
import { Detail } from "@raycast/api";

export default function Command() {
  return <Detail markdown="Hello World" />;
}
```
```javascript{title="layouts/_default/render-codeblock.html" theme="sand" mode ="dark"}
import { Detail } from "@raycast/api";

export default function Command() {
  return <Detail markdown="Hello World" />;
}
```