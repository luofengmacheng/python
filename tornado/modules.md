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

### 1 常用模块之间的关系

* 用户的应用程序中至少会引用web和ioloop模块：web模块中定义了Application和RequestHandler，Application可以用于封装系统配置和路由配置；
* web模块中主要定义两个类：RequestHandler，请求处理类，其中包含参数处理、返回数据处理，还有一些Hook函数；Application，应用类，主要用于封装请求处理类和一些配置，用于构建应用程序，

### 2 options

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

### 3 web

web中的两个类RequestHandler和Application是用于构建应用必不可少的。

#### 3.1 web.RequestHandler

RequestHandler是请求处理的基类，但是在实际使用中，通常会派生出业务使用的请求处理基类，其中会处理包含如登录等问题。

RequestHandler类中的方法可以分成几大类：

* 请求处理函数：例如获取请求中的参数(get_query_argument、get_body_argument、get_argument)、进行业务处理逻辑(head、get、post、delete、path、put、options都会定义为未实现的方法，子类如果需要可以进行实现)、返回请求处理结果(write和render)
* 请求处理过程中的钩子：initialize()、prepare(请求处理前执行)、on_finish(请求执行结束后执行)、on_connection_close()
* HTTP协议处理相关：响应返回码(set_status)，响应头部(set_header、add_header、clear_header)，cookie(get_cookie、set_cookie、clear_cookie、clear_all_cookie、set_secure_cookie)，重定向(redirect)
* 其它：用户处理(current_user)，安全(xsrf_token、check_xsrf_cookie、xsrf_form_html)

#### 3.2 web.Application

Application的方法比较少，主要是对请求处理器的操作：

* listen：对HTTPServer的listen的封装(实际上是调用tcpserver.TCPServer的listen)
* add_handlers：添加请求处理器
* add_transform：添加转换器
* __call__：
* find_handler：查找请求处理器
* get_handler_delegate：
* reverse_url：
* log_request：记录请求日志

结合RequestHandler和Application，请求的处理逻辑如下：

* 当收到请求后，会交给Application进行处理，调用Application的`__call__`函数，`__call__`会调用Application的find_handler查找对应的RequestHnalder
* 调用RequestHandler的_execute处理请求，这里面就是请求的整个处理逻辑，而且也可以看到，该函数是个协程，用于高效地处理请求

### 4 Server

#### 4.1 tcpserver.TCPServer

tcpserver.TCPServer是`单线程`、`非阻塞`的TCP服务器。当需要在TCP服务器之上构建其它服务器，可以对TCPServer进行派生：

``` python
class EchoServer(TCPServer):
  async def handle_stream(self, stream, address):
      while True:
          try:
              data = await stream.read_until(b"\n")
              await stream.write(data)
          except StreamClosedError:
              break
```

如上面的EchoServer，只要定义好请求的处理函数handle_stream即可。

* listen：绑定IP地址和端口，并调用add_sockets
* add_sockets：将套接字保存起来，并添加套接字读取的回调函数(当收到请求后，会调用`tcpserver._handle_connection`)
* bind：绑定服务端口
* start：启动服务器，并且在启动时可以启动多个进程
* stop：停止服务器，主要是将对应套接字从事件循环中剔除，并关闭连接
* `_handle_connection`：处理连接的回调函数，当有客户端连接服务器时就会调用`_handle_connection`，在`_handle_connection`中会进行SSL的处理，然后调用handle_stream
* handle_stream：请求的业务处理逻辑函数，TCPServer中该函数为空

#### 4.2 httpserver.HTTPServer

HTTPServer派生自TCPServer和httputil.HTTPServerConnectionDelegate：对于TCPServer，需要定义handle_stream函数用于处理请求；对于httputil.HTTPServerConnectionDelegate，需要定义start_request和on_close。

* handle_stream 当服务端收到请求后，会实例化http1connection.HTTP1ServerConnection，然后调用该对象的start_serving方法，而在start_serving方法中，会使用HTTP1Connection类对象处理请求，因此，整个HTTP协议处理的过程就在http1connection.HTTP1Connection.read_response中
* start_request
* on_close

### 5 process

多进程模块是创建出多个进程并对这些进程进行管理：

* fork_processes 该函数有两个参数num_processes和max_restarts：当num_processes是None或者<=0时，则根据CPU核数作为进程个数；当创建出子进程后，子进程会退出当前的fork_process函数，而父进程继续执行，并监控子进程的退出，当有子进程退出时，如果是异常退出，则进行重启，在重启之前会判断当前的重启次数是否超过max_restarts
* Subprocess 

### 6 ioloop

在Tornado6.0中，ioloop.IOLoop就是对asyncio事件循环的封装

### 7 wsgi

WSGI是Web Server和Web Framework之间的通信规范：

* Web Framework提供一个可调用的对象(函数或者类对象均可)，
* Web Server调用Web Framework的对象时传递两个参数，第一个参数是包含所有HTTP请求信息的字典，第二个参数是发送响应的函数，该函数的第一个参数是响应的状态码，第二个参数是响应头
* 通过上面这种规范，就可以搭配任意的Web Server(Tornado、Gunicorn、uWSGI)和Web Framework(Django、Flask、web.py)

Tornado既可以作为Web Server，又可以作为Web Framework，而Tornado中的wsgi模块可以让Tornado称为Web Server，在其上去跑其它的业务处理框架。

这里以Django为例，先说明Django是如何给出可调用对象的，再说明如何在Tornado中执行Django框架，最后再说明Tornado如何实现WSGI：

#### 7.1 Django中的wsgi

在创建Django项目后，在settings.py层的目录中有个wsgi.py的文件，这里面重要的只有两行代码：

``` python
# Django的配置文件模块
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'first.settings')

# Django开发创建提供的可调用对象
application = get_wsgi_application()
```

#### 7.2 Tornado如何与Django对接

有了Django框架提供的可调用对象，下一步就是使用Tornado的服务器功能来运行Django：

``` python
import os
from tornado.options import options, define, parse_command_line
import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.wsgi
from django.core.wsgi import get_wsgi_application
def run(port):
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'first.settings')
    parse_command_line()
    # 获取Django的可调用对象，并用wsgi模块中的WSGIContainer封装
    wsgi_app = get_wsgi_application()
    container = tornado.wsgi.WSGIContainer(wsgi_app)

    # 将请求的路由转给web.FallbackHandler，并传递container参数
    # 而在web.FallbackHandler中，在重载的prepare方法中，调用container
    tornado_app = tornado.web.Application(
        [
            ('.*', tornado.web.FallbackHandler, dict(fallback=container)),
        ])

    server = tornado.httpserver.HTTPServer(tornado_app)
    server.listen(port)

    tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
    run(8081)
```

#### 7.3 Tornado如何实现WSGI

Tornado实现WSGI需要实现以下三个部分：

* 从请求中解析出WSGI规范要求的请求信息，并生成对应的字典
* 实现响应头部的调用函数
* 调用Web Framework的对象，传入请求字典和响应头部的调用函数，就可以得到响应体，然后对响应头部和响应体进行额外的处理就可以返回给调用方

#### 7.4 小结

下面以Tornado为Web Server，Django为Web Framework总结下整个请求处理流程：

* Tornado将实现WSGI的部分封装为wsgi.WSGIContainer类
* Tornado会为所有请求路径创建一个特殊的请求处理器FallbackHandler，并用wsgi.WSGIContainer类对象作为初始化参数
* 当Tornado收到请求后，调用FallbackHandler的prepare()方法，该方法中会调用wsgi.WSGIContainer
* 在wsgi.WSGIContainer的__call_方法中调用Django框架提供的wsgi对象，得到响应结果