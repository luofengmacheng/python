## postman使用帮助文档

### 0 前言

postman是常用的用于测试接口的工具，最简单的就是用post和get对url进行请求测试，但是有时候用起来还是有好多问题，今天特地总结下。

### 1 HTTP报文结构

HTTP的请求报文结构如下所示：

```
<method> <path> <protocol_version>
<headers>

<body>
```

method：就是HTTP的请求方法，有GET、POST、PUT、DELETE等
path：请求的路径(域名在请求头中的Host字段)
headers：请求头，主要是一些控制B/S交流行为的字段
body：请求体，传输的具体内容

### 2 常用的方法

GET：通常用于从后台获取数据，当要使用GET方法时，可以在postman上输入url，并在Params部分用键值对形式输入请求参数。
POST：通常用于创建操作。
PUT：通常用于更新操作。
DELETE：通常用于删除操作。

发起一个HTTP请求，只需要两个参数，请求的URL和请求的参数。上面四个操作中，除了GET是将参数放在链接里面(postman中可以直接放在Params，postman可以自动生成链接)，其它的方法都可以将数据放在body里面。

### 3 在body中提交数据

提交数据有三种方式：

* multipart/form-data
* application/x-www-form-urlencoded
* application/json

#### 3.1 multipart/form-data

用途：既可以上传文件，也可以上传键值对。

用一个分隔符分隔多个字段，每个字段包含字段名以及内容，内容可以是文本也可以是二进制。

#### 3.2 application/x-www-form-urlencoded

用途：上传表单的键值对。

此种方式会将表单的数据转变成GET一样的传参方式，只是数据是在body中，而且它只能用来上传键值对。

#### 3.3 application/json

用途：json数据交互。

用此种方式发送数据时，body中是json字符串，在postman中的Body部分，需要先选择`raw`，然后就可以选择JSON，就可以在请求体中填充json是数据。

### 4 小结

这里简单介绍了HTTP的一些规则，以及如何使用postman用于接口测试，还介绍了几种常用的提交数据的类型。