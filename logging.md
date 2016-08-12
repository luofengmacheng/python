## 日志处理

前言：
> 无论程序长短，日志模块是每个程序都会使用的，因为，日志对于定位问题起着至关重要的作用。

python中常用的日志模块是logging。它由四个部分组成：

* logger。日志的操作接口，提供日志的配置和发送操作。
* handler。指定日志的发送目的地。
* filter。指定一条日志记录是否发送到handler。
* formatter。指定日志输出的具体格式。

### 1 简单的日志处理方式

```python
import logging

logging.basicConfig('test.log', level = logging.NOTSET, filemode = 'a', format = '%(asctime)s - %(levelname)s - %(message)s')

logger = logging.getLogger()

logger.info('information')
logger.debug('debug')
logger.error('error')
```

如上所示，简单的日志处理方式至少包含以下几个步骤：

* 导入相应的日志处理库
* 对日志进行配置，包括日志的文件名，写入模式，日志格式等
* 获取日志的对象
* 写入日志记录

### 2 formatter(日志格式)

日志格式用于定义一条日志记录该记录什么内容，在设置日志格式时，可以使用以下列：

|| %(name)s || Logger的名字 ||
|| %(levelno)s || 数字形式的日志级别 ||
|| %(levelname)s || 文本形式的日志级别 ||
|| %(pathname)s || 调用日志输出函数的模块的完整路径名 ||
|| %(filename)s || 调用日志输出函数的模块的文件名 ||
|| %(module)s || 调用日志输出函数的模块名 ||
|| %(funcName)s || 调用日志输出函数的函数名 ||
|| %(lineno)d || 调用日志输出函数的语句所在的代码行 ||
|| %(created)f || 当前时间，用UNIX标准的表示时间的浮点数表示 ||
|| %(relativeCreated)d || 输出日志信息时的，自Logger创建以来的毫秒数 ||
|| %(asctime)s || 字符串形式的当前时间。默认格式是 “2003-07-08 16:49:45,896” ||
|| %(thread)d || 线程ID ||
|| %(threadName)s || 线程名 ||
|| %(process)d || 进程ID ||
|| %(message)s || 用户输出的消息 ||

### 3 handler(日志的发送方式)

handler用于指定日志的发送方式，或者叫"存储方式"，可以将日志存储到文件中，也可以发送给其它的应用程序进行处理。

常用的handler有：

* StreamHandler，将日志输出到流，默认是sys.stderr。
* FileHandler，将日志输出到文件。第一个参数指定文件名，第二个参数指定写入模式，默认是追加("a")。
* logging.handlers.RotatingFileHandler，采用轮转的方式保存日志，采用该方式可以指定轮转的日志的大小，以及最多保存多少个日志文件。
* logging.handlers.TimedRotatingFileHandler，时间轮转的方式保存日志，即多长时间则对日志进行归档，需要设置一个时间段。
* logging.handlers.SocketHandler，将日志输出到远程套接字，需要设置远程套接字的IP和端口。
* logging.handlers.SysLogHandler，将日志输出到syslog。
* logging.handlers.HTTPHandler，通过GET或POST输出到远程HTTP服务器。

下面以日志的轮转为例：

```python
rotate_handler = logging.handlers.RotatingFileHandler(filename, 'a', 100 * 1024 * 1024, 5)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
rotate_handler.setFormatter(formatter)
logger = logging.getLogger()
loggger.addHandler(rotate_handler)
```

1 创建一个轮转的日志处理器，当文件到100MB则重新创建一个日志文件，最多保存5个文件
2 创建一个日志格式对象
3 将日志格式与日志处理器关联
4 创建日志对象
5 将日志处理器应用到日志对象

从以上可以知道，handler是一种对日志发送的处理方式，一个日志对象可以关联多个处理器，也就是同时发送到多个地方，并且，可以对每个处理器分别设置日志格式、日志级别、过滤器。

```python
handler.setLevel(logging.WARNING)
handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
handler.addFilter(logging.Filter('root.child1.child2'))
```

### 4 logger(日志对象，操作接口)

logging的日志处理提供了一种`父子`结构，总的思想是：

* 子日志的配置继承父日志的配置，当然，子日志也可以重新修改配置
* 所有发送到子日志的记录都会发送给父日志

```python
logger = logging.getLogger() # 创建root logger
child1 = logging.getLogger('child1') # 创建root.child1 logger
child2 = logging.getLogger('child1.child2') # 创建root.child1.child2 logger
```

#### 4.1 默认的日志配置

当不进行任何配置打印日志时，会采用默认配置：

* formatter: %(levelname)s:%(name)s:%(message)s
* 日志级别：logging.WARNING(CTITICAL > ERROR > WARNING > INFO > DEBUG > NOTSET)
* handler: sys.stderr

修改日志的默认配置：

basicConfig(filename, filemode, format, datefmt, level, stream)

* filename: 指定默认的文件，用于生成文件处理器
* filemode: 日志的写入模式，默认是a
* format: 日志格式
* datefmt: 指定日期时间格式
* level: 日志级别
* stream: 流处理器，当设置了filename时，会忽略stream参数

#### 5 日志配置文件

当日志的配置比较灵活时，为了能够灵活的修改日志的配置，可以将日志的配置写到配置文件中。

日志的配置文件分为两大部分：模块的总定义和模块本身的定义。例如：

如果要定义三个日志，则先在loggers中定义三个日志的名字，然后在下面分别以logger_XXXX开头定义每个日志的配置。handler，formatter，filter也类似。

```
# 定义logger模块，root是父类，必需存在的，其它的是自定义
[loggers]
keys=root,infoLogger,errorLogger

# 定义handler
[handlers]
keys=infoHandler,errorHandler

# 定义格式化输出
[formatters]
keys=infoFmt,errorFmt

#--------------------------------------------------
# 实现上面定义的logger模块，必需是[logger_xxxx]这样的形式
#--------------------------------------------------
# [logger_xxxx] logger_模块名称
# level     级别，级别有DEBUG、INFO、WARNING、ERROR、CRITICAL
# handlers  处理类，可以有多个，用逗号分开
# qualname  logger名称，应用程序通过 logging.getLogger获取。对于不能获取的名称，则记录到root模块。
# propagate 是否继承父类的log信息，0:否 1:是
[logger_root]
level=INFO
handlers=errorHandler

[logger_errorLogger]
level=ERROR
handlers=errorHandler
propagate=0
qualname=errorLogger

[logger_infoLogger]
level=INFO
handlers=infoHandler
propagate=0
qualname=infoLogger

#--------------------------------------------------
# handler
#--------------------------------------------------
# [handler_xxxx]
# class handler类名
# level 日志级别
# formatter，上面定义的formatter
# args handler初始化函数参数

[handler_infoHandler]
class=StreamHandler
level=INFO
formatter=infoFmt
args=(sys.stdout,)

[formatter_infoFmt]
format=%(asctime)s %(levelname)s %(message)s
datefmt=
class=logging.Formatter
```

