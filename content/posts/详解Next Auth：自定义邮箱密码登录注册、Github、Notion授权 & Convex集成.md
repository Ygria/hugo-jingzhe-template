---
title: 详解Next Auth：自定义邮箱密码登录注册、Github、Notion授权 & Convex集成
date: 2024-06-12
tags:
  - 编程
  - 全栈
image:   https://next-auth.js.org/img/logo/logo-sm.png
---


最近用NextJS框架做全栈项目做的很顺手，现在想给项目加上**登录、注册、鉴权拦截、分角色路由控制**等功能，并接入Github、Notion等第三方登录。
可以使用NextJS官方提供的Auth框架实现。

# Intro

阅读本篇，你将学会：
1、登录、注册等逻辑，和如何接入第三方（以Github、Notion为例）
2、建立用户、角色等数据模型，存储用户数据
3、公开、私有路由守卫

## 技术栈

*   NextJs（前端框架）  v14.2.3
*   React（前端框架）  18
*   NextAuth（鉴权框架） v5.0.0-beta.18
*   Convex （后端接口 + ORM）

## 背景知识学习

在开始实现之前，需要知道NextJS中服务端组件和客户端组件的概念。
NextJS中使用”use client“和”use server“标识服务端和客户端组件，客户端运行在浏览器中，服务端运行在服务器端。**不标识时，默认为服务端组件。**
服务端组件用于异步请求等，负责与服务端交互、请求数据等，客户端组件主要用于和用户交互。React的钩子也有明确的区分，比如useEffect等钩子只能在客户端组件中使用。

# 实现步骤

## 代码框架搭建

```node
npx create-next-app@latest  
```

使用**NextAuth（v5版本）**

```node
npm install next-auth@beta  
```

开始之前，需要在环境变量文件`.env.local`中配置变量

```json
AUTH_SECRET=**********************
```

# Credentials

我们首先实现一个简单的账号密码注册、登录、登出。
参考： [Credentials](https://authjs.dev/getting-started/authentication/credentials#credentials-provider)

## 1.基础配置

在项目根目录下，新建`auth.js`文件，并写入以下内容：

```javascript
import NextAuth from "next-auth"
import Credentials from "next-auth/providers/credentials"
// Your own logic for dealing with plaintext password strings; be careful!
import { saltAndHashPassword } from "@/utils/password"
 
export const { handlers, signIn, signOut, auth } = NextAuth({
  providers: [
    Credentials({
      authorize: async (credentials) => {
        let user = null
 
       // logic to salt and hash password
        const pwHash = saltAndHashPassword(credentials.password)
 
        // logic to verify if user exists
        user = await getUserFromDb(credentials.email, pwHash)
 
        if (!user) {
          // No user found, so this is their first attempt to login
          // meaning this is also the place you could do registration
          throw new Error("User not found.")
        }
 
        // return user object with the their profile data
        return user
      },
    }),
  ],
})
```

在根目录下，新建文件`middleware.ts`

```javascript
import NextAuth from 'next-auth';

import {
DEFAULT_LOGIN_REDIRECT,
apiAuthPrefix,
authRoutes,
publicRoutes,
} from "@/routes"

import { auth } from './auth';
export default auth((req) => {

const { nextUrl } = req;
// console.log("NEXT URL" + nextUrl.pathname)
const isLoggedIn = !!req.auth;
const isApiAuthRoute = nextUrl.pathname.startsWith(apiAuthPrefix);
const isPublicRoutes = publicRoutes.includes(nextUrl.pathname);
const isAuthRoute = authRoutes.includes(nextUrl.pathname);
if (isApiAuthRoute) {
// DO NOTHING!
return null;

}
if (isAuthRoute) {
if (isLoggedIn) {
return Response.redirect(new URL(DEFAULT_LOGIN_REDIRECT, nextUrl))
} else {
return null;
}
}

if (!isLoggedIn && !isPublicRoutes) {

return Response.redirect(new URL("/auth/login", nextUrl))

}

})
// invoke the middle ware!

export const config = {

matcher: ["/((?!.+\\.[\\w]+$|_next).*)", "/", "/(api|trpc)(.*)"],

};
```

routes.ts

```javascript
// Public Routes
export const publicRoutes = [
"/",
]
// redirect logged in users to /settings
export const authRoutes = [
"/auth/login",
"/auth/register",
]
export const apiAuthPrefix = "/api/auth"
export const DEFAULT_LOGIN_REDIRECT = "/dashboard"
```

`middleware.ts`为保留文件名，其中`config`变量定义了触发中间件方法的匹配规则。该文件中，定义了`auth`方法的过滤器。
在`route.ts`中定义公开路径、用于鉴权的路径、鉴权接口前缀及默认重定向地址。
在过滤方法中，返回null说明无需执行权限检查。对于公开路径及鉴权接口，无需登录即可访问。登录后，再访问注册和登录页面，会自动重定向到`DEFAULT_LOGIN_REDIRECT`定义的`/dashboard`路由中。
配置NextAuth路由：
`api/auth/[...nextauth]/route.ts`

```javascript
import { handlers } from "@/auth"
export const { GET, POST } = handlers
```

## 2.注册页面
实现形如下图的注册页面，核心为可提交的表单，包含name、email、password等字段。

![image.png](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/d13f0c305c004e24bea0da279ee4ce37~tplv-k3u1fbpfcp-jj-mark:0:0:0:0:q75.image#?w=388\&h=561\&s=25327\&e=png\&b=ffffff)

使用zod进行字段的合法性校验。在`schemas/index.ts`中，定义注册使用的schema：
```ts
import * as z from "zod"
export const RegisterSchema = z.object({
    email: z.string().email({
        message: "Email is Required."
    }),
    password: z.string().min(6,{
        message: "Minimum 6 characters required",
    }),
    name: z.string().min(1,{
        message: "Name is Required"
    })
})
```

注册页面代码（部分）：
```ts
"use client"
import { useState, useTransition } from "react"
import { cn } from "@/lib/utils"
import * as z from "zod"
import { zodResolver } from "@hookform/resolvers/zod"
import { register } from "@/actions/register"
interface RegisterFormProps extends React.HTMLAttributes<HTMLDivElement> { }
export function RegisterForm({ className, ...props }: RegisterFormProps) {
  const [isPending, startTransition] = useTransition();
  const [error, setError] = useState<string | undefined>("");
  const [success, setSuccess] = useState<string | undefined>("");
  const form = useForm<z.infer<typeof RegisterSchema>>({
    resolver: zodResolver(RegisterSchema),
    defaultValues: {
      name: "",
      email: "",
      password: ""
    }
  });
  async function onSubmit(values: z.infer<typeof RegisterSchema>) {
    setError("")
    setSuccess("")
    startTransition(() => {
      register(values).then((data) => {
        setError(data.error)
        setSuccess(data.success)
      })
    })
  }
  return (
    <div className={cn("grid gap-6", className)} {...props}>  
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
          // form field inputs
            <Button type="submit" className="w-full" disabled={isPending}>Create an account</Button>
          </form>
    </div>
  )
}
```
`actions/register.ts` 处理注册用户入库：
```ts
"use server";

import * as z from "zod"
import { RegisterSchema } from "@/schemas";
import  bcrypt  from "bcryptjs"
import { api } from "@/convex/_generated/api";
import { fetchMutation, fetchQuery } from "convex/nextjs";
import { getUserByEmail } from "@/data/user";

export const register = async (values: z.infer<typeof RegisterSchema>) => {
    const validatedFields = RegisterSchema.safeParse(values);
    if (!validatedFields.success) {
        return {
            error: "Invalid fields!"
        }
    }
    const { email, password, name } = validatedFields.data;
    const hasedPassword = await bcrypt.hash(password, 10)
    const existingUser = await getUserByEmail(email)
    if (existingUser) {
        ``
        return {
            error: "Email already in use!"
        }
    }
    await fetchMutation(api.user.create, {
        name,
        email,
        password: hasedPassword
    })
    // TODO : Send verification token email
    return {
        // error: "Invalid fields!",
        success: "User Created"
    }
}
```
用户在注册页面填写名称、邮箱、密码后，点击submit按钮，客户端组件调用了服务组件方法，先查询邮箱是否被占用，未被占用，将明文密码使用`bcryptjs`加密后，存入数据库中。
## 3.用户登录

![image.png](https://p1-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/e1a207eee5b14f279f6e7c469af4c482~tplv-k3u1fbpfcp-jj-mark:0:0:0:0:q75.image#?w=430&h=519&s=23590&e=png&b=ffffff)
同样使用zod进行登录表单的字段的合法性校验。在`schemas/index.ts`中，定义登录使用的schema：
```ts
import * as z from "zod"
export const LoginSchema = z.object({
    email: z.string().email(),
    password: z.string().min(1)
})
```
> 注意：不应限制用户填入密码规则。虽然注册时限定了用户填写的密码至少6位，但系统的密码规则有可能变更。

登录页面代码（部分）：
```ts
"use client"
import { useState, useTransition } from "react"
import { cn } from "@/lib/utils"
import { useForm } from "react-hook-form"
import { LoginSchema } from "@/schemas"
import * as z from "zod"
import { zodResolver } from "@hookform/resolvers/zod"
import { login } from "@/actions/login"
interface LoginFormProps extends React.HTMLAttributes<HTMLDivElement> { }

export function LoginForm({ className, ...props }: LoginFormProps) {
  const [isPending, startTransition] = useTransition();
  const [error, setError] = useState<string | undefined>("");
  const [success, setSuccess] = useState<string | undefined>("");
  const form = useForm<z.infer<typeof LoginSchema>>({
    resolver: zodResolver(LoginSchema),
    defaultValues: {
      email: "",
      password: ""
    }
  });

  async function onSubmit(values: z.infer<typeof LoginSchema>) {
    setError("")
    setSuccess("")
    startTransition(() => {
      login(values).then((data) => {
        if (data && data.error) {
          setError(data.error)
        }
      })
    })
  }
 return (
    <div className={cn("grid gap-6", className)} {...props}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
            <Button type="submit" className="w-full" disabled={isPending}>Login</Button>
          </form>
    </div>
  )
}

```
`actions/login.ts` 登录操作：
```ts
"use server";
import { signIn } from "@/auth";
import * as z from "zod"
import { LoginSchema } from "@/schemas";
import { DEFAULT_LOGIN_REDIRECT } from "@/routes";
import { AuthError } from "next-auth";
export const login = async (values: z.infer<typeof LoginSchema>) => {
    const validatedFields = LoginSchema.safeParse(values);
    if (!validatedFields.success) {
        return {
            error: "Invalid fields!"
        }
    }
    const { email, password } = validatedFields.data;
    console.log("EMAIL!" + email + "PASSWORD!" + password)

    try {
        await signIn("credentials", {
            email, password,
            // redirect: true,
            redirectTo: DEFAULT_LOGIN_REDIRECT
        },)
    } catch (error) {
        if (error instanceof AuthError) {
            switch (error.type) {
                case "CredentialsSignin":
                    return { error: "Invalid Credentials!" }
                default:
                    return { error: "Something went wrong!" }
            }
        }
        throw error;
    }
}
```
可以看到，该操作从`@/auth`中导入了SignIn方法，第一个参数指定了Provider，实际的授权在Provider定义的`authorize`方法中完成：
```ts
import bcrypt from "bcryptjs";
import NextAuth, { type DefaultSession } from "next-auth";
import Credentials from "next-auth/providers/credentials";
import { LoginSchema } from "./schemas";

export const { auth, handlers, signIn, signOut } = NextAuth({
    providers: [
        Credentials({
            async authorize(credentials) {
                const validatedFields = LoginSchema.safeParse(credentials);
                if (validatedFields.success) {
                    const { email, password } = validatedFields.data;
                    const user = await getUserByEmailFromDB(email);
                    if (!user || !user.password) return null;

                    const passwordsMatch = await bcrypt.compare(password, user.password);
                    if (passwordsMatch) {
                        return {
                            ...user,
                            id: user._id
                        }
                    }
                }
                return null;
            },

        }),]

}
```
其中，由于密码在注册时使用了`bcryptjs`加密，所以比较时也要使用`bcryptjs`提供的match方法。至此，使用邮箱和密码登录注册的简单逻辑已完成。

# Github Provider
## 1. 新建Github Oauth App

在`https://github.com/settings/developers`下，新建Oauth Apps

![image.png](https://p1-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/0fe1d1952c894a0887147f2c2a1cfffb~tplv-k3u1fbpfcp-jj-mark:0:0:0:0:q75.image#?w=1518&h=993&s=139826&e=png&b=ffffff)

> Callback url很重要，一定是你的站点host+port，后面配置为Next Auth默认回跳地址`/api/auth/callback/github`。（我当前配置为开发用，生产时需要改为线上地址。）


![image.png](https://p1-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/c6f6072a4ba2443cb684b1939776a5d4~tplv-k3u1fbpfcp-jj-mark:0:0:0:0:q75.image#?w=670&h=467&s=58414&e=png&b=ffffff)
配置完成后，将Client ID 和Client Secret粘贴到配置文件中。
`.env.local`
```env
GITHUB_CLIENT_ID=****
GITHUB_CLIENT_SECRET=****
```

## 2. 配置Github Provider

在`auth.ts`的Providers数组中，加入：
```ts
GitHub({
  clientId: process.env.GITHUB_CLIENT_ID,
  clientSecret: process.env.GITHUB_CLIENT_SECRET,
  allowDangerousEmailAccountLinking: true
}),
```
`allowDangerousEmailAccountLinking`是允许使用同一邮箱的Github、Notion账号互联。若不配置该属性，使用同一邮箱注册的Notion和Github（或其他第三方）登录将被拦截。当使用的Providers来自于不可靠的OAuth App厂商，须谨慎使用该属性。
## 3.页面触发Github登录
`social.tsx`
从`@/auth.ts`中导入登录方法，并在点击按钮时触发即可。
```ts
"use client"
import { FaGithub } from "react-icons/fa"
import { SiNotion } from "react-icons/si";
import { Button } from "@/components/ui/button"
import { signIn } from "next-auth/react"
import { DEFAULT_LOGIN_REDIRECT } from "@/routes"

export const Social = () => {
    const onClick = (provider: "github" | "notion") => {
        signIn(provider, {
            callbackUrl: DEFAULT_LOGIN_REDIRECT
        })
    }

    return (
        <div className="flex items-center w-full gap-x-2">
            <Button size="lg" className="w-full" variant="outline" onClick={() => onClick("github")}>
                <FaGithub className="h-5 w-5"></FaGithub>
            </Button>
            <Button size="lg" className="w-full" variant="outline" onClick={() => onClick("notion")}>
                <SiNotion className="h-5 w-5" />
            </Button>


        </div>
    )
}
```
首次点击时，会跳转到Github询问是否授权。之后会直接点击后跳转鉴权并登录。
# Notion Provider
Notion登录的配置方法与Github非常类似。
## 1. 配置Public Ingegration
前往https://www.notion.so/my-integrations ，新建一个Integration，并设置为公有

![image.png](https://p9-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/ddb316800dbd49e8adf78d60df2ea3e3~tplv-k3u1fbpfcp-jj-mark:0:0:0:0:q75.image#?w=1127&h=648&s=103126&e=png&b=fefdfb)
需将回调地址配置为`/api/auth/callback/notion`

![image.png](https://p1-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/1fbdfd00f8094b7bb6f2d522f73c15b1~tplv-k3u1fbpfcp-jj-mark:0:0:0:0:q75.image#?w=601&h=620&s=71973&e=png&b=fdfcfa)

生成并复制Secrets：

![image.png](https://p6-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/00b68d512f5246f381d18b667779e902~tplv-k3u1fbpfcp-jj-mark:0:0:0:0:q75.image#?w=988&h=407&s=40786&e=png&b=fefdfb)


将Client ID和Secret复制到配置文件中。
``` json
AUTH_NOTION_ID=""
AUTH_NOTION_SECRET=""
AUTH_NOTION_REDIRECT_URI="http://localhost:3001/api/auth/callback/notion"
```
## 2. 配置Notion Provider

在`auth.ts`的Providers数组中，加入：
```ts
 Notion({
      clientId: process.env.AUTH_NOTION_ID,
      clientSecret: process.env.AUTH_NOTION_SECRET,
      redirectUri: process.env.AUTH_NOTION_REDIRECT_URI,
      allowDangerousEmailAccountLinking: true
    }),
```
需传入redirectUri（该uri必须配置到上一步的Ingegration中）
## 使用Notion登录

登录的触发方法与Github相同，不赘述。点击登录时，会多出一步，可以选择授权访问的page范围。

![image.png](https://p9-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/c9b1c6b82d9f4dbe9ab8c1f64750fe8b~tplv-k3u1fbpfcp-jj-mark:0:0:0:0:q75.image#?w=663&h=733&s=70654&e=png&b=fdfcfc)

# Convex Adapter
参考文档：
1. [Auth.js | Creating A Database Adapter](https://authjs.dev/guides/creating-a-database-adapter)
2. https://stack.convex.dev/nextauth-adapter

本应用使用了Convex作为后台API提供，所以需要实现Convex Adapter。按https://stack.convex.dev/nextauth-adapter 步骤操作即可。

`auth.ts`
```ts
import NextAuth from "next-auth"
import { ConvexAdapter } from "@/app/ConvexAdapter";
 
export const { handlers, auth, signIn, signOut } = NextAuth({
  providers: [],
  adapter: ConvexAdapter,
})

```

> **注意避坑！！！！**
> 
> 这里遇到了一个坑，配置了Convex Adapter后，使用邮箱密码再也无法登陆。经过调试发现是通过Credentials登录时，没有调用createSession方法，session没有创建。在Github上搜索后，发现有人遇到类似问题：https://github.com/nextauthjs/next-auth/issues/3970

**在auth.ts中增加如下配置：**

```ts
 session: {
    // Set to jwt in order to CredentialsProvider works properly
    strategy: 'jwt'
  }
```
即可解决问题！！（卡了好久，真的有点坑……教训就是遇到问题先上github搜搜issue，我一直试图手动自己往数据库塞入一个session未果……）

# 其他功能
## 1.回调 callbacks
在回调中，可以向session加入自定义属性

`auth.ts`

```ts
  callbacks: {
    async signIn({ user }) {
      // console.log("AFTER SIGN IN !" + JSON.stringify(user));
      return true;
    },

    async jwt({ token, user, account, profile, isNewUser, session }) {
      if (user) {
        token.id = user.id
      }
      const notionAccount = await getNotionAccount(token.id!! as Id<"users">)
      if (notionAccount) {
        token.notion_token = notionAccount.access_token;
      
      }
      return token;
    },

    async session({ token, session }) {
      if (token.sub && session.user) {
        session.user.id = token.sub;
      }
      if (token.notion_token && session.user) {
        session.user.notion_token = token.notion_token;
      }

      return session;
    },
  },
```
执行顺序： signIn => jwt => session

可在session中读到在jwt方法返回的token值，可将需要的属性放到session中，如角色、权限等。此处我将Notion的secret放到session中，以便业务代码中取用。
## 2.自定义Session类型
在auth.ts中加入如下代码，可解决自定义session中的属性报ts错误问题。
```ts
declare module "next-auth" {
  /**
   * Returned by `auth`, `useSession`, `getSession` and received as a prop on the `SessionProvider` React Context
   */
  interface Session {
    user: {
      role: string;
      notion_token: string;
    } & DefaultSession["user"];
  }
}

```

## 3.事件 events

`auth.ts`
```ts
  events: {
    async linkAccount({ user }) {
      if (user.id) {
        await setEmailVerified(user.id)
      }
    },
  },
```
一个用户（user）可连接多个account（由github、notion等提供的第三方OAuth账号），可设置当连接用户时，将用户设置为邮箱已验证（通过github、notion等可靠app登录的用户无需二次验证邮箱。）

## 4.页面

`auth.ts`
```
  pages: {
    signIn: "/auth/login",
    error: "/auth/error"
  },
```

指定登录页、自定义鉴权出错页。

## 5.登出
`action/logout.ts`
```ts
"use server"
import { signOut } from "@/auth"

export const logout = async () => {
    //  Some server stuff
    await signOut();
}
```
在客户端组件中使用：
```ts
import { logout } from "@/actions/logout";
function onClickSignOut() {
    logout();
}
```
## 6.使用Session获取用户信息

在客户端调用useSession(),需要在SessionProvider的包裹下使用。

`(protected)/layout.ts`
```ts
import { Suspense } from "react";

import { SessionProvider } from "next-auth/react";

export default async function DashboardLayout({
  children, // will be a page or nested layout
}: {
  children: React.ReactNode;
}) {
  return (
    <SessionProvider>
        <div>{children}</div>     
    </SessionProvider>
  );
}

```
```ts
import { useSession } from "next-auth/react";
const session = useSession();
```
# 总结
NextAuth能帮助你快速集成第三方登录，也支持灵活的自定义账号、密码登录。

借助ORM框架和一些中间件，一个NextJS项目已可以完成所有业务功能，不需要再有独立的后端服务。对于小而美的项目，是一个快速落地的理想选择。

