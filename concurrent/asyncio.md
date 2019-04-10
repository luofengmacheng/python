## python中的asyncio

### 1 定义协程

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
* 事件循环，由于协程是用户态线程，会出现很多协程并发执行，那么必然需要一个调度程序用于调度应该执行哪些协程，事件循环就有这样的用处，事件循环中会定时处理需要执行的线程，因此这里使用asyncio.get_event_loop()获取事件循环，然后将协程放入到事件循环中执行

### 2 asyncio.sleep()的实现

上面的hello world程序中使用了asyncio.sleep()函数，为什么不用time.sleep()呢？先来看下python3.5版本中asyncio.sleep()的实现：

首先，asyncio.sleep()中有yield调用，所以它不普通函数，它是给生成器。

这里重新对yield和yield from的含义做下说明：

* yield可以使当前函数暂停执行，待下一次用next()函数再调用时可以直接从上次暂停的地方开始执行。因此，调用yield时相当于创建了一个待执行的上下文并保存起来，待下次调用next()时再重新载入生成器的上下文进行执行直到再次遇到yield。
* yield from后面接生成器，当用yield from调用生成器后，当前函数就会接管子生成器的事件，当对当前生成器调用next()函数，相当于对子生成器调用next()函数，让子生成器继续执行。因此，yield from要实现的功能其实是协程可以将耗时的操作委托给另一个协程。

从上面的两个语句的含义来说，为了实现协程的功能，需要能够保存协程的队列以及事件循环，这个事件循环中会从协程队列中取出一个协程，调用该协程的next()函数，让协程继续执行。

``` python
@asyncio.coroutine
def sleep(delay, result=None, *, loop=None):
    """Coroutine that completes after a given time (in seconds)."""
    if delay == 0:
        yield
        return result

    future = futures.Future(loop=loop)
    h = future._loop.call_later(delay,
                                futures._set_result_unless_cancelled,
                                future, result)
    try:
        return (yield from future)
    finally:
        h.cancel()
```

因此，我们从yield和yield from的含义再来理解上面的代码：

当delay为0时，直接就yield，其实此时可以直接return，但是为了让它成为一个生成器，直接就调用yield，那么在下次next()时就直接退出了。当delay不为0时，就创建一个Future对象，Future是对协程的封装，它里面保存了协程的回调函数、结果等信息，从下面的yield from future也能看出来它是个协程。

### 2 asyncio用于解决什么问题

