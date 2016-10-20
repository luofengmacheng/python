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

使用vim打开一个文件时，vim并不知道该文件是什么编码，而是会按照~/.vimrc中的编码配置进行探测：

```
set fileencodings=gb2312,gb18030,utf-8
```

如上所示，当用vim打开一个文件时，会按照上述顺序依次探测文件的编码，如果`探测成功`，则说明是该编码。这里所谓的`探测成功`只是说明，里面的二进制码可以在该字符编码中找到对应的字符，但是，该字符不一定是用户想要的。例如，在我自己的主机上创建一个文件，在里面输入中文`中国`，保存后，再用vim打开，里面显示的是三个乱码的字符，并且，使用set fileencoding查看编码时，给出的是gb18030。

这是因为，utf-8中`中国`两个字的编码是:e4b8,ade5,9bbd，vim在打开文件时，会按照gb2312->gb18030->utf-8的顺序进行探测，当探测到gb18030时，e4b8表示`涓`，ade5不能表示任何字符，于是系统以另一个字符代替(具体原因不明)，9bbd表示`浗`。于是，当打开该文件时，出现了可以查看的字符，但并不是用户想要的，而vim认为它找到了正确的字符编码，于是set fileencoding的结果就是gb18030。

在.vimrc中还有另外三个跟编码相关的配置：

* set fileencoding 当文件打开时，该值被设置为vi探测得到的编码，可以通过修改该值将文件保存为其它编码，同时，修改它时，也可以修改创建文件时的默认编码
* set termencoding 该配置会影响终端显示文件的编码
* set encoding vi内部使用的编码

根据上述几个编码配置，简单介绍下vi在编辑文件时对这几个配置的运用：

* 文件已经存在服务器上，它的编码是确定的
* 用vi打开文件时，会检查是否存在.vimrc，如果没有，则所有的编码配置根据locale，如果有该文件，会根据fileencodings中的编码顺序检测编码，并将检测得到的编码赋给fileencoding
* 然后，读取文件，并将读取的字节的编码转换为encoding，供vi在内部对文件进行编辑
* 当要展示给终端展示时，会将编码转换为termencoding
* 当保存文件时，会将编码转换为fileencoding，然后写入文件
* 当用本地客户端(SecureCRT)登录远程服务器时，本地客户端的编码也会影响显示：将编码转换为termencodging，然后传送到本地客户端，客户端在展示时，会用客户端设置的编码进行解码。因此，如果远程服务器的termencoding与本地的客户端编码不一致时，同样会造成乱码。
* 同时，采用本地客户端登录远程服务器的情况，还可以解释另一种乱码现象：在本地用vi打开文件乱码，而用cat打开该文件时则正常。这是因为，用vi打开文件时，会将文件编码先转成termencoding，然后在显示时再用客户端的编码进行解码；而用cat打开该文件时，是将文件的内容直接以服务器的locale编码传送到客户端，然后，显示时再用客户端的编码进行解码。因此，如果设置了错误的termencoding就会导致上面的情况。

### 3 python中会影响编码的部分

#### 3.1 coding=utf-8

相信很多程序员在写有中文的程序时，都会在前面添加一行注释：

```python
#coding=utf-8
```

当然啦，这行注释可以有多种格式，只要里面有coding和编码就行了。那么，问题是，写这句话之后，为什么就可以在程序中使用中文了呢？

首先，需要明确的是，写这句话并不会改变源文件本身的编码(一些高级的编辑器可以根据这部分而将文件保存为对应的编码格式)。

这句话影响的只是程序在执行时，python解释器以何种编码读取程序源代码。如果这里的注释的编码是utf-8，那么，python解释器在读取源代码时，会认为文件的编码是utf-8，因此，文件的实际编码应该与注释中声明的编码一致，否则python解释器在读取源代码时，会由于编码的不一致而造成乱码问题。

另外，如果不添加该行编码声明，python解释器就会认为文件的编码是ASCII，当遇到无法识别的字符时，就会失败。

#### 3.2 basestring、str、unicode

python中与字符串相关的有三个类:

* basestring 字符串的基类，声明了字符串的方法
* str 采用其它编码的字符串
* unicode 采用unicode编码的字符串

`str1 = '中国'`，这是一个str类型的字符串，在内存中使用的是定义的文件的编码；`str2 = u'中国'`，这是一个unicode类型的字符串，采用unicode编码。

下面分别看下当采用print打印中文时，会发生什么呢？

##### 3.2.1 print str

```python
str1 = '中国'
print str1
```

将两个中文赋给str1，那么str1就是有两个字符的str类型的字符串，因此，str1中保存的就是两个中文字符的utf-8字节串。

当python解释器读取源代码时，会将源代码转成unicode编码，然后由于这里是str，于是，又会根据文件指定的编码将中文进行转换并赋给str1。

##### 3.2.2 print unicode

```python
str2 = u'中国'
print str2

str3 = unicode('中国')
print str3
```

上述代码中，采用u的方式，会用文件头部注释中声明的编码将字符串转换为unicode对象；而采用unicode的构造函数创建unicode对象时，会用defaultencoding编码将字符串转换为unicode:`str3 = unicode('中国', defaultencoding = 'ascii')`，因此，第二种方式会报错。

#### 3.3 encode和decode

* encode: 将字符从unicode编码转换为其它编码
* decode: 将字符从其它编码转换为unicode编码

因此，在使用它们进行编码转换时，一定要明确原来的编码或者要转换的目的编码。

```python
s = '中国'
print s.encode('utf-8')
```

上面的代码会出现错误：

```
UnicodeDecodeError: ‘ascii’ codec can’t decode byte...
```

这是因为，s本身是str类型，它的编码是utf-8，然而，encode操作的对象是unicode编码的对象，因此，解释器就会用defaultencoding将s先解码为unicode: `s.decode(defaultencoding)`，而默认情况下，defaultencoding是ascii，于是，解释器在将s解码为unicode时失败。

#### 3.4 小结

* 保持文件的编码与头部注释声明的编码一致
* python2中尽量使用uncode，而不使用str
* 使用encode和decode进行编码转换时，必须要明确原编码和目的编码
* 当有IO时，在输入时，将字符编码转换为unicode，而输出时，将字符编码转换为其它编码。在中间进行处理时，统一使用unicode，这样能防止由于编码的不同而造成的乱码问题。

### 4 总结

* 中文环境下，尽量将locale设置为UTF-8
* 查看文件编码时，可以通过hexdump或者od等工具进行查看，不要相信vi中的set fileencoding