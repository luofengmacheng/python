## python中的wsgi和uWSGI的关系

### 1 什么是wsgi

首先，wsgi是一种规范，类似HTTP、fastcgi等。它的全称是Python Web Server Gateway Interface，是一种用于Web Server和Web App之间交互的协议。

为什么会有wsgi呢？先从处理web请求的流程开始说起，当用户在浏览器中发起一个请求后，请求会交给web服务器进行处理，但是由于后端技术的发展以及语言的迭代更新，开发人员会希望用新的语言和新的框架进行web后台开发，但是web服务器如何与我们的框架进行交互呢？早期(如apache)采用加载模块的方式或者CGI的方式，部署时需要安装该语言的一个扩展模块，灵活性不足。为了解耦web服务器和web框架，使得web服务器和web框架之间可以随意组合，就为web服务器和web框架之间加上了wsgi这样一种协议，只要双方分别实现wsgi协议，就可以正常地进行交互。

### 2 什么是uWSGI

uWSGI是一个web服务器，用于连接管理和进程管理，实际的业务处理逻辑则交给Web App。因此，在配置uWSGI时需要配置好Web App的一个程序，该程序返回一个可调用对象(例如django中项目的wsgi.py)。以Web App的角度来看，自身只是处理业务逻辑，但是主要解决的问题就是输入和输出，因此uWSGI与Web APP交互时其实就时调用Web APP的一个程序，将上下文环境和数据传给App，并提供一个回调函数用于返回数据给uWSGI。

### 3 为什么还需要nginx

其实，从上面的讲解，可以知道在Web领域有很多这种架构：

```
uWSGI/gunicorn -> Django/Flask
php-fpm -> CI(CodeIgniter)/Laravel
tomcat/apache -> spring
```

部署好Web Server和Web App后，我们用浏览器或者curl就可以直接访问页面了，那么为什么还需要nginx这个东西呢？

虽然上面的Web服务器也可以处理静态文件，但是由于nginx自身的设计和架构，使得它在连接管理、负载均衡、静态文件访问方面比上面的Web服务器好很多，因此，目前的Web架构都是会在Web Server前面添加nginx用于反向代理，主要目的就是解决负载均衡和静态资源访问的问题。

### 4 小结

从上面的讲解可以看出，Web服务业是一个分层的结构：

* nginx负责连接管理、负载均衡和静态资源访问
* Web Server负责进程管理，接收用户请求并调用Web App处理业务逻辑
* Web App只负责具体的业务逻辑，根据请求的参数访问数据库进行处理返回结果即可