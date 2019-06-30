## tornado中操作cookie和session以及登录的实现

### 1 cookie

cookie是服务端在客户端存储的数据，用于对客户端的身份进行标识。cookie常用的有4个字段：

* cookie的键
* cookie的值
* 域名
* 超时时间

tornado中，cookie的相关操作定义在web.RequestHandler中，上面的4部分分别对应了web.RequestHandler.set_cookie()的前4个参数：name，value，domain，expires。

另外，torando还提供了set_secure_cookie()，该函数会使用cookie_secret配置对值进行加密，而获取cookie时就必须使用get_secure_cookie()

### 2 session

session是在服务端存储的数据，session通常会结合cookie一起使用：

cookie中只存储ID，当访问时，服务端从cookie中获取ID，根据ID从session中获取用户信息，从而对客户端身份进行验证。

tornado中没有提供对session的操作，可以通过pycket库完成，并将session数据存储到redis中。

### 3 tornado中关于登录的部分

在登录验证领域，单点登录是最常用的登录方式。

单点登录的流程：

* 统一认证中心通过webservice的方式发布登录方法
* 当用户访问网站时，检查session中是否有用户的信息，如果没有，则认为当前用户没有登录，则跳转到统一认证中心提供的登录页面，并在跳转时加上访问的url
* 当用户在统一认证中心的登录页面进行登录时，会重新跳转到之前访问的页面，并且会在url中添加ticket票据，用该ticket票据调用统一认证中心的验证方法进行验证，如果验证成功，则将用户信息存储到session中，并重定向到当前访问页面，目的是去掉链接中的ticket票据

通常，上述流程可以成为web中的验证模块。

而在tornado中，与登录相关的有三个部分：

* get_current_user：该方法在web.RequestHandler中，用于返回当前登录用户，开发人员通常都会对web.RequestHandler.get_current_user()进行重载，例如，上述的单点登录流程就可以写成单独的模块并放到get_current_user()进行调用
* authenticated和login_url：web.authenticated是个装饰器，它的逻辑是：如果未获取到当前用户信息(get_current_user)，则获取配置好的login_url，并将当前访问的url追加到login_url后面用于之后跳转到登录前的页面，因此，login_url中需要处理next查询参数

### 4 XSS(跨站脚本攻击)和XSRF(跨站请求伪造)

XSS(跨站脚本攻击)：在页面插入恶意代码，当用户浏览页面时执行恶意代码用户获取用户信息、会话劫持等攻击。通常插入而已代码的方式：前台的表单，

防御思想：用户提交数据时，对数据进行严格验证；展示数据时，对展示的数据进行HTML编码。

tornado中对XSS的的预防方式：

tornado框架对数据展示进行了处理，将代码转成字符串，但是业务代码还是需要对数据进行严格验证。

CSRF(跨站请求伪造)：浏览恶意网站时，恶意网站获取用户信息，以用户的名义对其它网站执行恶意操作。

防御思想：当客户端发起请求时，服务端随机生成一个token，并将该token放到cookie中，同时在页面的提交的表单中也有该token值的字段，当提交表单时，会验证cookie中的值与表单中提交的值是否一致，从而判断该请求是否是从当前网站页面发起。

tornado中对XSRF的防御分为两步：

* 设置xsrf_cookies为True
* 在表单中添加`{% module xsrf_from_html() %}`