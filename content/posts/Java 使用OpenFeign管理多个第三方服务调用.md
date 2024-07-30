---
title: Java | 使用OpenFeign管理多个第三方服务调用
slug: use-open-feign
date: 2021-04-28
tags:
- 编程
- 后端
---


# 背景
最近开发了一个统一调度类的项目，需要依赖多个第三方服务，这些服务都提供了`HTTP`接口供我调用。

![组件架构](https://img-blog.csdnimg.cn/img_convert/1ff2d029d047f2573ccf599a473dea8d.png)

服务多、接口多，如何进行第三方服务管理和调用就成了问题。

常用的服务间调用往往采用`zk`、`Eureka`等注册中心进行服务管理（`SpringBoot`常使用`SpringCloud`）。`OpenFeign`也是`SpringCloud`的解决方案之一。我们单独使用`OpenFeign`， 无需对原有第三方服务进行改动，本服务开发时的引入也很轻量。

下面给出我的用法。

# 应用
## maven依赖
引入maven依赖：
 ```
        <dependency>
            <groupId>io.github.openfeign</groupId>
            <artifactId>feign-core</artifactId>
            <version>10.2.3</version>
        </dependency>
        <dependency>
            <groupId>io.github.openfeign</groupId>
            <artifactId>feign-gson</artifactId>
            <version>10.2.3</version>
        </dependency>
        <dependency>
            <groupId>io.github.openfeign.form</groupId>
            <artifactId>feign-form</artifactId>
            <version>3.8.0</version>
        </dependency>
        <dependency>
            <groupId>io.github.openfeign.form</groupId>
            <artifactId>feign-form-spring</artifactId>
            <version>3.8.0</version>
        </dependency>
```
其中，form相关引入是为了解决`ContentType`为`application/x-www-form-urlencoded`和`multipart/form-data`的编码问题。
## 配置和服务声明
第三方服务的地址通过配置来注入。
### 服务地址配置
`ThirdpartServiceConfig.java` 
```java
@Data
@Component
@ConfigurationProperties(prefix = "thirdpart-service")
public class ThirdpartServiceConfig {
    private String serviceA;
    private String serviceB;
    private String serviceC;
}
```
服务配置（超时时间配置等也可以写在这里）
 `application.yaml`
```yaml
thirdpart-service:
  serviceA: http://****:***/
  serviceB:  http://****:***/
  serviceC:  http://****:***/
```
### 第三方服务配置
因为声明方法一致，所以省略了多个第三方声明。
`ThirdPartClientConfig.java`
```java
@Configuration
public class ThirdParttClientConfig {

    @Resource
    private ThirdpartServiceConfig thirdpartServiceConfig;

    @Bean
    public ServiceAClient serviceAClient() {
        return Feign.builder()
            .encoder(new FormEncoder(new GsonEncoder()))
            .decoder(new GsonDecoder())
            .target(ServiceAClient.class, thirdpartServiceConfig.getServiceA());
    }
}
```
## 接口声明和使用
完成了服务的声明和服务的配置之后，就可以进行服务接口的声明了。具体声明方法可以参看`OpenFeign`文档：[# [翻译: Spring Cloud Feign使用文档](https://segmentfault.com/a/1190000018313243)
](https://segmentfault.com/a/1190000018313243?utm_source=tag-newest)
下面给出使用示例:
- `GET`请求（`feign`可直接将返回的结果反序列化为本服务中定义的`POJO`）
```java
@RequestLine("GET testGet?a={a}&b={b}")
ServiceResp testGet(@Param("a") String a,@Param("b")String b);
```
- `GET` 下载
使用`feign.Response`接收请求结果
```java
@RequestLine("GET export?exportId={exportId}")
Response exportFromServiceA(@Param("exportId")String exportId);
```

```
@Resource
private ServiceAClient serviceAClient ;

// 导出方法
public void export(exportId) {
    Response serviceResponse = serviceserviceAClient.exportFromServiceA(exportId);
    Response.Body body = serviceResponse.body();
    try(InputStream inputStream = body.asInputStream();
        // 处理获取到的inputStream
    } catch (IOException e) {
    log.error("导出发生异常",e);
}
```
- `POST` application/json"
```java
 @RequestLine("POST /save")
 @Headers("Cofntent-Type: application/json")
  ServiceResp saveEntity(EntityPOJO entityPOJO);
````
- POST form
```java
 @RequestLine("POST  uqa/repo/qa/batch")
 @Headers("Content-Type:multipart/form-data")
 ServiceResp uploadFile(@Param("id")String id, @Param("batch_file") File file);
```
-  注意：除了file类型，其他参数会被序列化为String，所以若第三方接口参数的值为POJO（或Map），可能会出错。
-  对于POJO参数，若第三方参数名含有`Java`中不合法的属性字符（如 ”-“，”#“，”.“等），可使用注解进行序列化时的转化。由于声明`Feign Client`时使用的encoder是`Gson`，所以使用如下注解：
```java 
 @SerializedName(value="aaa-bbb")
 private String aaaBbb;
```
如果使用的是其他序列化工具，改为对应的注解即可。
# 小结
使用声明式的第三方和接口写法，基本覆盖了请求第三方接口的需求，也易于拓展和管理。
我计划在后续添加统一的鉴权、日志打印和异常捕获处理功能，使依赖组件引入的风险更为可控。`OpenFeign`帮我们实现了服务声明、接口声明、HTTP请求发送和结果处理等逻辑，在项目需要调用多个第三方服务时可以使用。
