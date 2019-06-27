## RESTful使用要点

### 1 RESTful含义

REST的含义是(资源)表现层状态转换，下面从这几个方面说下REST本身的具体含义，也是在使用REST中的关键点：

* 资源：REST以资源为中心，所有的增删改查都围绕资源进行
* 表现层：数据的表示形式，例如，JSON、XML等
* 状态转换：所有的操作都是无状态的，客户端进行操作时，需要通过某种手段，让服务端数据发生状态转换

### 2 RESTful要点

#### 2.1 请求格式

1 客户端发出请求的格式是`HTTP方法 + 资源 + 筛选参数`，其中，HTTP方法与CRUD的对应关系分别是：

* POST：创建(Create)
* GET：读取(Retrieve)
* PUT：更新(Update)
* PATCH：部分更新
* DELETE：删除(Delete)

而资源则对应了请求的资源的路径，剩下的筛选参数则指明要对结果进行一定的操作。

2 URL中不能出现动词，而应该都是名词

3 如果客户端只能使用HTTP中的某些方法，例如，只能使用GET，则可以在URL中加上HTTP方法，例如：`/DELETE/books`，或者将实际的方法放在请求头部的`X-HTTP-Method-Override`字段

#### 2.2 返回码

返回码最好是能够精确地表明结果状态，例如，401表示Unauthorized(没有权限)，405表示Method Not Allowed(不能使用该HTTP方法)

#### 2.3 版本

api的设计中通常都会有版本信息，例如：v1版本的api的功能与v2版本的api的功能是不一样的，那么在调用时就需要对版本进行区分：

`GET /api/v1/books`

### 3 kubernetes中api的设计

#### 3.1 将请求代理到api-server

在k8s集群中，如果想要访问api-server，需要进行授权，因此，如果只是调试或者学习，则可以在node节点上启动proxy，通过proxy将请求转发给api-server，具体的方法是：

* 在node节点上启动proxy：`kubectl proxy`，就会在默认的8001端口上启动代理server
* 在node节点上访问本地的8001端口：`curl 'localhost:8001'`，就可以看到所有的api列表

#### 3.2 kubernetes的api设计规则

![Kubernetes API reference](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.15/)

1 访问根路径可以返回所有的api列表，这里面分成以下几种类型：

* `/api`，是核心组api，后面可以跟api的版本：`/api/v1`
* `/apis`，是其它组api，后面可以跟的是对象以及版本号
* `/healthz`，健康检查
* `/logs`，日志
* `/metrics`，指标
* `/openapi/v2`和`/swagger`等都是与api的描述相关
* `/version`，api-server的版本

2 通过HTTP方法对资源进行操作

3 调用接口返回的状态码符合HTTP规范，同时在出错时会返回状态对象，状态对象被编码为JSON，同时在状态对象中会给出出错的详细原因：

```
{
  "kind": "Status",
  "apiVersion": "v1",
  "metadata": {
    
  },
  "status": "Failure",
  "message": "the server could not find the requested resource",
  "reason": "NotFound",
  "details": {
    
  },
  "code": 404
}
```



