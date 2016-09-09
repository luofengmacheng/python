## 日志的继承对日志级别的影响以及使用logging模块的注意要点

### 1 前言

python中的logging日志处理模块提供了一种层级结构的日志，由于这种层次关系，当要打印不同的级别的日志时，会产生与用户想法不同的结果。

### 2 一个小例子

```python
import logging

log = logging.getLogger(__name__)
fh = logging.FileHandler('test.log')
fh.setLevel(logging.DEBUG)
log.addHandler(fh)

def make_log():
    log.debug('debug')
    log.info('info')
    log.warn('warn')
    log.error('error')
    log.critical('critical')

make_log()
```

以上代码打印的日志中会有如下内容(这里只给出消息内容)：

```
warn
error
critical
```

按照日志的高低级别(CTITICAL > ERROR > WARNING > INFO > DEBUG > NOTSET)，这里首先为文件处理器设置了日志级别为DEBUG，然而在日志文件中只能看到WARN及以上级别的日志。

然后再做另一个实验：

在make_log()函数定义的前面添加log.setLevel(logging.DEBUG)

以上代码打印的日志中会有如下内容(这里只给出消息内容)：

```
debug
info
warn
error
critical
```

难道为handler设置level没用，只有为log设置level才行吗？

### 3 源码分析

python的logging模块中的__init__.py代码：

```python
# Logger类的error方法
def error(self, msg, *args, **kwargs):
    if self.isEnabledFor(ERROR):
        self._log(ERROR, msg, args, **kwargs)
```

其中当参数提供的日志级别大于getEffectiveLevel()的返回值时，isEnabledFor()返回True:

```python
def getEffectiveLevel(self):
	"""
	Get the effective level for this logger.

	Loop through this logger and its parents in the logger hierarchy,
	looking for a non-zero logging level. Return the first one found.
	"""
	logger = self
	while logger:
	if logger.level:
	return logger.level
	logger = logger.parent
	return NOTSET
```

通过英文解释可以知道，该方法遍历当前日志到root日志，直到找到一个设置了日志级别的logger(logger.level为真也即logger.level!=logging.NOTSET，而NOTSET正是默认设置的日志级别)，然后返回该日志级别。由于root logger的默认级别是WARN，因此，如果不修改root logger的日志级别，该函数是不可能返回NOTSET的。

现在，让我们回过头来看下本文开始的代码：

```python
log = logging.getLogger(__name__)
fh = logging.FileHandler('test.log')
fh.setLevel(logging.DEBUG)
log.addHandler(fh)
```

我们只是为文件处理器设置了日志级别，那么，log的日志级别就是NOTSET，由于这里getLogger()函数是带参数的，它就是root logger的孩子日志，在打印日志时，首先查看日志的日志级别(NOSET)，那么就查看父日志(root)的日志级别(WARN)，于是，getEffectiveLevel()返回WARN，因此，在打印日志时，就是打印WARN及以上级别的日志。

从Logger.error()方法可以知道，打印日志时，会先检测log本身及父日志的级别，然后再遍历该日志的所有handler，如果允许打印(打印的日志级别比handler的大)，则输出到日志。

### 4 对日志级别的小结

* 日志的级别可以应用在日志上，也可以应用到handler上。
* 打印日志时，会从当前日志到root logger上的所有日志中找到一个设置了日志级别的级别，只有大于该级别，才考虑是否输出到日志。
* 输出时，会遍历该日志绑定的所有handler，检查是否可以输出。
* 因此，在一个日志对象上是否可以输出该信息，首先依赖于该日志对象的日志级别及祖先的日志级别，然后则依赖于handler的日志级别。

### 5 使用logging模块的几点建议

* logging日志模块是分层级的，不要每个模块都用getLogger()，而应该使用getLogger(__name__)。
* 根据上面所说，在设置日志级别时，只要设置handler日志级别，然后修改root logger的日志级别，就可以很灵活的配置各个handler的日志级别(既然有多个处理器，肯定希望每个处理器的日志级别都不一样)。
* 为了可以很灵活地配置各个handler，也可以将配置写到配置文件中。