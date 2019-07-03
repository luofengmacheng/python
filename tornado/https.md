## tornado配置https

### 1 https中的基本概念

1 对称加密和非对称加密

对称加密：加密和解密的秘钥是一样的。

非对称加密：加密和解密的秘钥不一样，分为公钥和私钥，公钥可以分给其它人使用，私钥需要保留。

2 数字签名

工作方式：

* 发送方计算要发送的数据的摘要(MD5[消息摘要]或者SHA1[安全散列])
* 发送方使用私钥对摘要进行加密，生成“数字签名”，然后将数字签名和发送的内容发送给接收方
* 接收方用发送方的公钥进行解密，将接收的内容通过同样的摘要算法生成摘要，然后与接收的数字签名进行对比，从而确认内容是从发送发发送的，而且内容未被篡改

数字签名的作用：确认公钥是从发送放发送的以及确保数据未被篡改

3 数字证书

工作方式：

* 证书中心可以对公钥进行认证
* 证书中心用证书中心的私钥对被认证机构的公钥、证书的信息进行加密，生成“数字证书”
* 发送方发送数据时，要发送内容、数字证书、数字签名
* 接收方用证书中心的公钥解开数字证书，拿到发送方的公钥，然后用公钥进行解密，对比摘要和数字签名是否一致

数字证书的作用：确保只有用可以信任的公钥解密数字证书，并保证数字证书未被篡改

4 CA证书

CA就是上面的认证中心，即证书的签发机构，通常是一些受大家信任的第三方机构，而CA证书由CA颁发的数字证书

5 证书链

下面以baidu.com使用的证书说明证书链，查看baidu.com的证书可以知道它上面还有两层证书：

* GlobalSign Root CA
* GlobalSign Organization Validation CA：用签名算法对(GlobalSign Organization Validation CA的公钥+GlobalSign Organization Validation CA的信息)进行签名，用GlobalSign Root CA的私钥对签名和签名算法进行加密
* baidu.com：用签名算法对(baidu.com的公钥+baidu.com的信息)进行签名，用GlobalSign Organization Validation CA的私钥对签名和签名算法进行加密

以上就是证书链，各级证书构成了一种`信任`关系，这种信任关系是如何建立的呢？

首先，需要明确的是，对于baidu.com的证书来说，baidu.com的公钥+baidu.com的信息是公开的，谁都可以看，而证书的功能就是保证这些信息没有被篡改，并且是来自受信任的机构签发的。

* 当客户端访问baidu.com时，客户端会收到baidu.com发来的证书
* 在证书中可以知道该证书是由GlobalSign Organization Validation CA签发的，从系统中找到GlobalSign Organization Validation CA的公钥
* 用GlobalSign Organization Validation CA的公钥对证书进行解密，提取出签名和签名算法，然后用该签名和签名算法对证书进行验证，确保数据完整且未被篡改

因此，A`信任`B的意思是，B证书的公钥可以通过通过A证书的公钥进行解密和验证。

6 根证书

针对上面的证书链，最顶部的就是根证书，多级证书之间构成了信任链。如上例，GlobalSign Root CA`信任`GlobalSign Organization Validation CA，GlobalSign Organization Validation CA`信任`baidu.com。那么，谁`信任`GlobalSign Root CA呢？

GlobalSign Root CA是根证书，操作系统会默认安装一些信任度较高的根证书，系统也会默认信任这些根证书，相当于根证书是由系统默认信任的。

小结：

* 根证书是一种特殊的CA证书
* CA证书是CA颁发的数字证书
* 数字证书：保证证书里面的公钥确实属于证书的所有者，即确认对方的身份，用于传送公钥
* 数字签名：保证数据未被篡改

### 2 https

对称加密和非对称加密有各自的特点：

* 对称机密算法公开、计算速度快、效率高
* 安全性更高、速度慢，只适合对少量数据进行加密

鉴于以上特点，https的通信过程使用了对称加密和非对称加密：

* 用非对称加密方式传输对称加密的秘钥
* 用对称加密的秘钥进行数据传输

工作方式：

* 客户端与服务端在实际传输数据之前需要进行安全握手：对服务端的身份进行验证，并沟通后续的对称加密秘钥
* 客户端发起验证服务端身份的请求，服务端将自己的`数字证书`发送给客户端
* 客户端收到服务端的数字证书后，会根据证书中的颁发机构，从系统中找到颁发机构的公钥，用该公钥对证书进行解密，验证证书的签名，如果没有问题，可以从中提取出服务端的公钥(通过这种方式，可以证明该证书确实是权威的证书授予中心颁发的，而且证书内容没有被篡改)
* 对服务端验证成功后，客户端用公钥对(对称加密秘钥、对称加密算法)加密，服务端对收到的数据进行解密，从而确定后续对称加密算法和加密秘钥
* 后续，双方就可以用协商好的对称加密算法和加密秘钥进行通信

简单总结下https的整个的流程：

* 常规的tcp三次握手
* 客户端向服务端索要公钥，服务端发送证书，客户端验证证书
* 协商对称秘钥
* 使用对称秘钥进行加密通信

### 3 关于https的三个问题

#### 3.1 http和https有啥区别?

https与http的主要的区别在于安全性上，https通过对通信过程中的数据进行加密，从而防止数据被篡改或者窃听。

#### 3.2 https解决了什么问题，怎么解决的？

* https解决数据窃听和篡改的问题
* 通信过程中使用对称秘钥对数据加密，防止数据被窃听
* 对称秘钥的协商则通过非对称加密，而非对称加密的公钥分发则通过根证书和CA证书进行
* CA证书则保证了公钥的安全性，根证书保证了CA证书是可以信任的

#### 3.3 https的握手过程

* 客户端进行验证服务端身份
* 服务端发送证书，客户端根据证书中的颁发机构，从系统中找到颁发机构的公钥，用颁发机构的公钥解密证书并验证证书未被篡改，如果验证成功，则从证书中提取出公钥
* 客户端用公钥对对称秘钥进行加密，发送给服务端，服务端用私钥进行解密，并从中获取到对称秘钥
* 服务端用对称秘钥加密数据，发送给客户端，客户端用对称秘钥进行解密，并检查数据完整性，确认没有问题，后续就可以用对称秘钥进行通信

### 4 tornado配置https

#### 4.1 生成公钥、私钥和CSR

* 生成私钥：openssl genrsa -des3 -out server.key 1024(生成1024位的RSA私钥，并用DES3进行加密)
* 去掉密码：openssl rsa -in server.key -out server.key
* 生成CSR：openssl req -new -key server.key -out server.csr(req常用于生成csr以及生成自签名证书，该语句根据私钥server.key生成CSR文件server.csr)
* 将CSR发给CA，然后CA用CSR文件和CA自身的私钥生成证书，此处生成自签名，因此signkey选项设置为server.key：openssl x509 -req -days 365 -in server.csr -signkey server.key -out server.crt(使用server.key对server.csr签发证书)
* CA将server.crt发送给申请机构

#### 4.2 tornado监听443

当申请机构有了server.key(私钥)、server.crt(证书)就可以将它们配置到SSL选项中，同时在启动服务时用443端口启动：

``` python
http_server = tornado.httpserver.HTTPServer(app, ssl_options={
	"certfile": os.path.join(os.path.abspath("."), "cert/server.crt"),
	"keyfile": os.path.join(os.path.abspath("."), "cert/server.key"),
})
tornado.options.parse_config_file("config/tornado.conf")
http_server.listen(tornado.options.options['listen_port'])
http_server.listen(tornado.options.options['ssl_listen_port'])
```

然后，在浏览器中用https进行访问，会有不安全提示，直接访问后，在网址栏前还是红色的，查看证书时，可以看到自己生成的证书，查看证书路径时，可以看到证书状态：

```
由于CA 根证书不在“受信任的根证书颁发机构”存储区中，所以它不受信任。
```

参考文章：

* [数字证书原理](https://www.cnblogs.com/JeffreySun/archive/2010/06/24/1627247.html)
