---
title: JavaScript ES6  使用展开运算符完成全平台校验重名逻辑封装
date:  2021-07-08
tags:
- 编程
- 前端
---



# 背景
在应用系统中创建业务对象时，需要填写表单，对于对象的名称、标识等，全平台往往有统一的功能规范。
例如：
- 名称：统一为中文、不超过50字符、不能为空、不能与现有平台重复
- 标识：统一为英文，不超过50字符、不能为空、不能与现有平台重复
交互逻辑一致（填写名称/标识后，调用后台接口进行判断，后台查询数据库后，返回是否存在重名数据（`true/false`）,存在重复则报表单校验错误，不允许表单提交），前端使用的组件也一致（使用`element-UI`的`Form`组件），公共逻辑清晰，于是我尝试进行统一的**规则校验逻辑**方法封装，简化了大量重复代码，在使用时用**展开运算符`spread(...)`**进行引入，保证了代码的优雅和简洁。

# 展开（spread）运算符
展开运算符是`JavaScript ES6`的特性，可以用于数组、字符串、对象的解构赋值。
具体使用逻辑请参考：[扩展运算符](https://github.com/ruanyf/es6tutorial/blob/3929f4f21148dcd2a10d2ebc722323a5dbd473f4/docs/array.md)

# 校验逻辑方法定义
## 校验函数封装
定义方法入参：
1、资源英文名称
用于拼接调用后端`RESTful`接口，例如：校验应用重复，后端定义接口URI为：
`/api/applications/nameOrKeyExisted`，此时资源英文名称为`applications`
2、资源中文名 
用于页面提示回显，例如：表单中应用名称没有填写，提示：“请填写应用名称”，应用名称已存在，提示：“应用名称重复”，此时资源中文名为“应用”
3、附加参数
- 有些资源限定为某类型下不能重复，或某个领域内不能重复，在调用判重接口时需要传递给后端。
- prop参数，用于表单绑定的`prop`定义，如果不传，默认为name和key，允许传入自定义值。
方法前端源码（定义在通用的`util.js`中，在Vue工程中可以在`main.js`引入到全局中。）

定义方法返回：
返回对象，对象中，键对应表单 `prop`属性，值是一个数组，包括多种规则（特殊字符校验、非空校验、重名校验等）
utils.js：
```
/**
 * @entity 校验实体资源
 * @entityName 校验实体中文名
 * @options  调用校验接口，额外参数传递
 */
function getRules(entity, entityName,options) {
  let name = options?.nameProp || 'name'
  let key = options?.keyProp || 'key'
  let rules = {};
  rules[name] = validateRules(
    'name',
    entity,
    entityName,
    options?.params
  );
  rules[key] = validateRules(
    'key',
    entity,
    entityName,
    options?.params
  );
  return rules;

}
function validateRules(field, entity, entityName,extraParams) {
  let rules = [];

  let requiredRule = {
    required: true,
    message: `请输入${entityName}${field === 'key' ? '标识' : '名称'}`,
    trigger: "blur",
  };
  if (field == 'key') {
    let maxLengthRule = { max: 40, message: "不得超过40个字符", trigger: "blur" };
    rules.push(maxLengthRule);
    rules.push({ validator: keyValidator, trigger: ['blur', 'change'] })
  } else {
    let maxLengthRule = { max: 16, message: "不得超过16个字符", trigger: "blur" };
    rules.push(maxLengthRule);
    rules.push({ validator: nameValidator, trigger: ['blur', 'change'] })
  }

  rules.push(requiredRule);
  rules.push(
    {
      validator:
        nameOrKeyExistedValidator,
      entity: entity,
      extraParams: extraParams,
      entityName: entityName,
      trigger: "blur",
    }
  );
  return rules;
}
const keyValidator = (rule, value, callback) => {
  const reg = /^[a-zA-Z0-9_]+$/
  if (!reg.test(value)) {
    callback(new Error('仅支持英文、数字和下划线'))
  } else {
    callback();
  }
}
const nameValidator = (rule, value, callback) => {
  const reg = /^[a-zA-Z0-9_\u4e00-\u9fa5]+$/

  if (!reg.test(value)) {
    callback(new Error('仅支持中文、英文、数字和下划线'))
  } else {
    callback();
  }
}
const nameOrKeyExistedValidator = (rule, value, callback) => {
  if (rule.oldVal && rule.oldVal === value) {
    callback();
  } else {
    nameOrKeyExisted(rule.entity, rule.field, value,rule.extraParams).then(res => {
      if (res) {
        if (rule.field === "name") {
          callback(`${rule.entityName}名称重复`)
        } else {
          callback(`${rule.entityName}标识重复`)
        }
      } else {
        callback();
      }
    })
  }
}
```
- 编辑实体时的判断逻辑（传入oldVal，避免错误的报错）
这里的逻辑暂时没想到比较好的解决方法，所以写的比较恶心，因为原先的值可能是异步拿到的，所以需要手动赋值。传入oldVal后，当表单输入值与原先的值一致时，就不会调用后端判重接口了。
```
  created() {
    if (this.isEdit) {
      this.rules.name[3].oldVal = this.ruleForm.name
      this.rules.key[3].oldVal = this.ruleForm.key
    }
  }
```


封装后端axios请求：
```
export function nameOrKeyExisted(entityName, type, data, params) {
  let queryParams ={};
  if (params) {
     queryParams = {
      ...params,
      type: type,
      nameOrKey: data
     }
  } else {
     queryParams = {
      type: type,
      nameOrKey: data
    }
  }
  return $get(`/api/${entityName}/nameOrKeyExisted`, queryParams)
}
```
请求的封装需要后端的配合~（因为这个平台后端也是由我一手包办的，所以当然不在话下啦）
* 后端定义接口时，只需要注意后端URI和返回值一致就可以了。

# 使用

```
 <el-form :model="esseForm" :rules="esseFormRules" ref="baseInfoForm">
...
</el-form>
```
```
 esseFormRules: {
        type: [
          {
            required: true,
            message: '请选择实体类型',
            trigger: 'blur'
          }
        ],

        ...this.$utils.validate.getRules('sem-esses', '实体',{params: {user: a}})
      },
```
如上，使用展开运算符，将返回的结果赋值到rules对象中，名称和标识的规则由通用的校验函数根据入参生成，该方法已经挂载到全局的$utils上，无需额外的引入成本，一次性生成了对于名称、标识的所有校验。
# 小结
本方法适用于校验逻辑雷同、并且需要实体创建和校验的平台，如果功规调整，也能快速适应（例如长度从限制50字符改为限制100字符），节约时间。
缺陷：校验规则函数的灵活度往往与复杂度成正比，如果需要更多特殊的校验，需要考虑是否有必要修改校验函数，可能不太适用这种方法，如果创建表单的校验逻辑差异较大，就还是建议为每个表单定义自己的rules规则。
