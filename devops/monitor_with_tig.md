## 小试TIG监控方案(Telegraf+InfluxDB+Grafana)

### 1 简介

开源监控方案除了常见的ELK，还有influxData公司的TICK，由于它的前台展示还不完善，而且监控策略比较复杂，因此这里就以展示为主，不用CK，而用G(Grafana)。而且influxData公司还有个特点：后台组件是用纯go语言编写的，编译完成后的二进制程序没有任何依赖，解压后直接执行。

从上面的几个组件就可以知道监控方案包含几个部分：

* 数据采集
* 数据存储
* 监控策略分析
* 监控展示

另外后台组件会以部署、配置为主，暂不涉及到原理和架构，前台会以监控仪表盘的配置为主。并且各组件可以直接从[influxData官网](https://portal.influxdata.com/downloads/)和[grafana官网](https://grafana.com/get)下载。

### 2 数据采集：Telegraf

将Telegraf包解压后，里面的目录结构根linux一致，只有涉及到的三个部分：etc存储配置，usr存储二进制程序和启动方案，var下只有目录用于存储自身的日志。

因此，直接将该目录下的内容拷贝到根路径下即可：`tar -x telegraf-XXX.tar.gz && cd telegraf && cp -r * /`。

安装完成后，我们需要干三件事情：

1 启动telegraf进行测试，看程序是否可以正常执行：`telegraf --test`，并输出本机的一些监控指标。

2 设置服务，对于使用systemctl来说，需要将telegraf.service拷贝到/usr/lib/systemd/system/telegraf.service下，然后执行`systemctl start telegraf`。(我在测试时已经将配置文件中的influxdb配置去掉，并且只打开了file输出，执行systemctl时还是会输出`Failed to start The plugin-driven server agent for reporting metrics into InfluxDB`)

3 熟悉配置，telegraf的配置文件包含两个部分：telegraf自身的配置(agent节)以及插件的配置。

数据采集包含几个部分：输入、预处理、聚合、输出，而在telegraf中则体现为4种插件：Input Plugins、Processor Plugins、Aggregator Plugins、Output Plugins。

* Input Plugins给出需要采集的对象，例如默认配置中会采集[[inputs.cpu]]、[[inputs.disk]]等，每个部分都描述了要采集什么内容，然后在每个部分中还可以针对每个指标设置对应的属性，例如采集inputs.disk时可以忽略某些文件系统类型。
* Processor Plugins可以对采集的数据进行预处理，例如，需要将某个指标值减去一个数字。
* Aggregator Plugins对数据进行聚合，例如，可以每隔30秒对数据进行聚合一次。
* Output Plugins指定输出目的地，例如可以输出到influxDB、ES中。

本文当然还是以influxDB为存储，配置如下：

``` sh
[[outputs.influxdb]]
  ## The full HTTP or UDP URL for your InfluxDB instance.
  ##
  ## Multiple URLs can be specified for a single cluster, only ONE of the
  ## urls will be written to each interval.
  # urls = ["unix:///var/run/influxdb.sock"]
  # urls = ["udp://127.0.0.1:8086"]
  urls = ["http://127.0.0.1:8086"]

  ## The target database for metrics; will be created as needed.
  ## For UDP url endpoint database needs to be configured on server side.
  database = "telegraf"
```

### 3 数据存储：InfluxDB

InfluxDB新出了2.0的alpha版本，其中最大的变化就是主推新的FLUX查询语言，由于InfluxDB2.0还处于alpha阶段，不适合用在生产环境，因此，这里还是使用v1版本，v1版本的查询语言跟SQL差不多，所以对于使用过数据库的人操作起来比较好理解。

将InfluxDB包解压后，目录结构跟telegraf类似，直接解压，然后拷贝到根目录即可：`cp -r * /`。

然后直接启动influxd服务端程序即可，如果没有报错说明正常，并且可以另开一个终端启动influx客户端程序。

启动InfluxDB后，可以启动telegraf，然后使用influx客户端登录数据库用SQL语句进行查看进行查看：

```
influx
> show databases  # 查看数据库
> use telegraf    # 进入telegraf数据库
> show measurements  # 类似与mysql中的表，对应于telegraf中的输入插件，其中的每个列就是一个指标
> select * from cpu order by time desc limit 10 # 查看CPU的指标
```

以下是InfluxDBv2的安装过程，由于采用了新的查询语言和安全机制，使用起来比较麻烦。

将InfluxDB包解压后，里面只有两个程序：influxd和influx，其中influxd是服务端程序，influx是客户端程序，将这两个程序拷贝到/usr/bin目录下即可。

InfluxDB2.0的部署过程与1.x也由所不同，其中还增加了很多安全验证机制。

为了正常启动InfluxDB，还需要进行一些配置：

* 启动influxd，执行`influx setup`，在其中配置当前用户的用户名和密码以及`organization`、`bucket`，然后会在$USER/.influxdbv2/credentials文件中存储token。
* 用户可以通过`influx org find`查看organization，`influx bucket find`查看bucket。

然后启动influxd并在后台执行：`nohup influxd > /tmp/influxd.log 2>&1 &`。

再启动Telegraf，如果没有报错，则可以再InfluxDB中查询到数据：`influx query -o organization 'from(bucket:"my-bucket")|>range(start:-1h)'`。

### 4 数据展示：Grafana

将Grafana下载到本地进行解压后，直接执行里面的`./bin/grafana-server ./conf/defaults.ini`即可启动，默认端口是3000，然后可以在浏览器中就可以访问，默认可以登录的用户是admin，密码也是admin。登录后，就可以在里面添加数据源，这里依然使用InfluxDB。

1 添加数据源：对于InfluxDBv1只需要设置好访问的URL和数据库即可

2 添加仪表板：添加好仪表板后，可以通过添加SQL语句生成监控曲线。

Grafana提供可视化的配置方式，可以直接在页面进行填充SQL某个字段进行：

```
FROM (measurement) WHERE (多个条件)
SELECT field(指定字段) (聚合函数) 
GROUP BY time($_inerval) fill(linear)
FORMAT AS (时序还是表格，暂时不知道有啥用)
ALIAS BY (为曲线设置别名，可以体现在曲线图中)

例子：

FROM mem
SELECT field(used_percent) mean()
GROUP BY time($_interval)
FORMAT Time series
ALIAS BY 内存使用率
```

上面这个配置就会生成按照内存使用率均值的曲线，而且会生成下面这样一条SQL语句：

`SELECT mean("used_percent") FROM "mem" WHERE $timeFilter GROUP BY time($__interval) fill(linear)`

### 5 总结

本文通过对TIG三个组件进行部署和试用，在开发人力不够的时候，这些组件对于构建监控系统是很有帮助的。

* Telegraf的采集流程跟ETL类似，并且为了提高可扩展性，将各种输入、转换、输出都实现为各种插件，便于接入各种系统。
* InfluxDB是InfluxData产品中唯一一个已Influx开头的产品，是一个采用类SQL语言的时序数据库，很适合数据采集类的存储，对于熟悉关系数据的开发人员来说，易于使用。
* Grafana是一个可视化套件，在其中可以对接多种数据源，并用可视化的方式构建看板，常用于监控场景。

当然，本文只是对TIG的一个初体验，还有更多功能等待探索。