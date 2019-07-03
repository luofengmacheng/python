## 将python2升级到python3

### 1 前言

本文介绍将python2升级到python3过程中的部分问题的解决。

### 2 ssl模块的问题

有时候在安装好python3后，执行pip3时会出现以下错误信息：

```
Retrying (Retry(total=4, connect=None, read=None, redirect=None, status=None)) after connection broken by 'SSLError("Can't connect to HTTPS URL because the SSL module is not available.",)'
```

这是由于安装过程中ssl模块编译失败所致，一般是由于openssl未安装或者版本过低引起的。

* 到openssl官网下载包进行安装
* 下载python的安装包，进行解压后，去掉其中的Modules/Setup.dist中的ssl的注释
* 对python进行编译：`./configure --with-openssl=/usr/local/ssl`

详细安装步骤如下：

* yum update
* yum install -y lrzsz gcc libffi-devel openssl-devel
* cd openssl-1.1.1c &&  ./config --prefix=/usr/local/openssl && make && make install
* 编辑Python安装包中的Modules/Setup.dist，去掉ssl的注释
* cd Python-3.7.2 && ./configure && make && make install