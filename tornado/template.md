## tornado中的模版引擎

### 1 模版配置目录

当模版的配置目录为None(RequestHandler.get_template_path)时，会从当前路径为相对路径进行查找。可以在程序的模版配置template_path设置模版的根目录，当进行查找时可以相对该路径进行查找。

``` python
settings = dict(
	debug=True,
	template_path=ROOT_PATH + "/templates",
)
```

### 2 模版语法

模版文件的语法一般会分成两种情况：

* 直接输出元素的值或者表达式，例如：`{{ title }}`、`{{ escape(item) }}`
* 流程控制语句，可以使用常用的if、for、while、try，这些都需要在结尾加上`{% end %}`

tornado中还能使用extends和block进行模版的继承。

另外，当使用RequestHandler.render和RequestHandler.render_string时，还可以在模版文件中使用下面这些对象和函数：

* escape: tornado.escape.xhtml_escape
* xhtml_escape: tornado.escape.xhtml_escape
* url_escape: tornado.escape.url_escape
* json_encode: tornado.escape.json_encode
* squeeze: tornado.escape.squeeze
* linkify: tornado.escape.linkify
* datetime: the Python datetime module
* handler: the current RequestHandler object
* request: handler.request
* current_user: handler.current_user
* locale: handler.locale
* _: handler.locale.translate
* static_url: handler.static_url
* xsrf_form_html: handler.xsrf_form_html
* reverse_url: Application.reverse_url
* All entries from the ui_methods and ui_modules Application settings

### 3 模版的使用

前面说过，请求响应的形式有两种：write()和render()，当需要返回页面时就需要使用render()。

tornado.web.RequestHandler.render()的第一个参数是模版文件路径，后面是以键值对参数的形式将数据传递给模版文件。

当模版文件为：

``` html
<html>
	<head>
		<title>{{ title }}</title>
	</head>
	<body>
		<ul>
		{% for item in items %}
		<li>{{ escape(item) }}</li>
		{% end %}
		</ul>
	</body>
</html>
```

``` python
items = ["Item 1", "Item 2", "Item 3"]

# 直接以键值对参数传递
self.render("template.html", title="My title", items=items)

# 直接传递字典
self.render("template.html", {
	"title": "My title",
	"items": items
	})
```

### 4 总结

每个web后台框架都会有模版的概念，其实就是将页面的结构和数据进行分离，在最后返回给前端时再进行组装，因此，通过模版返回页面时只需要知道模版的文件名和模版中要装载的数据。而在python中，模版中的语法大同小异，其实就是对python中的语言结构进行了转换。