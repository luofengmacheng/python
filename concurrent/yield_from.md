## 理解python中的yield from

### 1 yield from的基本用法

`yield from`是python3.3引入的，下面以几个例子说明yield from的作用。

例子一：

``` python
def gen1(iterable):
    yield iterable

def gen2(iterable):
    yield from iterable

g1 = gen1(range(10))
for v in g1:
    print(v)

g2 = gen2(range(10))
for v in g2:
    print(v)
```

遍历打印g1时直接打印了生成器对象，就跟直接执行`print(range(10))`的结果是一样的，直接将参数的可迭代对象给返回了，而遍历打印g2时，就跟直接遍历range(10)的结果是一样的，也就是说，这里yield from对iterable进行了解析，并返回，因此，这里的yield from可以直接替换成

``` python
# yield from
def gen2(iterable):
	for v in iterable:
		yield v
```

那么，yield from就是替换了for遍历的过程吗？请看下一个例子。

例子二：

其实yield from最大的用法就是将部分逻辑交给其他的生成器完成，下面看一个用于计算每个学生的平均成绩的代码：

``` python
results = {}

# 子生成器
# 接收成绩，并计算处平均值，并返回给委托生成器
def average():
    total = 0.0
    count = 0
    average = None
    while True:
        score = yield
        if score is None:
            break
        total += score
        count += 1
        average = total/count

    return average

# 委托生成器
# 从子生成器获取一个学生的平均成绩，并赋值给结果字典
def count_one(name):
    while True:
        results[name] = yield from average()

if __name__ == '__main__':
    # 主函数作为调用方
    # data中保存的是三个学生的成绩
    # 这里的目的是要分别计算处每个学生的平均成绩
    # 最终的结果保存在results字典中，同样以名字为键，平均成绩为值
    data = {
        'zhangsan':[80, 90, 60],
        'lisi': [50, 70, 90],
        'wangwu':[60, 30, 60],
    }

    # 针对每个学生都创建一个生成器，并传入name作为最终结果的键
    for name, score in data.items():
        co = count_one(name)
        # 发送None预激生成器，并将该学生的每门成绩发送给生成器
        co.send(None)
        for v in score:
            co.send(v)
        co.send(None)
    print(results)
```

上面的代码已经添加了解释，但是其中有两个地方还是难以理解：

第一个问题：

为什么一定要用yield from呢？average()生成器本身就可以用于计算平均值啊，为什么不能直接使用average()呢？

如果直接使用average()生成器计算平均值，需要解决的就是结果的获取，平均值计算完成后，如何返回给调用方呢？由于生成器执行结束后会抛出StopIteration异常，并将返回值放入到异常信息中，因此，可以通过处理该异常获取返回结果。下面就是直接使用average()获取某个学生的平均成绩的方法：


``` python
avg = average()
avg.send(None)
avg.send(70)
avg.send(80)
avg.send(90)
try:
    avg.send(None)
except StopIteration as e:
    print(e.value)
```

可以看到，这样的代码是很难看的，在注重代码优美的python语言中，就需要以一种优美的方式进行改写，这就催生了yield from的出现，它主要解决的就是各种异常的处理。

第二个问题：

中间的count_one()委托生成器为什么一定要加while True呢？

如果在委托生成器中不加while True，当最后一次发送结束信号send(None)时就会抛出StopIteration异常。这里就涉及到yield from对于调用方的send()方法的处理：

``` python
# 这里节选了yield from实现的对于收到值的处理逻辑
# _s 委托生成器从主调用方获取到的值
# _i 子生成器
try:
	if _s is None:
		_y = next(_i)
    else:
        _y = _i.send(_s)
except StopIteration as _e:
    _r = _e.value
    break
```

* 当调用方发送None时，委托生成器就会调用子生成器的next()
* 当调用方发送非None数据时，委托生成器就会调用子生成器的send()函数将数据转发给子生成器

因此，当最后调用avg.send(None)时，就会调用子生成器的next()，此时子生成器的yield会返回None，子生成器就会退出，并抛出StopIteration，并将子生成器的返回值赋给_r，最后执行break，yield from执行结束，并将_r赋值给RESULT并返回，results完成赋值后，就会退出委托生成器，此时就会抛出StopIteration。如果加上while True循环，就会执行到下一次循环，此时委托生成器的状态还是GEN_SUSPENDED。

因此，给委托生成器加上while True循环，目的就是不让委托生成器结束，避免处理委托生成器的异常。

其实，从上面的分析也可以看出yield本身的一些特点：

* 对生成器执行next()函数，如果生成器的状态是GEN_CREATED，则启动执行生成器中的代码，将yield后面的变量值返回(如果没有变量则返回None)，并暂停；如果生成器的状态是GEN_SUSPENDED，则从生成器暂停处开始执行，直到下一个yield。
* 对生成器执行send()函数发送数据，如果生成器的状态是GEN_CREATED，则启动执行生成器中的代码，将yield后面的变量值返回(如果没有变量则返回None)，并暂停；如果生成器的状态是GEN_SUSPENDED，则yield就会返回接收到的值，并继续执行，直到下一次yield。

所以，i.send(None)和next(i)在大部分场景上功能是相同的，唯一不同的是，使用next(i)时，生成器i无法收到值，因此，这里yield from的实现中要区分发送数据是否是None分别处理需要进一步考证。

### 2 yield from的使用场景

从上面的讲解可以知道，yield from的主要功能是封装子生成器的功能，并在底层处理了各种异常保证了上层代码的优美。因此，简单总结下yield from的使用场景：

* yield from可以用于对可迭代对象进行迭代并分别yield
* yield from可以用于委托操作给子生成器，对多个元素执行子生成器中的操作