## python中的多线程编程

> 多线程编程中会涉及到线程的互斥和同步，分别使用了锁和信号量机制。而python的threading库中提供了多个用于处理互斥和同步的类。

### 1 线程互斥(threading.Lock和threading.RLock)

``` python
#!/usr/bin/env python
# encoding=utf8
 
import threading
 
lock = threading.Lock()
l = []
 
def test_with_lock(n):
    lock.acquire()
    l.append(n)
    print(l)
    lock.release()
 
def test(n):
    l.append(n)
    print(l)
 
def main():
    for i in range(10):
        th = threading.Thread(target=test, args=(i, ))
        th.start()

if __name__ == '__main__':
    main()
```

在上面的代码中，l对象是多个线程可以同时操作的，而在操作时会边append边print，因此，当多个线程执行时可能会出现异常：
备注：以上代码在python2中执行时会出现list打印的混乱，但是在python3中打印则是正常，应该是python3对打印做了某种优化操作。

为了将对l的访问进行原子化，在每个线程中对l的访问进行加锁，如test_with_lock()所示，该代码在python2中也可以正常执行。

threading.Lock()是一种互斥锁，也就是说同一时刻只能有一个线程访问资源，其它线程则会阻塞。

threading.RLock()是一种可重入锁，也就是说在执行了acquire()后，依然可以执行acquire()，同样地，acquire()和release()必须成对出现。该锁通常使用在以下场景：

``` python
#!/usr/bin/env python
# encoding=utf8
 
import threading
import time
import dis
 
lock = threading.RLock()
l = []
 
def func1(i):
    lock.acquire()
    func2(i)
    lock.release()
 
def func2(i):
    lock.acquire()
    l.append(i)
    print(l)
    lock.release()
 
def main():
    for i in range(10):
        th = threading.Thread(target=func1, args=(i, ))
        th.start()

if __name__ == '__main__':
    main()
```

### 2 线程同步(threading.Condition、threading.Semaphore、threading.Event)

threading.Condition 条件变量，使用场景：需要等待某个条件的发生，典型的应用场景就是[生产者消费者模型](https://github.com/luofengmacheng/python/blob/master/producer_consumer.md)。

threading.Semaphore 信号量，与互斥锁有些类似，用于限制同时访问资源的线程的数量，互斥锁可以看作是信号量的一种特殊形式。使用场景：需要限制资源同时访问的数量，例如，由于很多服务器都限制了爬虫爬取数据的频率，一种方式可以限制线程数量，另一种方式就是用信号量限制发起爬取数据请求的线程并发度。

threading.Event 事件，可以用于一对多的线程通知，一个线程给其它线程发送事件，其它线程可以等待事件的发生，然后进行相应的动作，而且该事件只有发生和不发生两种状态，使用场景：其它线程等待主线程的命令，执行对应的动作。

``` python

```

``` python
# threading.Semaphore
import threading
import time
 
def work(sem, i):
    sem.acquire()
    print("doing work in room")
    time.sleep(2)
    sem.release()
 
def main():
    # 限制最多有3个人进入房间工作
    sem = threading.Semaphore(3)
    for i in range(10):
        th = threading.Thread(target=work, args=(sem, i))
        th.start()

if __name__ == '__main__':
    main()
```

``` python
# threading.Event
import threading
import time

# 红绿灯
class light(threading.Thread):
    def __init__(self, signal):
        threading.Thread.__init__(self)
        self.signal = signal
    
    def run(self):
        while True:
            '''
            当事件设置了说明是绿灯，则清除，变成红灯
            当事件未设置说明是红灯，则设置，变成绿灯
            红灯和绿灯之间的时间间隔是3秒钟
            '''
            if self.signal.is_set():
                self.signal.clear()
                print("red light is on")
            else:
                self.signal.set()
                print("green light is on")
            time.sleep(3)

# 车
class cars(threading.Thread):
    def __init__(self, singal):
        threading.Thread.__init__(self)
        self.signal = singal
    
    def run(self):
        '''
        车要过十字路口时，检查是否是红灯(事件未设置)
        如果是红灯，则等待事件的发生
        如果是绿灯，则通过
        '''
        if not self.signal.is_set():
            print("car number {} wait".format(self.name))
            self.signal.wait()
        print("car number {} pass".format(self.name))
 
def main():
    signal = threading.Event()
    lg = light(signal)
    lg.start()
    for i in range(10):
        cr = cars(signal)
        cr.start()
        time.sleep(1)

if __name__ == '__main__':
    main()
```