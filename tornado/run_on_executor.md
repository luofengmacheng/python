## tornado执行同步操作

### 1 从并发说起

tornado与其它框架最大的不同点在于它是非阻塞模式的，由于使用python开发，新版本的tornado使用新引入的协程代替了原来的生成器(协程)。但是，由于tornado是单线程运行，如果某个操作是阻塞的，就会导致整个服务器阻塞，那么也就谈不上高效了，因此，在tornado很重要的一点就是：所有的操作都必须是非阻塞的，如果是阻塞的操作就需要将该操作用多线程或者多进程执行，从而不影响主流程。下面就会从concurrent库、asyncio库、tornado中处理阻塞操作时使用的多线程和多进程。

### 2 concurrent.futures库中的ThreadPoolExecutor和ProcessPoolExecutor

python原本自带了多线程库(thread)和多进程库(multiprocessing)，但是由于这两个库使用比较复杂，因此，python提供了对线程池和进程池的更高一层的抽象：ThreadPoolExecutor和ProcessPoolExecutor。

ThreadPoolExecutor和ProcessPoolExecutor定义在concurrent库，它们都继承自基类Executor，只提供两个接口：submit()和map()。

submit()用于向池中提交callable去执行，返回concurrent.futures.Future，通过该对象的方法可以查看任务执行进度：例如Future.done()，Future.running()。

``` python
from concurrent.futures import ProcessPoolExecutor, as_completed

def func(data):
    return data * 2

with ProcessPoolExecutor() as executor:
    future = [executor.submit(func, "abc")]
    for f in as_completed(future):
        print(f.result())
```

上面的代码使用with语句包含ProcessPoolExecutor的对象executor，在其中提交一个任务，该任务执行一个函数，函数的参数是abc，submit()返回的是Future，由于需要获取结果，这里使用as_completed()，该函数传入可迭代对象，再使用Future的result()函数获取任务结果。

因此，submit()函数的特点是：

* 提交单个任务，返回一个Future
* 可以通过Future的方法查看任务的状态
* 如果使用as_completed()或者wait()函数获取结果，需要将Future放到数组中

map()用于向池中提交多个任务执行，并将参数放到集合中进行批量提交。

``` python
from concurrent.futures import ProcessPoolExecutor, as_completed
import traceback

def func(a, b):
    return a + b

alist = [1, 2, 3, 4, 5]
blist = [2, 3, 4, 5, 6]
with ProcessPoolExecutor() as executor:
    try:
        result = executor.map(func, alist, blist)
        for r in result:
            print(r)
    except Exception as e:
        print(traceback.format_exc())
```

上面的代码使用ProcessPoolExecutor的map()函数计算两个数组中对应位置的元素的和，返回计算结果的生成器，然后使用for循环遍历计算结果。

因此，map()函数的特点是：

* 提交多个任务，并且参数可以通过多个数组的对应位置进行输入
* 返回执行结果的生成器，于是，可以直接对返回结果进行迭代

### 3 asyncio中的run_in_executor

asyncio是个异步库，通过执行循环的run_in_executor函数可以将阻塞的操作放到池中执行。

``` python
import asyncio
import time
from concurrent.futures import ProcessPoolExecutor

executor = ProcessPoolExecutor()

def sync_func(i):
    print("before func: " + str(i))
    time.sleep(2)
    print("after func: " + str(i))
    return i

async def func(i):
    loop = asyncio.get_event_loop()
    res = await loop.run_in_executor(executor, sync_func, i)
    return res

def main():
    loop = asyncio.get_event_loop()
    tasks = [asyncio.ensure_future(func(i)) for i in range(10)]
    loop.run_until_complete(asyncio.wait(tasks))

    for t in tasks:
        print(t.result())

if __name__ == "__main__":
    main()
```

上面的sync_func()用于模拟阻塞操作，例如，requests.post()等，而在func()函数中使用loop.run_in_executor()将sync_func()放到进程池中运行，然后在main()函数中提交10个func()任务。

``` python
class BaseEventLoop(events.AbstractEventLoop):

    def run_in_executor(self, executor, func, *args):
        self._check_closed()
        if self._debug:
            self._check_callback(func, 'run_in_executor')
        if executor is None:
            # 如果没有提供池，就使用默认池
            executor = self._default_executor
            if executor is None:
                # 如果默认池也没有，则创建线程池并赋给默认池
                executor = concurrent.futures.ThreadPoolExecutor()
                self._default_executor = executor

        # 将函数放到池中运行，并返回Future对象(Future对象是Awaitable，因此，可以对run_in_executor()执行await)
        # 由于run_in_executor()使用的是submit()，它只能提交单个任务
        return futures.wrap_future(
            executor.submit(func, *args), loop=self)
```

### 4 Tornado中的run_on_executor

Tornado为了解决阻塞函数耗时长的问题，提供了装饰器函数run_on_executor()。

``` python
from concurrent.futures import ThreadPoolExecutor
from tornado.concurrent import run_on_executor

import time

class MainHandler(BaseHandler):
    executor = ThreadPoolExecutor()

    @run_on_executor
    def get(self):
        time.sleep(2)
        self.write("query ok")
```

上面的get()函数中，依然用time.sleep(2)模拟阻塞的耗时函数，由于该函数比较耗时，如果跟全局的事件循环放在一起执行，当执行get()函数时会阻塞整个流程，因此，给get()函数加上装饰器run_on_executor，同时，需要在类中定义池，这里使用线程池。因此，当收到请求后，就会直接将该get()函数丢到线程池中执行，然后主流程可以继续处理其它的请求。

``` python
def run_on_executor(*args: Any, **kwargs: Any) -> Callable:

    def run_on_executor_decorator(fn: Callable) -> Callable[..., Future]:
        executor = kwargs.get("executor", "executor")

        @functools.wraps(fn)
        def wrapper(self: Any, *args: Any, **kwargs: Any) -> Future:
            async_future = Future()  # type: Future
            conc_future = getattr(self, executor).submit(fn, self, *args, **kwargs)
            chain_future(conc_future, async_future)
            return async_future

        return wrapper

    if args and kwargs:
        raise ValueError("cannot combine positional and keyword args")
    if len(args) == 1:
        return run_on_executor_decorator(args[0])
    elif len(args) != 0:
        raise ValueError("expected 1 argument, got %d", len(args))
    return run_on_executor_decorator
```

run_on_executor()函数的核心代码就是将要执行的任务submit()到池中执行，然后返回Future对象。