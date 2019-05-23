## tornado基础知识

### 1 web后台框架需要熟悉的内容

* 开发环境搭建
* 目录结构规范
* 配置文件
* 路由配置和管理
* ORM(SQLAlchemy)
* 部署

* webservice
* RESTful

### 2 开发环境搭建

1 创建虚拟开发环境：由于最新的tornado只支持python3，而且python3自带虚拟环境。因此，在安装好python3后，执行`python -m venv tornado_dev`创建虚拟开发环境。

2 在虚拟环境中执行`pip install tornado`安装tornado库。

3 使用豆瓣源安装：`pip install -i http://pypi.douban.com/simple/ --trusted-host=pypi.douban.com tornado`

### 3 目录结构规范

proj_root/
	config/ ---- 存放配置文件
	handlers/ ---- 路由映射
	models/ ---- 模型，与数据库交互
	libs/ ---- 库文件，做一些封装
	requirements.txt ---- 依赖的库文件
	server.py ---- 启动文件

### 4 配置文件

web后台包含的配置包括：

* 数据库
* 日志
* 常量(项目根路径、调试模式)

### 5 路由配置和管理

在server.py中创建tornado.web.Application的子类，并配置好路径和处理器的对应关系。

``` python
class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", MainHandler),
        ]
        settings = dict(
            debug=True,
        )
        super(Application, self).__init__(handlers, **settings)
```

### 6 ORM(SQLAlchemy)

### 7 部署

谈到tornado的部署就要谈到它与django和flask的区别了。

django和flask只是开发框架，提供了一种方式可以让我们方便的编写业务代码，django的优点是自带管理台后端，而且集成了web框架的几乎所有的功能，flask的优点在于小巧，用户可以在需要的时候再使用自己想要的功能，而且它也自称是微框架。

而tornado与它们的两者的很大的区别就是：torando不仅是开发框架，而且是web服务器。因此再部署时，django和flask需要另外再部署web服务器，而tornado则不需要，因此，它们的常见的部署方式是：

```
uWSGI/gunicorn -> django/flask
tornado
```

但是由于nginx的高性能，有反向代理的功能，并且提供负载均衡，对于静态文件的性能很高，因此它们的部署方式就变成了：

```
nginx -> uWSGI/gunicorn -> django/flask
nginx -> tornado
```

因此，部署tornado包含tornado自身的部署和nginx中的配置。

tornado自身的部署有两种方式：以守护进程启动；以前台进程启动并且用监控软件管理。如果以守护进程启动：`nohup python server.py > /tmp/server.log 2>/tmp/server.error &`，需要自己写监控程序。如果以前台进程启动，可以在docker中启动或者是使用类似supervisor等进程进行监控。

部署完tornado，就需要在nginx中将路由导向tornado，根据开发方式又有所区别：

* 如果不是前后端分离的方式，也就是使用tornado自身的模板系统，就可以将其中的静态文件，例如js、css等，单独放在一个目录，然后在nginx中分成两个路由，分别导向静态文件和动态文件。
* 如果是前后端分离的方式，tornado只提供api，前端负责调用api，前台编译构建完成后会得到一个首页index.html和一个static目录(其中包含js和css)，这种方式的好处就是自动将静态目录给独立出来，此时就需要在nginx中配置两个URL：

方式一：将默认路径路由到静态目录，后台访问的URL路由到tornado

```
# 所有的路径都导入到静态目录
location / {
    root /data/www/dist;
}

# 后端api请求就给到tornado进程处理
location /api/ {
    proxy_pass http://localhost:8000;
}
```

方式二：将默认路径路由到

```
# 指定静态文件路由
# ^~ 表示如果匹配到了这条路由则不继续匹配
location ^~ /static/ {
    # 在location中的路径尽量使用alias，而不用root
    # 例如，如果这里使用root，就要设置路径/data/www/dist/
    # 但是这样不好理解，而且如果实际的最终路径名不是static就要通过软链接来实现了
    alias /data/www/dist/static/;

    # 告诉客户端缓存时间长度，通常针对静态资源设置
    expires 24h;
}

# 根路径可以匹配任何路由，因此一个网站对于除了静态资源以外的资源都可以匹配根路径
# 
location / {
    index index.html

    proxy_pass_header Server;

    proxy_set_header Host $http_host;

    proxy_redirect off;

    proxy_set_header X-Real-IP $remote_addr;

    # 把请求方向代理传给tornado服务器，负载均衡

    proxy_pass http://tornados;

}
```

### 8 nginx中部分配置

#### 8.1 日志格式

```
log_format main    '$status|$scheme://$http_host|$remote_addr|$upstream_addr|nginxProxy|$uri|$time_local|$request_time|$http_Tencent_LeakScan|$arg_offer_id|url="$r
equest",body="$request_body"|s=$bytes_sent|"$http_user_agent"';
```

#### 8.2 日志按月分割

```
access_log      /usr/local/nginx/logs/access-$year$month.log  main;

if ($time_iso8601 ~ "^(\d{4})-(\d{2})-(\d{2})") {
    set $year $1;
    set $month $2;
}
```

#### 8.3 关于index指令

当访问的URL以`/`结尾时，就会访问匹配的路由中index指令后的文件，如果找到了其中的某个文件，就会发起内部重定向。

如下例子，后端是php，管理进程是php-fpm，如果访问`http://localhost`时，路径就是`/`，此时就会匹配第一条路由，发现index.php存在，就会内部重定向到`http://localhost/index.php`，此时就会匹配第二条路由，就会访问到后端的默认控制器。

```
location / {
    index index.php index.html;
}
location ~ .*\.php {
    fastcgi_index     index.php;
    fastcgi_pass      127.0.0.1:9000;
    fastcgi_connect_timeout 300;
    fastcgi_send_timeout 300;
    fastcgi_read_timeout    300;
    fastcgi_split_path_info ^((?U).+.php)(/?.+)$;
    fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
    fastcgi_param PATH_INFO $fastcgi_path_info;
    fastcgi_param PATH_TRANSLATED $document_root$fastcgi_path_info;
    include           fastcgi.conf;

    gzip on;
}
```