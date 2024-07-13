---
title: Vue 定义指令和动态路由实现权限控制
date:  2020-08-27
tags:
- 编程
- 前端
---


功能概述：
- 根据后端返回接口，实现路由动态显示
- 实现按钮（HTML元素）级别权限控制

涉及知识点：
- 路由守卫
- Vuex使用
- Vue自定义指令

# 导航守卫
> 前端工程采用Github开源项目`Vue-element-admin`作为模板，该项目地址：[Github | Vue-element-admin](https://github.com/PanJiaChen/vue-element-admin) 。 

在`Vue-element-admin`模板项目的[src/permission.js](https://github.com/PanJiaChen/vue-element-admin/blob/master/src/permission.js)文件中，给出了路由守卫、加载动态路由的实现方案，在实现了基于不同角色加载动态路由的功能。我们只需要稍作改动，就能将基于角色加载路由改造为基于权限加载路由。
> **导航守卫**：可以应用于在路由跳转时，对用户的登录状态或权限进行判断。项目中使用全局前置守卫。参考Vue官方文档：[https://router.vuejs.org/zh/guide/advanced/navigation-guards.html](https://router.vuejs.org/zh/guide/advanced/navigation-guards.html)

##  后台返回接口

![getUserInfo接口返回用户信息和路由、操作权限等](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy82ODEwNjIwLWNlODcwMTFmNDBkYjljNzIucG5n?x-oss-process=image/format,png)
权限系统后台采用基于角色的权限控制方案（`role-based access control`），如上图所示，
该用户信息接口将查询用户所具有的所有角色，再将这些角色的权限并集按照路由 - 操作整合在一起返回。在用户登录入系统后，我们从后台请求获得用户信息（个人信息 + 权限信息），作为全局属性储存在前端。不同权限的用户看到的页面不同，依赖于这些属性，它们决定了路由如何加载、页面如何渲染。

这种多个组件依赖一组属性的场景，Vue提供了`VueX`作为全局状态管理方案。

## 使用VueX存储权限信息
在`src/store/moudules`目录下定义`permission.js` 
### 1.定义异步方法，方法内部包含HTTP请求从后台拉取数据

```
import http from '../../axios';
async function getUserInfo() {
  const res = await http.getUserInfo();
  return res;
}
```
使用`await`关键字，保证执行顺序正确。这里是为了保证能拿到接口返回的内容，以便于下一步处理。
```
const actions = {
  getPermissions({ commit }) {
    return new Promise(resolve => {
      getUserInfo().then(res => {
        if (res) {
          let permissionList = res.permissionList;
          commit('SET_PERMISSIONS', permissionList);
          // 根据后台返回的路由，生成实际可以访问的路由
          let accessRoutes = filterAsyncRoutesByPermissions(asyncRoutes, permissionList);
          commit('SET_ROUTES', accessRoutes);
          commit('SET_USER_INFO', { name: res.name, accountName: res.accountName })
          resolve(accessRoutes);
        } else {
          resolve([]);
        }
      }).catch(() => resolve([]));
    })
  }
}
```
VueX中action定义异步方法。
###  2. 定义静态、动态路由
`src/router/index.js`
静态路由：
```
export const constantRoutes = [
    {
        path: '/redirect',
        component: Layout,
        hidden: true,
        children: [
            {
                path: '/redirect/:path(.*)',
                component: () => import('@/views/redirect/index'),
            },
        ],
    ,
  ...
    {
        path: '/404',
        component: () => import('@/views/error-page/404'),
        hidden: true,
    }
];
```
动态路由：
```
export const asyncRoutes = [
    {
        path: '/system',
        component: Layout,
        name: '系统管理',
        meta: { title: '系统管理', icon: 'el-icon-user', affix: true },
        children: [
            {
                path: '/system',
                component: () => import('@/views/management/system/Index'),
                meta: { title: '系统管理', icon: 'el-icon-setting', affix: true },
            },
        ],
    }
...
]
```
静态路由中定义了所有用户均可访问的路由，动态路由中定义了动态加载的路由。

### 3.根据权限过滤并排序路由
```
export function filterAsyncRoutesByPermissions(routes, menus) {
  const res = []
  routes.forEach(route => {
    const tmp = { ...route }
    let index = menus.map(menu => menu.url).indexOf(tmp.path);
    if (index != -1) {
      // 后端返回路由信息覆盖前端定义路由信息
      tmp.name = menus[index].name;
      // debugger;
      tmp.meta.title = menus[index].name;
      tmp.children.forEach(child => {
        if (child.path == tmp.path) {
          child.meta.title = tmp.meta.title;
        }
      })
      res.push(tmp)
    }
  });
  // 根据返回菜单顺序，确定路由顺序
  /**
   * TODO 子菜单排序
   */
  res.sort((routeA, routeB) => menus.map(menu => menu.url).indexOf(routeA.path) - menus.map(menu => menu.url).indexOf(routeB.path))
  return res
}
```
根据url匹配，匹配到url的路由则加入数组。最终用户可以访问的路由 = 允许访问的动态路由 + 不需要权限的静态路由。

### 4.src/permission.js中的处理逻辑
```javascript
// 引入store
import store from './store';
const whiteList = ['/login', '/auth-redirect']; // no redirect whitelist

// 路由守卫
router.beforeEach(async (to, from, next) => {
    //start progress bar
    NProgress.start()
    if (hasToken) {
        if (to.path === '/login') {
          // ... 省略登出逻辑
            NProgress.done();
        } else {    
            // 查看是否已缓存过动态路由
            const hasRoutes = store.getters.permission_routes && store.getters.permission_routes.length > 0;
            if (hasRoutes) {
                next();
            } else {
                try {
                    const accessRoutes = await store.dispatch('permission/getPermissions');
                    router.addRoutes(accessRoutes);
                    const toRoute = accessRoutes.filter((route) => route.path == to.path);
                    next({ path: toRoute.length > 0 ? toRoute[0].path : accessRoutes[0].path, replace: true });
                } catch (error) {
                    next(`/login?redirect=${to.path}`);
                    NProgress.done();
                }
            }
        }
    } else {
        if (whiteList.indexOf(to.path) !== -1) {
            // in the free login whitelist, go directly
            next();
        } else {
            next(`/login?redirect=${to.path}`);
            NProgress.done();
        }
    }
});

router.afterEach(() => {
    // finish progress bar
    NProgress.done();
});
```
以上是动态路由实现方案。

---
`Vue`支持自定义指令，用法类似于Vue原生指令如`v-model`、`v-on`等，网上查阅到的大部分细粒度权限控制方案都使用这种方法。下面将给出我的实现。

# 自定义指令
自定义指令 `v-permission`：

`src/directive/permission/index.js`
```javascript
import store from '@/store'
 export default {
  inserted(el, binding, vnode) {
    const { value } = binding
    const permissions = store.getters && store.getters.permissions;
    if (value) {
      // 获取当前所挂载的vue所在的上下文节点url
      let url = vnode.context.$route.path;
      let permissionActions = permissions[url];
      // console.log(permissionActions)
      const hasPermission = permissionActions.some(action => {
        if (value.constructor === Array) {
          // 或判断： 只要存在任1，判定为有权限
          return value.includes(action);
        } else {
          return action === value;
        }
      })
      if (!hasPermission) {
        el.parentNode && el.parentNode.removeChild(el)
      }
    } else {
      throw new Error(`need further permissions!`)
    }
  }
}
```


后端给出的权限数据是路由（url）与操作的对应Map，url可以通过将要挂载到的vnode属性拿到。这个方法有点类似于AOP，在虚拟元素挂载之后做判断，如果没有权限则从父元素上移除掉。
使用方法：
* 举例一：单个按钮 （注意双引号套单引号的写法）
```html
  <el-button @click.native.prevent="editUser(scope.row)" type="text" size="small" v-permission="'op_edit'">
                                编辑
 </el-button>
```
* 举例二：或判断（传入数组），只要拥有数组中一个权限，则保留元素，所有权限都没有，则移除。
在上一篇博客[https://www.jianshu.com/p/066c4ce4c767](https://www.jianshu.com/p/066c4ce4c767)
下拉菜单上增加控制：
![dot-dropdown](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy82ODEwNjIwLTJiNDNjZGFjNThmZmQzM2IucG5n?x-oss-process=image/format,png)
![数据定义](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy82ODEwNjIwLWExZTQyODhhOTAzODA4MGQucG5n?x-oss-process=image/format,png)
相应数据定义中增加action属性。

该方法无法覆盖所有场景，所以依然给出相应工具类：
```
/**
 * 
 * @param {*当前页面路由} url 
 * @param {*操作code e.g op_add } value 
 * @return true/false 是否有该项权限
 */
function checkPermission(url, value) {

    const permissions = store.getters && store.getters.permissions;
    let permissionActions = permissions[url];

    if (!permissionActions) {
        return false;
    }

    let hasPermission = permissionActions.some(action => {
        if (value.constructor === Array) {
            // 或判断： 只要存在任1，判定为有权限
            return value.includes(action);
        } else {
            return action === value;
        }
    });
    return hasPermission;

}
```
 以上完成按钮粒度权限控制。
