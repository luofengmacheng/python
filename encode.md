## 编码问题

### 1 常见编码

#### 1.1 GB2312

* 当一个字节小于127时，表示的字符与ASCII一样
* 两个大于127的字节连在一起，表示一个汉字
* GB2312的另一个名字是euc-cn

#### 1.2 GBK

第一个字节大于127，就跟后面一个字节连在一起，表示一个汉字

#### 1.3 GB18030

与GBK的编码方式一致，只是字符比GBK多

#### 1.4 unicode与utf-8的关系和区别

* unicode是一种字符集，规定了字符与字节的对应关系(一个字符对应两个字节)
* utf-8是对unicode字符集进行编码的一种实现方式，其中考虑了保存时空间的节省和传输时带宽的节省
* unicode中中文是两个字节，但是，utf-8中中文是三个字节

### 2 linux系统的编码和vim的编码

当使用vim创建一个文件时，文件所使用的编码依赖于linux系统的编码。

linux系统可以用在各种语言环境下，系统中有一个命令用于查看系统所使用的`环境`:locale。它在国际化与本土化是一个很重要的概念。locale中两个变量：

* LC_ALL 强制设置
* LANG 默认设置

并且它们之间的优先级是:LC_ALL > LC_* > LANG。

例如，在我的机器上的locale的输出如下：

```
LANG=POSIX
LC_CTYPE=en_US.UTF-8   # 语言符号
LC_NUMERIC="POSIX"     # 数字
LC_TIME="POSIX"        # 时间显示格式
LC_COLLATE="POSIX"     # 比较和排序习惯
LC_MONETARY="POSIX"    # 货币单位
LC_MESSAGES="POSIX"    # 信息
LC_PAPER="POSIX"       # 默认纸张大小
LC_NAME="POSIX"        # 姓名书写方式
LC_ADDRESS="POSIX"     # 地址书写方式
LC_TELEPHONE="POSIX"   # 电话号码书写方式
LC_MEASUREMENT="POSIX" # 度量表达方式
LC_IDENTIFICATION="POSIX" # locale对自身包含信息的概述
LC_ALL=
```

由于LC_ALL为空，则配置依赖于LC_*和LANG，当某个LC_*配置为空时，则采用默认的LANG配置。

也就是说，当使用vim创建一个文件时，文件的编码是UTF-8的。

网上说，在使用vim打开文件，然后set fileencoding时，可以查看文件的编码。但是，用这种方式查看到的编码与vim本身配置的编码有很大的关系。



### 3 python中会影响编码的部分

#### 3.1 coding=utf-8

相信很多程序员在写有中文的程序时，都会在前面添加一行注释：

```python
#coding=utf-8
```

当然啦，这行注释可以有多种格式，只要里面有coding和编码就行了。那么，问题是，写这句话之后，为什么就可以在程序中使用中文了呢？

首先，需要明确的是，写这句话并不会改变源文件本身的编码(有些人说Emacs会根据这一行自动在保存时设置相应编码)。

这句话影响的只是程序在执行时，python解释器以何种编码解析程序。

