## 用asyncio协程实现的网络爬虫

> 翻译自：http://aosabook.org/en/500L/a-web-crawler-with-asyncio-coroutines.html

### 1 简介

传统的计算机科学都将重点放在如何用高效的算法优化性能，但是网络应用程序通常会面临不同的挑战：

* 会保持大量慢速的连接
* 事件不频繁

网络爬虫也是这样：网络爬虫需要并发地发起大量请求，并等待响应，计算工作却很少。因此，大量的资源都消耗在保持连接上，大量的时间都消耗在网络IO上。

如果用多线程进行优化，每个线程发起请求并处理响应，但是每个连接也会占用操作系统资源，在面对大量连接的情况下，还没用完句柄时，就会耗尽内存和线程占用的资源。因此，这里使用异步IO进行优化。

下面会以三个阶段解决这个问题：

* 使用事件循环和回调：非常高效，但是难以扩展和维护
* 使用python生成器实现的协程：高效并可扩展
* 使用python的异步标准库asyncio和异步队列

### 2 任务

网络爬虫的工作方式：

* 给定一个根URL，并将根路径放入到一个待爬取队列A和获取的URL的set B
* 循环从待爬取队列A中获取一个URL，爬取该URL，解析页面的链接，如果解析到的链接不在B中，将链接也放入待爬取队列A和集合B
* 当待爬取队列中为空时结束循环

### 3 传统方法

最常见的优化方式就是使用多线程/多进程，当获取一个URL，就启动一个线程/进程爬取页面并解析，但是如果链接较多，线程/进程频繁地创建和销毁，消耗了大量资源，而且在线程/进程生存期间，它的主要耗时是在等待服务器的返回。进一步，可以使用线程池/进程池优化线程和进程的创建和销毁。

但是，用多线程时，每个线程需要系统资源(例如内存)，当线程个数达到一定数量时，系统就会崩溃，因此，系统对于线程的限制就成为了瓶颈。

另外，在每个线程中，connect()和recv()是很耗时的操作，并且默认情况下，它们是阻塞的，也就是执行结束，函数才会返回。

### 4 异步

异步IO框架的一个特点是需要使用非阻塞的函数，例如connect()：

``` python
sock = socket.socket()
sock.setblocking(False)
try:
    sock.connect(('xkcd.com', 80))
except BlockingIOError:
    pass
```

上面的代码将套接字设置为非阻塞，然后就会以非阻塞方式执行connect()函数，当连接没有建立结束时，就会抛出BlockingIOError异常，抛出该异常只是说操作还没有完成。上面的程序在处理完连接的异常后，程序就会往下执行，那么连接操作何时执行结束呢？只有当连接操作执行结束我们才能进行正常的收发数据。

为了能够处理套接字的读写，可以使用IO多路复用，linux中IO多路复用有三种方式：select、poll、epoll，用法也类似，基本就是为关心的事件设置好回调：

``` python
from selectors import DefaultSelector, EVENT_WRITE

selector = DefaultSelector()

sock = socket.socket()
sock.setblocking(False)
try:
    sock.connect(('xkcd.com', 80))
except BlockingIOError:
    pass

def connected():
    selector.unregister(sock.fileno())
    print('connected!')

selector.register(sock.fileno(), EVENT_WRITE, connected)
```

上面的代码为套接字设置连接建立成功的回调函数，同时为了处理各种事件，需要事件循环：

``` python
def loop():
    while True:
        events = selector.select()
        for event_key, event_mask in events:
            callback = event_key.data
            callback()
```

事件循环中，用无限循环包含一个select()函数，selector.select()是个阻塞函数，如果已经注册的描述符的事件发生时该函数才会返回，然后遍历发生的事件，调用对应的回调函数。基于IO多路复用技术，程序可以在单线程中并发处理多个描述符的事件。

### 5 用回调实现爬虫

``` python
import socket
from urllib.parse import urlparse

from selectors import DefaultSelector, EVENT_WRITE

selector = DefaultSelector()

class Fetcher:
    def __init__(self, url):
        self.response = b''
        self.url = url
        self.sock = None
        url_res = urlparse(self.url)
        self.host = url_res[1]
        self.port = 80
        path = url_res[2]
        if path == '':
            self.path = '/'
        else:
            self.path = path
    
    def fetch(self):
    	"""
    	发起连接请求，注册连接成功的回调函数
    	"""
        self.sock = socket.socket()
        self.sock.setblocking(False)
        try:
            self.sock.connect((self.host, self.port))
        except BlockingIOError:
            pass

        # Register next callback.
        selector.register(self.sock.fileno(),
                          EVENT_WRITE,
                          self.connected)
    
    def connected(self, key, mask):
    	"""
    	连接成功后，发起GET页面请求，注册页面接受响应回调函数
    	"""
        print('connected!')
        selector.unregister(key.fd)
        request = 'GET {} HTTP/1.0\r\nHost: {}\r\n\r\n'.format(self.path, self.host)
        self.sock.send(request.encode('ascii'))

        # Register the next callback.
        selector.register(key.fd,
                          EVENT_READ,
                          self.read_response)
    
    def read_response(self, key, mask):
    	"""
    	当描述符可读后，从描述符读取页面数据，解析页面中的链接
    	然后发起一个新的链接的请求
    	"""
        global stopped

        chunk = self.sock.recv(4096)  # 4k chunk size.
        if chunk:
            self.response += chunk
        else:
            selector.unregister(key.fd)  # Done reading.
            links = self.parse_links()

            # Python set-logic:
            for link in links.difference(seen_urls):
                urls_todo.add(link)
                Fetcher(link).fetch()  # <- New Fetcher.

            seen_urls.update(links)
            urls_todo.remove(self.url)
            if not urls_todo:
                stopped = True
    
def loop():
    while not stopped:
        events = selector.select()
        for event_key, event_mask in events:
            callback = event_key.data
            callback(event_key, event_mask)

if __name__ == "__main__":

    stopped = False
    urls_todo = set(['http://www.baidu.com/'])
    seen_urls = set(['http://www.baidu.com/'])

    fetcher = Fetcher('http://www.baidu.com/')
    fetcher.fetch()

    loop()
```

上面是用回调实现的爬虫代码，主要的逻辑还是`事件循环 + 回调函数`，而且回调函数还有嵌套：

* 发起连接请求，并注册连接成功回调函数
* 连接成功后，发起获取页面的请求，并数据到达的回调函数
* 当数据到达时，从描述符读取数据，进行解析进一步再处理

上面的代码有什么问题呢？

问题一：这里引入了一个名词：面条代码，意思是逻辑之间相互纠缠，不好理清

问题二：整个爬取逻辑不是连贯的，是被分布在几个函数中，这几个函数之间必然需要传递部分变量，此处是通过实例对象自身存储的

问题三：异常处理不好定位，如果事件循环中由于某个回调函数抛出异常，程序结束的堆栈中就只能看出是loop()函数中调用callback()失败，无法具体知道在实际函数调用中的栈帧

通常我们会比较多线程和异步的效率，还有另一个问题也值得考虑：哪一个更可能出错。多线程需要处理好线程之间的同步，异步则需要应对上面提到的问题。

### 6 协程

因此，我们想结合多线程和异步的优势：即用同步的方式写异步的代码。

协程的定义：能够停止和启动的子程序。

协程相对于线程的特点：

* 占用资源少
* 线程由操作系统调度，有抢占式的特点；协程由程序员决定是否调度，因此它们之间是协作的关系

``` python
 @asyncio.coroutine
 def fetch(self, url):
    response = yield from self.session.get(url)
    body = yield from response.read()
```

python中的协程也经历了几个过程：

* 3.3 yield from
* 3.4 asyncio
* 3.5 async/await

### 7 python中生成器的工作方式

在理解python生成器的工作方式之前，需要先理解python函数的工作方式。python函数也是通过栈帧实现的，但是跟C函数不同的是：`python函数的栈帧是在堆上分配的，而C函数的栈帧是在栈上自动分配的`。因此，当函数退出时，栈帧还是存在的，可以由解释器控制，这是能够实现函数暂停并且启动的基础。

解释器在执行python程序时会先编译为字节码，然后再执行，以下面的代码看下生成器的工作方式：

``` python
def gen_fn():
    result = yield 1
    print('result of yield: {}'.format(result))
    result2 = yield 2
    print('result of 2nd yield: {}'.format(result2))
    return 'done'
```

当解释器在编译上面的代码时，如果发现函数中有yield关键字，就会给函数设置一个标志，表明该函数是个生成器。生成器的实现主要有两个元素：生成器函数的代码以及一个栈帧，在栈帧中保存着生成器当前执行的最后一条指令的索引。就是通过该索引实现生成器的暂停和执行。

生成器有四种状态：已创建、执行、挂起、关闭。但是，我们常见的是三种状态：

* 已创建，完成生成器对象的创建，还未执行
* 挂起，生成器执行后，如果遇到yield时会停止，此时状态就是挂起
* 关闭，当调用生成器的close()函数或者生成器执行结束，状态就是关闭

当生成器创建后，必须要调用生成器的send()函数发送None预激生成器，当生成器遇到yield就会停止。当调用send(3)时，生成器启动执行，并且会将3返回给result，并继续执行到下一个yield，由于yield后面有参数2，因此，send(3)的返回值就时2。

因此，通过堆上面的栈帧以及生成器栈帧中的最后执行指令的索引来实现生成器的暂停和启动。

### 8 用生成器构建协程

本节用生成器、Future、Task、yield from实现简化版的asyncio库。这里重点就是要理解为什么会有Future和Task以及yield from的作用。

``` python
class Future:
	"""
	Future用于存放结果和回调，表示未来要等待的结果
	"""

    def __init__(self):
        self.result = None
        self._callbacks = []

    def add_done_callback(self, fn):
        self._callbacks.append(fn)

    def set_result(self, result):
        self.result = result
        for fn in self._callbacks:
            fn(self)

class Task:
	"""
	Task
	"""

    def __init__(self, coro):
        self.coro = coro
        f = Future()
        f.set_result(None)
        self.step(f)

    def step(self, future):
        try:
            next_future = self.coro.send(future.result)
        except StopIteration:
            return

        next_future.add_done_callback(self.step)

class Fetcher:
	"""
	爬虫类
	"""

	def fetch(self):
	    sock = socket.socket()
	    sock.setblocking(False)
	    try:
	        sock.connect(('xkcd.com', 80))
	    except BlockingIOError:
	        pass

	    f = Future()

	    def on_connected():
	        f.set_result(None)

	    selector.register(sock.fileno(),
	                        EVENT_WRITE,
	                        on_connected)
	    yield f
	    selector.unregister(sock.fileno())
	    print('connected!')

fetcher = Fetcher('/353/')
Task(fetcher.fetch())

loop()
```

**将生成器对象作为Task的参数后，在Task的初始化函数中创建Future对象，然后调用fetcher.fetch()生成器的send()函数进行激活，fetch()生成器执行到yield f处停止，并将f返回给next_future，并为f设置回调函数Task.step()，当连接建立完成后，执行on_connected()函数，其中在执行set_result()时会执行f的回调函数即Task.step()，fetch()生成器继续执行，然后生成器会抛出StopInteration异常，异常被Task.step()捕获，程序执行结束**

通过Task和Future可以让一个协程在需要的时候重新启动执行，使用协程时还有另一个很有用的需求，当执行某个子程序时，该子程序中包含另一个异步程序，这就需要用到yield from语句。使用该语句，可以将异步耗时的动作委托给子协程：

``` python
def gen_fn():
    result = yield 1
    print('result of yield: {}'.format(result))
    result2 = yield 2
    print('result of 2nd yield: {}'.format(result2))
    return 'done'

def caller_fn():
	gen = gen_fn()
    rv = yield from gen
```

当caller_fn()协程执行到yield from时，会等待gen协程执行结束并将gen协程的结果done返回给rv变量。

因此，基于生成器的协程的使用规则是：当要等待事件的结果时，用yield，当要等待另一个生成器的结果时，使用yield from。因此，在这里开发人员需要对等待的对象进行区分，这显然是不方便的，为了统一(只要等待一个未来完成的结果，就使用yield from)，对Future类进行改造：

``` python
def __iter__(self):
    yield self
    return self.result
```

为什么改造成上面这样，`yield f`就可以写成`yield from f`呢？yield from可以理解为用for循环对生成器进行迭代，yield from就可以理解为`for + yield + 异常处理`，因此，当使用yield from f时就相当于获取了f的迭代器。

### 9 使用asyncio库中的协程

直接上最终可以跑的用asyncio库实现的爬虫程序：

``` python
import re
import asyncio
import aiohttp
import pyquery

from urllib.parse import urlparse

from asyncio import Queue

class Crawler:
    def __init__(self, root_url, max_redirect):
        # 并发执行协程的数量
        self.max_tasks = 10
        # 连接的最大重定向次数，初始化时进行传参，本例设置为0
        # 当访问一个链接A时，将元祖(A, 10)放入队列，由于访问A时会重定向到B，
        # 于是将(B, 9)放入队列，因此max_redirect用于控制一个链接重定向的次数
        # 用于防止一个链接被重定向次数过多或者出现重定向循环？
        self.max_redirect = max_redirect

        # 多协程共享队列，协程从队列中获取url
        self.q = Queue()

        # 已经抓取和待抓取的url，防止重复抓取
        self.seen_urls = set()

        # 用于统计抓取的url数量
        self.url_cnt = 1

        # 初始化队列，此处跟直接调用self.q.put()是一样的
        # put()和put_nowait()的区别在于：
        # put()是个协程，当队列满时，应该要await放入完成时函数才实际返回
        # put_nowait()是个普通函数，当队列满时直接抛出异常，当队列有空间时，则直接放入
        self.q.put_nowait((root_url, self.max_redirect))
    
    async def crawl(self):
        """
        创建max_tasks个协程并发爬取
        """
        workers = [asyncio.Task(self.work())
                   for _ in range(self.max_tasks)]

        await self.q.join()

        # 由于work()协程是个死循环，因此，当待爬取队列为空时协程的状态就是GEN_SUSPEND
        # 当当前协程直接退出时，关闭这些暂停的任务就会报异常，调用Task.cancel()就相当于调用协程的close()
        for w in workers:
            w.cancel()
    
    async def work(self):
        while True:
            # 从队列中获取URL，队列的get()函数是个协程
            # 当队列中有元素时get()协程才会返回，否则协程会暂停
            url, max_redirect = await self.q.get()

            await self.fetch(url, max_redirect)

            # 对获取到的url完成爬取后，调用队列的task_done()
            # Queue.get()用于从队列中获取任务，Queue.task_done()则告诉队列任务已经处理完成
            # Queue.join()也是个协程，需要根据队列中未完成的任务计数器进行判断
            # 当向队列中放入元素时，_unfinished_tasks加1
            # 当从队列中获取元素并调用task_done()后，_unfinished_tasks减1
            # 当队列中有元素时，Queue.join()会阻塞，直到_unfinished_tasks为0
            self.q.task_done()
    
    async def parse_links(self, response, cur_url):
        """从爬取的网页内容中分析出链接
        1 由于读取网页内容也是比较耗时的，而且这里response.text()是个协程
        可以await读取网页内容，用pyquery分析出其中的<a>元素，然后获取元素的href
        2 通过正则表达式判断是否为合法的url，如果是合法的url，为了减少爬取的链接数，只抓取首页页面
        """
        self.url_cnt += 1
        response = await response.text()
        if not response:
            return set()
        doc = pyquery.PyQuery(response)
        ret = set()
        for link in doc('a'):
            url = link.get('href')
            if url and re.match(r'^https?:/{2}\w.+$', url):
                url_item = urlparse(url)
                ret.add(url_item.scheme + '://' + url_item.netloc)
        return ret
    
    async def fetch(self, url, max_redirect):
        """使用aiohttp抓取网页
        1 进行抓取时，aiohttp库如果遇到重定向默认会自动处理，这里由我们自己处理，因为可以对中间的链接也可以进行过滤并分析
        2 进行抓取时，要设置超时时间，而且还要对asyncio.TimeoutError异常进行处理
        3 此处通过状态码判断是否为重定向
        """
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, allow_redirects=False, timeout=10) as response:

                    if response.status in [301, 302, 307]:
                        # 如果当前爬取的url是重定向，则获取重定向的链接并且通过已知的url决定是否放入待爬取队列
                        if max_redirect > 0:
                            next_url = response.headers['location']
                            if next_url in self.seen_urls:
                                return

                            self.seen_urls.add(next_url)

                            self.q.put_nowait((next_url, max_redirect - 1))
                    else:
                        # 如果当前爬取的是正常的url，则分析出其中的链接，通过与已知链接进行对比得出需要爬取的url
                        links = await self.parse_links(response, url)
                        for link in links.difference(self.seen_urls):
                            self.q.put_nowait((link, self.max_redirect))
                        
                        # 将刚才分析出的链接放入已知链接集合中
                        # set的add和update的区别：
                        # add()会将参数作为一个整体放入集合中
                        # update()会将参数进行迭代遍历后的元素放入集合(相当于将一个集合放入另一个集合)
                        self.seen_urls.update(links)
            except asyncio.TimeoutError:
                print('crawl ', url, ' timeout')
            except Exception as e:
                print('other error occur')
            
def main():
    loop = asyncio.get_event_loop()

    crawler = Crawler('http://xkcd.com', 5)

    loop.run_until_complete(crawler.crawl())

if __name__ == "__main__":
    main()
```


### 10 总结

`pip install -i http://pypi.douban.com/simple/ --trusted-host=pypi.douban.com pyquery`

`现代程序大多都是IO密集型而非CPU密集型`。而使用python多线程会带来一些问题：GIL	的存在使得无法同时执行计算，而抢占式切换会使得需要对线程进行同步。因此，异步可以用于解决这些问题，但是基于回调的异步在代码扩展和调试方面是不够友好的。而`协程是可以用同步编码方式进行异步编程`。

yield from语句可以告诉解释器可以在哪里停止然后启动执行。python3.4引入的asyncio库，python3.5则将协程内置于语言中，并且为了与生成器进行区分，引入了`async def`和`await`，它们分别用于替代`@asyncio.coroutine`和`yield from`，并且协程装饰器会在python3.10中去掉。虽然语法有些变化，但是核心思想没有变化。
