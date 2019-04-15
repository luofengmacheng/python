## python中的asyncio基础

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

并等待协程执行结束* 用装饰器`@asyncio.coroutine`定义一个协程
* 事件循环，由于协程相当于用户态线程，那么那么我们在创建一个协程后该如何执行这个协程呢？因为会出现很多协程并发执行，那么必然需要一个调度程序用于调度应该执行哪些协程，事件循环可以理解为一个无限循环，定时处理需要执行的线程，因此这里使用asyncio.get_event_loop()获取事件循环，然后将协程放入到事件循环中执行并等待协程执行结束，因此，run_until_complete()是个阻塞函数，只有当协程执行完了，才会执行下面的loop.close()。

### 2 asyncio.sleep()的实现

上面的hello world程序中使用了asyncio.sleep()函数，为什么不用time.sleep()呢？先来看下python3.5版本中asyncio.sleep()的实现：

首先，asyncio.sleep()中有yield调用，所以它不普通函数，它是个生成器。

这里重新对yield和yield from的含义做下说明：

* yield可以使当前函数暂停执行，待下一次用next()函数调用生成器时可以直接从上次暂停的地方开始执行。因此，调用yield时相当于创建了一个待执行的上下文并保存起来，待下次调用next()时再重新载入生成器的上下文进行执行直到再次遇到yield。
* yield from后面接生成器，当用yield from调用生成器后，当前函数就会接管子生成器的事件，当对当前生成器调用next()函数，相当于对子生成器调用next()函数，让子生成器继续执行。因此，yield from要实现的功能其实是，协程可以将耗时的操作委托给另一个协程。

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

当delay为0时，直接就yield，其实此时可以直接return，但是为了让它成为一个生成器，直接就调用yield，那么在下次next()时就直接退出了。当delay不为0时，就创建一个Future对象，Future是对协程的封装，它里面保存了协程的回调函数、结果等信息，从下面的yield from future也能看出来它是个协程，当创建好Future对象后，就为这个协程设置延迟执行，然后用yield from future返回，此时，函数会立即返回，但是这里其实是将该协程放入到事件循环，等待下一次轮询，如果下一次轮询时时间到了，该函数才会真正的执行结束，然后就会执行hello()协程的下一个打印语句。

以往我们在使用这种异步编程模式时，都是使用回调实现，也就是设置好一个函数执行结束后，应该执行什么动作，比较有典型的就是前端的jquery和nodejs，由于网络请求是很耗时的，因此，在编写代码时就需要为网络IO设置好回调，当网络IO完成后，浏览器自动执行回调，但是这样编写的代码有几个问题：

* 回调模式不同于常规的顺序执行的代码，多个异步函数之间是并行执行的，直观上不好理解
* 如果多个动作之间有依赖，即A执行结束后需要执行B，执行B结束后需要执行C，代码会非常难看

而asyncio中异步编码方式跟同步一样，当执行到耗时的操作时，可以告诉解释器，该行语句可以立即返回，等到该操作真的完成时再继续执行。

### 3 async/await

上面在定义协程和等待协程结束使用的是`@asyncio.coroutine`和`yield from`，为了更好地区分生成器和协程，python3.5引入了async和await，它们的含义分别与前两个类似，而且基于生成器的老式协程会在python3.10中移除，因此，后面还是用新式的协程。上面的hello world的例子可以写成：

``` python
async def hello():
    print("Hello")
    # 这里就将耗时的sleep()操作给yield出去
    # 那么当前协程的执行就不会等待asyncio.sleep()
    await asyncio.sleep(1)
    print(" world")

# 获取一个事件循环
loop = asyncio.get_event_loop()

# 等待事件执行结束
loop.run_until_complete(hello())
loop.close()
```

用async def定义一个协程，协程就可以丢进事件循环中执行，而且在协程中有一个sleep()的函数，由于asyncio.sleep()是一个协程，而且是一个耗时操作，因此，需要用await立即返回当前协程，当asyncio.sleep()中的时间结束后就可以立即执行下面的print()函数。

### 4 如何执行一个协程

python中提供了三种方式执行协程：

* asyncio.run()，如上面的hello world例子：asyncio.run(hello())
* await，等待另一个协程执行结束，当前协程才会继续执行
* asyncio.create_task()

### 5 任务和Future

python中await后面可以使用协程、任务和Future对象，它们都是可以异步执行的，只有当等待的对象执行结束才会执行await后面的语句。

#### 5.1 Future

Future主要用于获取异步的结果，常用方法是result()，用于返回一个Future的结果。

``` python
import asyncio

async def world():
    await asyncio.sleep(1)
    return "world"

async def hello():
    print("Hello")
    await asyncio.sleep(1)

    future1 = asyncio.ensure_future(world())

    res1 = await future1

    future2 = asyncio.ensure_future(world())

    res2 = await future2

    return res1 + ' ' + res2

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(hello())

    loop.run_until_complete(future)
    print(future.result())
```

#### 5.2 Task 任务

Task是Future的子类，用法跟Future类似，都可以对协程进行封装，并且返回结果。

``` python
import asyncio

async def world():
    await asyncio.sleep(1)
    return "world"

async def hello():
    print("Hello")

    task = asyncio.create_task(world())

    return await task

async def main():
    task = asyncio.create_task(world())
    print(task)

    res = await task
    print(res)

if __name__ == "__main__":
    asyncio.run(main())
```



