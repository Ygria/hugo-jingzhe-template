---
title: 博客美化：代码块美化示例
date: 2024-07-19 11:13:33 +0800
slug: prettier-codeblock-demo
icon: 🥳
tags:
  - 建站
  - 编程
---

1. 默认（可自定义）
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

```rust{title="rust demo" theme="candy" mode="dark"}
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
```javascript{title="layouts/_default/render-codeblock.html" theme="ice" mode="dark" }
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

```javascript{title="layouts/_default/render-codeblock.html" theme="breeze" mode="dark"}
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

## 4.forest
```javascript{title="layouts/_default/render-codeblock.html" theme="forest" }
import { Detail } from "@raycast/api";

export default function Command() {
  return <Detail markdown="Hello World" />;
}
```
```javascript{title="layouts/_default/render-codeblock.html" theme="forest" mode ="dark"}
import { Detail } from "@raycast/api";

export default function Command() {
  return <Detail markdown="Hello World" />;
}
```

## 5.mono
```javascript{title="layouts/_default/render-codeblock.html" theme="mono" }
import { Detail } from "@raycast/api";

export default function Command() {
  return <Detail markdown="Hello World" />;
}
```
```javascript{title="layouts/_default/render-codeblock.html" theme="mono" mode ="dark"}
import { Detail } from "@raycast/api";

export default function Command() {
  return <Detail markdown="Hello World" />;
}
```
## 6.midnight
```javascript{title="layouts/_default/render-codeblock.html" theme="midnight" }
import { Detail } from "@raycast/api";

export default function Command() {
  return <Detail markdown="Hello World" />;
}
```
```javascript{title="layouts/_default/render-codeblock.html" theme="midnight" mode ="dark"}
import { Detail } from "@raycast/api";

export default function Command() {
  return <Detail markdown="Hello World" />;
}
```

## 7.raindrop
```javascript{title="layouts/_default/render-codeblock.html" theme="raindrop" }
import { Detail } from "@raycast/api";

export default function Command() {
  return <Detail markdown="Hello World" />;
}
```
```javascript{title="layouts/_default/render-codeblock.html" theme="raindrop" mode ="dark"}
import { Detail } from "@raycast/api";

export default function Command() {
  return <Detail markdown="Hello World" />;
}
```

## 8.meadow

```javascript{title="Untitled" theme="meadow" }
import { Detail } from "@raycast/api";

export default function Command() {
  return <Detail markdown="Hello World" />;
}
```
```javascript{title="Untitled" theme="meadow" mode ="dark"}
import { Detail } from "@raycast/api";

export default function Command() {
  return <Detail markdown="Hello World" />;
}
```


## 9.falcon

```javascript{title="Untitled" theme="falcon" }
import { Detail } from "@raycast/api";

export default function Command() {
  return <Detail markdown="Hello World" />;
}
```
```javascript{title="Untitled" theme="falcon" mode ="dark"}
import { Detail } from "@raycast/api";

export default function Command() {
  return <Detail markdown="Hello World" />;
}
```

## 10.crimson


```javascript{title="Untitled" theme="crimson" }
import { Detail } from "@raycast/api";

export default function Command() {
  return <Detail markdown="Hello World" />;
}
```
```javascript{title="Untitled" theme="crimson" mode ="dark"}
import { Detail } from "@raycast/api";

export default function Command() {
  return <Detail markdown="Hello World" />;
}
```

## 11.noir

```javascript{title="Untitled" theme="noir" }
import { Detail } from "@raycast/api";

export default function Command() {
  return <Detail markdown="Hello World" />;
}
```
```javascript{title="Untitled" theme="noir" mode ="dark"}
import { Detail } from "@raycast/api";

export default function Command() {
  return <Detail markdown="Hello World" />;
}
```

## 12.sunset

```javascript{title="Untitled" theme="sunset" }
import { Detail } from "@raycast/api";

export default function Command() {
  return <Detail markdown="Hello World" />;
}
```
```javascript{title="Untitled" theme="sunset" mode ="dark"}
import { Detail } from "@raycast/api";

export default function Command() {
  return <Detail markdown="Hello World" />;
}
```