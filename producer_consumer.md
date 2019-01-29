## 任务流程系统设计以及其中的生产者和消费者模式应用

### 1 任务流程系统

运营系统中，任务流程系统的设计是个绕不开的部分，现在我们都在讲`智能化`、`AIOps`，但是如果系统连`自动化`水平都达不到，实在不敢妄想一步就达到智能化水平。而在自动化阶段，最常见的思路就是先脚本化，然后用任务流程系统将脚本串联封装成用户需要的功能，那么，当用户需要执行某个功能时，就交给任务流程系统执行相应的流程，以此来达到初级水平的`自动化`。

#### 1.1 定时扫表轮询

用户提交一个任务后，将该任务写入库表，前台可以直接返回，提高用户的体验。后台的svr程序定时从库表中获取任务，按照预先定义的子任务关系(每个任务包含若干个子任务，这些子任务之间也包含一定的先后顺序或者并行关系)分解出初始子任务，并将子任务写入到库表中，并且每个任务和子任务都会带上状态字段和结果字段(状态字段表明该任务是否执行结束，结果字段表明该任务是否执行成功)，该svr的工作流程如下：

```
1 扫描任务表，如果有未开始执行的任务，则分解出初始子任务，并写入库表
2 扫描子任务表
    如果有未开始执行的子任务，则根据子任务ID找到子任务信息，与提交的参数一起执行该子任务
    如果有已经执行的子任务，则查看该子任务是否执行结束
        如果该子任务已经执行结束，则更新子任务状态，并解析出下一个子任务，写入库表
```

架构上就是这样：

![定时扫表实现任务流程系统](https://github.com/luofengmacheng/python/blob/master/pics/task_flow_db.png)

从上面的流程可以看出，该方式最大的优点就是实现简单，当然，缺点也很明显，在扫描表时，一定会加limit(如果不加limit，可能会由于任务持续增加，导致早就结束的任务不能更新状态)，那么可能会由于任务的增加，导致后面提交的任务等待时间增加，任务执行效率会急剧降低。

#### 1.2 任务分发(celery vs gearman)

通过上面的分析，知道了扫描方式的缺点在于：

* 定时扫表，浪费查询资源
* 当任务量很大时，扫表会导致后面提交的任务等待时间很长，体验很差，也会使得整个系统效率急剧降低

此时就需要用到分布式任务框架：celery和gearman。

celery和gearman都可以实现类似任务分发的功能：提交任务给组件，组件会将任务交付给后台的worker执行。

但是从使用上有点小的区别：

```
1 两者都可以实现同步任务和异步任务，celery对于异步任务可以返回任务ID，后期可以用任务ID查询任务的状态和结果，而gearman提交异步任务后无法返回任务ID，任务状态的修改就只能依靠worker自己上报
2 gearman是用C语言实现的，但是请求的发起和处理可以用任何语言编写；celery是用python语言实现的，请求的发起可以用任何语言，但是请求的处理需要用python语言编写
```

至于其它的区别，只能在以后使用过程中再细细对比了。

### 2 gearman

这里给出简单的用gearman实现任务处理的系统架构：

![gearman实现任务流程系统](https://github.com/luofengmacheng/python/blob/master/pics/task_process_with_gearman.jpg)

用户在web前台提交任务后，会把任务的相关信息和参数传送给web后台，web后台对请求的数据进行封装，发送给gearmand守护程序，gearmand程序收到请求后，会交给job server执行，同时为了提高系统的效率，在每个worker上又可以用多线程的方式执行任务，那么整个系统相当于有3*n个线程在执行任务，而且job server是可以横向扩展的，相当于有无限的处理能力。

通过以上方式gearman解决了多机之间任务分发的问题，但同时，每个job server又有多个线程处理任务，因此，这里又产生了多线程同时去竞争job server的任务的问题，也就是生产者和消费者模式。

### 3 生产者和消费者模式(包含任务队列)

生产者和消费者模式是操作系统课程中最常讲的关于进程互斥和同步的例子：生产者生产消息，将消息放入到队列，消费者取出队列中的消息进行消费，对于队列而言，由于是多个进程都可以访问的共享资源，在访问时需要加锁，这是进程的互斥，而对于整个消息的产生和消费而言，只有队列有空间时才允许生产者生产消息，只有队列不空时才允许消费者消费消息，这是进程的同步。

下面就以python中实现简单的生产者和消费者模式：

``` python
import threading
import random
import queue

# 队列，用于生产者和消费者之间的缓冲
que = queue.Queue(10)

class Producer(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
    
    def run(self):
        global que
        while True:
            data = random.randint(100, 999)
            que.put(data)
            print("producer send data: {}".format(data))

class Consumer(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
    
    def run(self):
        global que
        while True:
            data = que.get()
            print("consumer receive data: {}".format(data))

p = Producer()
c = Consumer()
p.start()
c.start()
```

上面用两个线程分别模拟了生产者和消费者：

* 这里的队列用的是标准库的queue，该队列是线程安全的，在多个线程进行操作时可以保证不会出现并发访问的问题，因此，在访问队列时没有加锁
* 向队列中放入数据和从队列中获取数据用的是队列自身的操作，这两个操作默认是阻塞的：get()时如果没有数据，则等待；put()时如果没有空间，则等待。
该操作会使得该线程直接阻塞，但是该线程还是在执行中，这个也会浪费计算资源

为了解决上面的第二个问题，当队列中没有数据时，发起get()操作时需要使得线程休眠。此时，需要使用到条件变量进行线程同步。

``` python
import threading
import time
import random
import queue

# 条件变量
con = threading.Condition()
que = queue.Queue(10)

class Producer(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
    
    def run(self):
        global que
        global con
        while True:
            data = random.randint(100, 999)
            que.put(data)

            con.acquire()
            con.notify()
            con.release()
            print("producer send data: {}".format(data))

class Consumer(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
    
    def run(self):
        global que
        global con
        while True:
            con.acquire()
            con.wait()
            con.release()
            while True:
                try:
                    # 采用非阻塞方式从队列中取出数据
                    # 如果队列为空，则抛出Empty异常
                    data = que.get(False)
                    print("consumer receive data: {}".format(data))
                    time.sleep(1)
                    que.task_done()
                except queue.Empty as exp:
                    break
                except Exception as exp:
                    print("exception: {}".format(str(exp)))
                    break
```

这里使用了线程的Condition条件变量对生产者和消费者进行线程同步：当生产者生成数据后，会给等待该条件的线程发送消息；消费者采用非阻塞的方式从队列中取出数据，如果队列中有数据，则直接取出，当消费完数据后，给队列一个完成的标记(queue.task_done()，也可以不加，但是如果要旁路用join()判断队列是否为空时则必须要加)，如果队列中没有数据，则抛出Empty异常，跳出内层的while循环，于是会执行wait()等待条件的发生。通过这种方式，当消费者线程无法获取数据时，线程会休眠，避免计算资源的浪费。

### 4 gearman中worker的生产者和消费者模式

上文中提到，当单个worker收到任务后，可以用多个线程处理任务，提高系统的吞吐量，这里会提到另外两个词：任务队列和线程池。

worker在收到任务后，可以将任务放到任务队列中，worker会管理由多个线程组成的线程池，每个线程会都会尝试从任务队列中获取任务，然后进行处理，因此，虽然worker名义上是处理任务的工作者线程，也可以在该进程中用生产者和消费者模式最大化系统的处理性能。

### 5 小结

本文从任务流程系统出发，介绍了任务流程系统实现的常见的两种方式以及它们的优缺点，然后介绍了celery和gearman，针对gearman，给出了分布式任务处理的架构，同时为了提高系统的处理性能，在worker进程中使用了生产者和消费者模式。

因此，celery和gearman此种任务分发框架用于处理多机之间的任务分发，而在单机上使用生产者和消费者模式来提高处理性能。