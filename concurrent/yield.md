## python中的yield

### 1 yield基本使用方法

python中带有yield的函数就是一个生成器，生成器最常用的用法就是懒加载地返回用户需要的数据，例如python2中有range()和xrange()，它们的区别就是range()会生成一个数组，每次从其中返回一个元素，而xrange()是一个生成器，只有当用户需要一个元素时才从其中计算出下一个元素返回给用户：

``` python
def user_range(x):
    i = 0
    while i < x:
        yield i
        i += 1

if __name__ == "__main__":
    print(user_range(5))
    for i in user_range(5):
        print(i)
```

从它的输出中就可以看出user_range()是一个生成器，生成器用于多次返回数据给用户，但是只有在用户需要数据时才去计算，例如，如果是从一个数组中获取下一个值，那么需要将数组全部加载到内存，然后再去遍历，而对于生成器，当用户需要数据时才去计算，不需要将所有数据载入内存。

因此，使用生成器的主要好处就是：节省内存空间。

但是，yield还有另一种用法，除了可以从生成器中获取数据，我们也可以向生成器发送数据，生成器接收到数据进行处理后，我们可以直接获取结果：

``` python
from inspect import getgeneratorstate

def work():
    num = 0
    res = 0
    while True:
        num = yield res
        print("receive: ", num)
        res += num
        print("ready to send result: ", res)

if __name__ == "__main__":
    w = work()
    print(getgeneratorstate(w))
    w.send(None)
    # next(w)
    # w.__next__()
    print(getgeneratorstate(w))
    print('receive result: ', w.send(1))
    print('receive result: ', w.send(2))
    print('receive result: ', w.send(3))
    print(getgeneratorstate(w))
    w.close()
    print(getgeneratorstate(w))
```

在上面的例子中，我们使用inspect包中的getgeneratorstate()函数获取生成器的状态，从上面可以知道生成器至少有三种状态：

* GEN_CREATED 已创建，完成生成器的状态，还未开始执行
* GEN_SUSPENDED 已挂起，当生成器执行到yield处停止时状态就是挂起
* GEN_CLOSED 已关闭，当执行生成器的close()函数，生成器的状态就会变成关闭

除了上述三种状态，生成器都在执行过程中，因此，生成器还有第四种状态：GEN_RUNNING。

这里我们需要注意两个地方：

* 创建一个生成器后，生成器的状态还是GEN_CREATED，此时生成器未执行到yield处，不能向生成器发送数据，必须要执行w.send(None)或者w.__next__()或者next(w)预激生成器，让生成器的状态转变为GEN_SUSPENDED，然后才能向生成器发送数据
* 需要理解`num = yield res`，这句的意思是生成器返回res，并进入到GEN_SUSPENDED，当调用send()向生成器发送数据时，生成器收到数据，将数据返回给num，生成器的状态就切换为GEN_RUNNING，然后执行下面的计算逻辑，当执行完成后，会重新调用yield，此时会将上次计算好的值返回给用户，然后再次进入GEN_SUSPENDED。

### 2 yield使用场景(用于解决什么问题)

因此，从上面的例子可以看到，yield就像是一个额外的线程，我们可以向线程发送数据，然后线程计算完成后会将结果发送给用户，用户可以获取到返回的结果，这种执行方式很类似线程，而且每次执行时也需要将上下文切换为当前的执行环境，由于执行环境的切换是在用户态完成，因此，也将生成器理解为协程。

我们也可以得出yield的使用场景：

* 用户需要多次获取结果，并且每次的结果可以根据之前的结果计算而来
* 将计算逻辑可以独立于用户逻辑
