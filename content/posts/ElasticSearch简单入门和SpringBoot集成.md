---
title: ElasticSearch简单入门和SpringBoot集成
date: 2022-05-07
tags:
- 编程
- 后端
---

# 背景
项目中使用第三方网关系统，该网关使用`ElasticSearch`进行服务访问日志记录。
为充分利用该网关功能，并在数据基础上实现计数、计费功能，需对`ElasticSearch`进行快速学习，并使用Java代码集成，从而实现项目所需要的运营功能。

# ElasticSearch基础知识学习
为快速建立起对ES印象，可按下表进行概念映射：
![image.png](https://cdn.jsdelivr.net/gh/Ygria/Pictures@main/20240417143109.png)

# Kibana搭建
为对ES中数据可视化，在服务器上进行`Kibana`搭建。
### 1、下载指定压缩包
地址： https://www.elastic.co/cn/downloads/kibana
传至服务器上，解压即可。注意要与ES版本相对应。
`kibana-6.8.23-linux-x86_64.tar.gz`

```bash
# 解压缩
tar -zxvf kibana-6.8.23-linux-x86_64.tar.gz
# 进入配置文件，进行配置的编写
vi /config/kibana.yml
```
### 2、修改配置并启动
编辑配置文件如下：
```yaml
# 指定ElasticSearch实例地址
elasticsearch.hosts: ["http://localhost:9200"]
# 指定允许访问服务地址，规定为0.0.0.0，为允许所有ip访问
server.host: "0.0.0.0"
 # 指定es的用户名
elasticsearch.username: "username"
 # 指定es的密码
elasticsearch.password: "password"
# 指定kibana的语言为中文
i18n.locale: "zh-CN"
```
进入bin目录并启动：
```shell
nohup ./kibana &
tailf -n nohup.out
```
访问`ip:5601`端口即可打开页面访问:

![image.png](https://cdn.jsdelivr.net/gh/Ygria/Pictures@main/20240417143159.png)


### 3、页面设置索引规则

![image.png](https://cdn.jsdelivr.net/gh/Ygria/Pictures@main/20240417143214.png)

使用索引模式，建立通配索引后，可以在discover tab下查看到内容。

### 4、使用开发工具，进行查询语句调试
对于需要调试的DSL语句，可以使用开发工具进行请求的调试。



# SpringBoot集成
## 客户端集成（带账号、密码）
1、将密码、地址等配到SpringBoot项目的配置文件中;
2、重写restHighLevelClient
代码清单如下：
```java
@Configuration
@Log4j2
public class ElasticSearchConfiguration {


    @Value("${elasticsearch.host}")
    private String elasticSearchHost;

    @Value("${elasticsearch.port}")
    private String elasticSearchPort;

    @Value("${elasticsearch.username}")
    private String elasticSearchUser;

    @Value("${elasticsearch.password}")
    private String elasticSearchPass;

    @Bean(name = "restHighLevelClient")
    public RestHighLevelClient restHighLevelClient() {
        List<HttpHost> hostLists = new ArrayList<>();
        hostLists.add(new HttpHost(elasticSearchHost, Integer.parseInt(elasticSearchPort), "http"));
        final CredentialsProvider credentialsProvider = new BasicCredentialsProvider();
        credentialsProvider.setCredentials(AuthScope.ANY, new UsernamePasswordCredentials(elasticSearchUser, elasticSearchPass));

        // 转换成 HttpHost 数组
        HttpHost[] httpHost = hostLists.toArray(new HttpHost[]{});
        // 构建连接对象
        RestClientBuilder builder = RestClient.builder(httpHost);
        // 异步连接延时配置
        builder.setRequestConfigCallback(requestConfigBuilder -> {
            requestConfigBuilder.setConnectTimeout(5000);
            requestConfigBuilder.setSocketTimeout(5000);
            requestConfigBuilder.setConnectionRequestTimeout(5000);
            return requestConfigBuilder;
        });
        // 异步连接数配置
        builder.setHttpClientConfigCallback(httpClientBuilder -> {
            httpClientBuilder.setMaxConnTotal(100);
            httpClientBuilder.setMaxConnPerRoute(100);
            return httpClientBuilder.setDefaultCredentialsProvider(credentialsProvider);
        });
        return new RestHighLevelClient(builder);
    }
}
```
# 聚合查询示例
业务需求：
1、按照查询条件，查询某服务的访问次数
2、查询该服务的请求体总长度，用于计量计费
给出单元测试代码：
```java
    @Resource
    RestHighLevelClient client;
    @Test
    public void testQuery() {
        SearchRequest searchRequest = new SearchRequest("sg-access-*");
//构建查询
        SearchSourceBuilder sourceBuilder = new SearchSourceBuilder();

        //按时间聚合，求TX的和
        BoolQueryBuilder queryBuilder = QueryBuilders.boolQuery().must(QueryBuilders.matchPhraseQuery("paasid", "111"))
                .must(QueryBuilders.matchQuery("srvid", "111"));

        AggregationBuilder aggregation = AggregationBuilders.filter("term", queryBuilder);
        aggregation.subAggregation(AggregationBuilders.sum("reqLengthSum").field("reqLength"));

        sourceBuilder.aggregation(aggregation);


        searchRequest.source(sourceBuilder);
        //发送请求
        SearchResponse searchResponse = null;
        try {
            searchResponse = client.search(searchRequest, RequestOptions.DEFAULT);
            Aggregations aggFilter = searchResponse.getAggregations();
            if (aggFilter != null && aggFilter.get("term") != null) {
                ParsedFilter parsedFilter = aggFilter.get("term");
                System.out.println("查询出请求的次数：" + parsedFilter.getDocCount());
                ParsedSum sum = (ParsedSum) parsedFilter.getAggregations().getAsMap().get("reqLengthSum");
                System.out.println("请求体的总大小 ：" +  sum.getValue());
            }

        } catch (IOException e) {
            System.out.println(searchResponse);
        }
    }
```
运行结果如下：
![image.png](https://cdn.jsdelivr.net/gh/Ygria/Pictures@main/20240417143241.png)

可以看出，我们可以通过Java代码，对ES的数据进行条件查询，并对索引进行通配匹配查询，并使用聚合方法进行聚合运算。