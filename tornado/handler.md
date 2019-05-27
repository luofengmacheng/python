## tornado请求处理器

### 1 获取参数

1 获取get参数

get参数通过RequestHandler的`get_query_argument()`方法获取，例如：

``` python
class GoodsHandler(tornado.web.RequestHandler):
    def get(self):
        # 获取url中的查询参数name，如果没有该参数就返回空字符串
        name = self.get_query_argument("name", "")
        self.write(name)
```

2 获取post参数

``` python
class GoodsHandler(tornado.web.RequestHandler):
    def post(self):
        name = self.get_body_argument("name", "")
        self.write("name=" + name)
```

3 获取url中的参数(可以用于实现RESTful)

这种方式需要url进行配合，在将url绑定到handler时进行配置

4 获取body中的参数(json)

方法一：

``` python
class GoodsHandler(tornado.web.RequestHandler):
    def post(self, id):
        data = str(self.request.body, encoding='utf-8')
        data = json.loads(data)
        self.write("name=" + data["name"])
```

方法二：

``` python
class GoodsHandler(tornado.web.RequestHandler):
    def prepare(self):
        if self.request.headers.get("Content-Type", "").startswith("application/json"):
            self.json_args = json.loads(self.request.body)
        else:
            self.json_args = None
```

### 2 RequestHandler的执行流程以及对部分方法的重载

tornado.web.RequestHandler是tornado中用于处理用户请求的类，开发人员通常会创建处理请求的基类BaseHandler，该类继承自RequestHandler，然后在BaseHandler的基础上再创建处理业务逻辑的类。

而在一次请求过程中，会按照以下流程执行，并且用户可以对这些方法进行重载：

* initialize() 子类初始化函数，可以从urlconf中传递参数，通常用于初始化对象成员
* prepare() 每次执行实际的操作前都会执行的动作，通常会在基类BaseHandler中进行重写，例如上面将请求中的json数据提取出来变成对象成员
* get()、post()、put()、delete()
* on_finish() 当请求结束时会执行该函数

另外，还有两个比较用户的方法可以重载：

* write_error() 如果在处理业务逻辑过程中出错，则会调用write_error()返回错误信息或者返回一个页面
* get_current_user() 用于获取当前登录的用户信息
* set_default_headers() 设置响应的默认的头部

### 3 重定向

tornado中进行重定向有两种方式：RequestHandler.redirect和RedirectHandler。

可以直接在RequestHandler中使用redirect()进行重定向，该方法有一个可选参数permanent，该参数默认为False，它会影响重定向的行为：如果该参数为False，会返回302重定向；如果该参数为True，会返回301 Moved Permanently。

RedirectHandler可以用于直接在url配置中配置重定向：

``` python
app = tornado.web.Application([
	url(r"/app", tornado.web.RedirectHandler,
	dict(url="http://www.baidu.com")),
])
```

与RequestHandler.redirect不同的是，RedirectHandler默认是301，因为这种配置在运行时是不会改变的。

### 4 请求响应

后端执行业务逻辑处理后，通常有两种返回数据的方式：

* render() 返回页面
* write() 返回数据，而且当数据是字典时，会编码为json字符串，因此，如果是编写api，就可以使用write()

### 5 总结

本节重点讲了tornado用于处理业务逻辑时的输入和输出，以及RequestHandler的部分重载函数。