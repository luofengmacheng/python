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


