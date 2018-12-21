## python简单地使用gearman

> 前言：gearman的英文字面意思是`齿轮工`，它是一款分布式任务分发的框架，当某项任务比较耗费系统资源时，可以将该任务调度到其它机器上执行，此时就是gearman大显身手的时候。

### 1 gearman部署

下载gearmand：[gearman github](https://github.com/gearman/gearmand/releases)

job svr部署：

```
yum install -y boost-devel* gperf* libevent-devel* libuuid-devel mysql-devel.x86_64

#解压gearmand并安装
./configure && make && make install

# 查看gearmand版本
gearmand --version

# 启动job svr
gearmand -d
```

client和worker库安装(python版)：

(1) pip install gearman

(2) 源码安装

下载gearman：[gearman pypi](https://pypi.org/project/gearman/)，安装即可。

### 2 架构概述

gearman分为三种角色：

* client：客户端，提交任务
* job svr：调度服务器，调度任务
* worker：作业服务器，执行任务

job svr即是上面的gearmand，client和worker所在的机器上需要安装某种语言的扩展，然后基于该扩展编写client和worker程序。

所以，这里的任务的执行方式是：client提交任务给gearmand，gearmand保存在队列中，并唤醒worker，worker获取任务并执行，将结果反馈给gearmand，gearmand再反馈给client。

关于容灾：

* worker本身是无状态的，而且可以随时添加和删除，已经是容灾模式
* client和worker可以指定多个job svr进行容灾
* gearmand中任务队列的数据是保存在内存的，将任务队列持久化就可以解决服务器宕机的问题

### 3 demo

worker

``` python
#!/usr/bin/env python

import gearman

gm_worker = gearman.GearmanWorker(['host1:4730', 'host2:4730'])

def task_reverse(gearman_worker, gearman_job):
    print 'reversing string: ' + gearman_job.data
    return gearman_job.data[::-1]

gm_worker.register_task('reverse', task_reverse)

gm_worker.work()
```

client

``` python
#!/usr/bin/env python

import gearman

def check_request_status(job_request):
    if job_request.complete:
        print "Job %s finished!  Result: %s - %s" % (job_request.job.unique, job_request.state, job_request.result)
    elif job_request.timed_out:
        print "Job %s timed out!" % job_request.unique
    elif job_request.state == JOB_UNKNOWN:
        print "Job %s connection failed!" % job_request.unique

gm_client = gearman.GearmanClient(['host1:4730', 'host2:4730'])

completed_job_request = gm_client.submit_job("reverse", "lovellluo")
check_request_status(completed_job_request)
```

先启动worker：nohup python worker.py > worker.run.log 2>&1 &

在执行client：python client.py就可以查看到结果。

另外，gearman中还有前台任务和后台任务之分：前台任务即是同步任务，客户端会等待任务执行完成；后台任务即是异步任务，提交之后，客户端无法查询到任务状态，可以在执行的任务中通过数据库或者消息队列传递结果状态。
