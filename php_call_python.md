## php调用python无结果的处理

前言：

> 有时候，一个程序的执行没有给出任何结果，这就让程序员无法定位问题，这次我就遇到这样的问题。

### 1 事件缘由

在开发某个功能时，需要在前端点击一个按钮，从而触发后台去执行一个python脚本。首先，在linux系统上编写好python代码，然后手工运行正确，然后，当前端点击按钮时，就触发执行一个php脚本，在这个php脚本中使用exec调用python脚本。但是，python没有打印任何日志信息，也就是说，根本没有执行该python脚本。

### 2 程序权限问题?

首先考虑的是程序的执行权限。手工执行python脚本时，用的是root用户，而php执行时采用的是daemon用户。于是，将用户切换成daemon，然后再手动执行，发现可以正常运行，也就说应该不是这个问题。

### 3 将执行的结果重定向到文件

```
cmd >> run.log
```

发现还是没有任何输出

### 4 将错误也重定向到文件

```
cmd > run.log 2>&1
```

终于发现了错误信息：

![](https://github.com/luofengmacheng/web_learning/blob/master/php/pics/php_call_python_error.png)

### 5 解决问题

从上图可以知道，是由于导入MySQLdb时，需要访问python eggs cache，因此，在执行程序时，可以修改默认的cache目录：

```python
import os
os.environ['PYTHON_EGG_CACHE'] = '/data/home/daemon/.python-eggs'
```

### 6 小结

开发时，大部分的时间都是在构造思路和调试程序，编写主体代码的时间是很短的，因此，最怕的就是写了一段代码，执行时，没有任何输出，这时候让开发人员无法找到问题。

此时，将程序的输出，包括错误输出都重定向到日志文件是个不错的办法。