## 使用timeit和cProfile做python的benchmark

### 0 前言

在开始python并发编程之前，先来看下python内置的两个用于测量执行时间的库的一些用法，后面会使用这两个工具进行对比分析。

### 1 timeit基本用法

timeit是python的内置模块，它能够给出程序运行的时间，其中最常用的是两个方法：

``` python
def test_func():
    for i in range(1000):
        pass

if __name__ == "__main__":
    # 返回执行100次test_func()函数时的时间
    print(timeit.timeit(test_func, number=100))
    # 将上述过程执行3次，返回一个数组，其中包含执行每次执行的时间
    print(timeit.repeat(test_func, repeat=3, number=100))
```

这两个方法还有给参数setup，它可以作为执行test()的准备工作，并不计算它的时间。

### 2 cProfile基本用法

``` python
# test.py
import time

def test_func():
    for i in range(1000):
        pass

def test_func2():
    time.sleep(2)

test_func()
test_func2()
```

以模块的方式调用以上方法：`python -m cProfile test.py`

![cProfile结果](https://github.com/luofengmacheng/python/blob/master/concurrent/pics/benchmark_cprofile.png)

下面简单介绍下几个字段的含义：

* ncalls 被调用了几次
* tottime 总共执行的时间
* percall 每次执行的时间 = tottime / ncalls
* cumtime 累计时间
* percall 总共的每次执行的时间 = cumtime / ncalls
* filename:lineno(function) 表示被分析的函数在文件中的行号

另外，也可以加上`-s tottime`选项进行排序，可以只关心耗时较长的部分。

### 3 如何用timeit和cProfile的结果衡量python程序的性能

在进行程序的性能测试或者对比测试时，第一个关注点就是时间，如果A程序执行某个操作需要5秒，而B程序执行同一个操作只需要2秒，那么从表象上看肯定B程序性能高。另外如果A程序执行时间较长，那么就可以进一步使用cProfile分析哪些调用的耗时较长。