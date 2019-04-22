## 以模块方式执行程序

### 1 执行方式

执行一个python程序时除了常用的`python filename.py`之外，经常还会用到`-m`选项，帮助文档中给出的含义是：

-m mod : run library module as a script (terminates option list)

以模块的方式运行python程序：`python -m filename`。python中的模块就是一个python程序，只是在进行大型程序构建时会将模块组合成包，因此再执行模块时不用加后缀。

### 2 区别

那么，`python filename.py`和`python -m filename`有什么区别呢？

它们的区别在于对`sys.path`的影响：

当以`python path/filename.py`运行程序时，会将path路径加入到sys.path中，而以`python -m path/filename`运行程序时，则会将当前路径加入到sys.path中。这样带来的影响就是：针对本地库而言，就无法进行import。

例如，当前路径是/opt，本地有个包：pkg/mod.py(完整路径就是/opt/pkg/mod.py)，以及主程序src/run.py(完整路径就是/opt/src/run.py)，那么无论使用`python src/run.py`还是`cd src/ && python run.py`，都会将/opt/src加入到sys.path中，而如果在src/run.py中导入pkg/mod.py时(import pkg)，就找不到pkg这个包，如果使用`python -m src.run`时，就会将/opt加入到sys.path中，解释器就可以找到pkg这个包。

因此，两者的区别对于本地库的导入会有影响。

另外，以模块的方式运行还有另一个用处：运行系统自带的模块。例如：`python -m http.server`就可以去已经安装的包中查找该模块并执行，如果要想用普通方式去执行，就需要去库目录中去执行：`python http/server.py`和`cd http/ && python server.py`。(上面两个都可以，因为库中的程序只会用到库中的包，而库目录一定在搜索路径中)

### 3 总结

以模块的方式运行python程序有两个好处：

* 可以将当前路径加入模块搜索路径，使得可以以目录结构访问当前本地库
* 可以运行系统自带的模块，常用的：`python -m venv test_env`和`python -m http.server`。