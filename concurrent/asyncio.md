## python中的asyncio

### 1 asyncio的基本用法

上节讲解了yield from的用法，它的用处就是将操作委托给子生成器，待子生成器执行结束后委托生成器就可以获取到子生成器的结果。虽然表面看上次平淡无奇，但是可以这么理解：

要抓取100个网页的页面，由于网络操作是很耗时的，那么我们的程序可以将这种耗时的操作给yield出去：

``` python
def get_one_html():
	url = yield
	content = http.get(url)
	return content

def get_html(url):
	while True:
        results[url] = yield from get_one_html()

for url in url_list:
	gh = get_html(url)
	gh.send(None)
	gh.send(url)
```

get_one_html()中会调用实际的获取页面的操作，这个操作时很耗时的，在主for循环中，将数据发送给委托生成器get_html()，然后委托生成器又交给子生成器，这个时候主for循环还是继续执行，并没有阻塞着，因此，这些网页的获取操作几乎可以说是并行的。这个其实就是协程。

为了更好的支持协程，python3.4引入了asyncio模块(更确切地说是异步框架)。

#### 1.1 定义协程

``` python
import asyncio

# 用装饰器定义一个协程
@asyncio.coroutine
def hello():
    print("Hello")
    # 这里就将耗时的sleep()操作给yield出去
    # 那么当前协程的执行就不会等待asyncio.sleep()
    yield from asyncio.sleep(1)
    print(" world")

# 获取一个事件循环
loop = asyncio.get_event_loop()

# 等待事件执行结束
loop.run_until_complete(hello())
loop.close()
```

这里涉及到几方面的内容：

* 用装饰器`@asyncio.coroutine`定义一个协程，其实就是一个生成器
* 事件循环，由于系统中会有很多协程在并发执行，那么运行时环境必然要维护一个

### 2 asyncio用于解决什么问题

