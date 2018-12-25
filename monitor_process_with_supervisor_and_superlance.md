## 使用supervisor和superlance监控进程

> 前言：对于运维来说，日常运维一定要做的事情是：进程监控和日志管理。本篇文章讲的就是进程监控，监控进程有两个常见的需求：自动拉起和启动通知。

### 1 部署supervisor

supervisor是一款监控进程的python程序，可以用于将同步进程转换为后台daemon程序，并对进程的执行状态进行监控。

* yum install supervisor
* pip install supervisor
* python setup.py install (从pypi上下载包进行安装)

上面的命令会安装三个工具：

* supervisord 进程监控的守护进程
* supervisorctl 客户端管理进程
* echo_supervisord_conf 生成配置文件

因此，在安装完上述三个命令后还需要启动守护进程：

```
echo_supervisord_conf > /etc/supervisord.conf
supervisord -c /etc/supervisord.conf
```

### 2 supervisor配置文件

supervisor的配置文件就是上面的/etc/supervisord.conf，它的格式是windows中常见的ini。

常见的需要关注的几个段分别是：

* unix_http_server unix套接字监听的配置
* inet_http_server http
* supervisord 守护进程的配置
* supervisorctl 客户端程序的配置
* program:theprogramname 配置进程监控的示例
* eventlistener:theeventlistenername 
* group:thegroupname 用于将多个进程监控配置成组
* include 用于包含其它的配置文件

#### 2.1 program:theprogramname配置

```
[program:theprogramname]
command=/bin/cat              ; 进程启动命令
process_name=%(program_name)s ; 进程名
numprocs=1                    ; 进程数
directory=/tmp                ; 执行启动命令的目录
;umask=022                     ; umask for process (default None)
;priority=999                  ; the relative start priority (default 999)
autostart=true                ; 当supervisord启动时启动该进程
;startsecs=1                   ; # of secs prog must stay up to be running (def. 1)
startretries=3                ; 重启次数
autorestart=unexpected        ; 自动重启
;exitcodes=0,2                 ; 'expected' exit codes used with autorestart (default 0,2)
;stopsignal=QUIT               ; signal used to kill process (default TERM)
;stopwaitsecs=10               ; max num secs to wait b4 SIGKILL (default 10)
;stopasgroup=false             ; send stop signal to the UNIX process group (default false)
;killasgroup=false             ; SIGKILL the UNIX process group (def false)
;user=chrism                   ; setuid to this UNIX account to run the program
redirect_stderr=true          ; 将出错重定向到标准输出
stdout_logfile=/a/path        ; 标准输出日志
;stdout_logfile_maxbytes=1MB   ; max # logfile bytes b4 rotation (default 50MB)
;stdout_logfile_backups=10     ; # of stdout logfile backups (0 means none, default 10)
;stdout_capture_maxbytes=1MB   ; number of bytes in 'capturemode' (default 0)
;stdout_events_enabled=false   ; emit events on stdout writes (default false)
stderr_logfile=/a/path        ; 错误日志
;stderr_logfile_maxbytes=1MB   ; max # logfile bytes b4 rotation (default 50MB)
;stderr_logfile_backups=10     ; # of stderr logfile backups (0 means none, default 10)
;stderr_capture_maxbytes=1MB   ; number of bytes in 'capturemode' (default 0)
;stderr_events_enabled=false   ; emit events on stderr writes (default false)
environment=A="1",B="2"       ; 环境变量
```

### 3 superlance

supervisor虽然可以监控进程，但是如果进程由于某种原因失败了，并且经过多次重启还是起不来，运维还是不知道，这时是有问题的，因此，当进程在重启时，也必须通知运维人员，这时就需要用到superlance。

安装superlance：`pip install superlance`

但是通过superlance与supervisor交互时只能发送email，不能只是简单地执行命令，这个后面再研究下。