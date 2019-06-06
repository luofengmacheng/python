## Tornado中的主要模块

常用模块：

* options 命令行和配置文件解析(通过该模块处理命令行参数和配置文件)
* escape HTML、JSON、url等的编解码
* web 基础web框架()
* httpserver HTTP服务器
* tcpserver TCP服务器
* ioloop 核心的I/O循环
* testing 单元测试
* process 多进程实现

模块分类：

1 核心模块：

* web 基础web框架
* httpserver HTTP服务器
* tcpserver TCP服务器
* template 模版系统
* escape HTML、JSON、url等的编解码
* locale 国际化支持

2 底层模块：

* ioloop 核心的I/O循环
* iosteam 
* httpclient/simple_httpclient/curl_httpclient 实现了http的客户端，其中httpclient定义了后面两者的接口，simple_httpclient满足大部分的需求，只是在少部分场景才需要用到curl_httpclient

3 与其它服务

* auth 第三方认证模块
* websocket 用于实现实时通信，常用于弹幕等实时消息推送
* wsgi 与其它python网络框架/服务器交互

4 工具模块

* options 参数和配置文件解析
* process 多进程实现
* testing 单元测试
* gen 基于生成器的协程实现(不过建议使用新的async/await)
* autoreload 开发环境可以自动检查代码更新并重新加载(开发人员不会直接使用该模块)

### 1 options

`tornado.options`是tornado中的一个选项模块，可以用于自定义程序配置。在使用配置时，可以按照以下步骤进行：

* 定义程序包含的配置项

``` python
from tornado.options import define

# 使用define()函数定义了一个配置(参数)，默认值为80，类型为int，把它放在global组中
# 如果配置太多，可以对配置进行分组
define("listen_port", default=80, help="server listen port", type=int, group="global")
```

* 在配置文件中定义配置的值

``` python
# config/tornado.conf
# 配置文件中是完全合法的python代码
listen_port = 8081
```

* 在程序中解析：`tornado.options.parse_config_file("config/tornado.conf")`

* 在程序中使用配置的值：`tornado.options.options['listen_port']`

### 2 escape



