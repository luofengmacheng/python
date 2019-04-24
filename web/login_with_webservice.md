## web开发中的单点登录

### 1 webservice

webservice是一种用于提供RPC功能的方式，该技术由三个部分构成：XML+SOAP+WSDL：

* XML 提供远程数据交换的格式
* SOAP 提供元素数据交换的协议
* WSDL 提供RPC远程调用的方法的描述信息

通过WSDL可以直到远程服务器提供哪些功能(服务)，通过SOAP协议与远程服务器交换数据，而在底层通过XML格式进行数据传输。

因此，webservice是一种通用的RPC技术，通过WSDL提供服务描述，通过SOAP提供数据交换协议，通过XML提供数据传输格式。

### 2 单点登录

对于很多公司来说，无论是提供外网服务还是内网服务，都会有很多个平台，例如百度，会有百度音乐、百度知道、百度百家，这些平台都是共享登录的，在其中一个平台进行登录后，直接就可以访问其他平台而无需登录，因此，单点登录最大的特点就是：共享登录态。业界比较有名的就是`CAS(Central Authentication Service)`，核心思想就是使用一个登录服务和ticket分别用于登录认证和登录签名验证。

单点登录CAS大致流程如下：

* 这里有三个角色：客户端C，平台W，统一登录系统S
* 客户端C访问平台W，平台W会通过验证cookie和session判断用户是否登录，如果登录则可以继续访问
* 如果未登录，则跳转到统一登录系统S，并给跳转链接加上登录成功跳转的URL
* 客户端C在统一登录系统S上进行登录验证，登录成功后，在认证服务器上记录下要登录的系统，然后跳转到登录前的URL，并且携带ticket
* 平台W获取ticket，调用统一登录系统S的接口验证ticket是否有效，并从解出的信息中提取用户信息，将信息写入session

其中有几个点需要注意下：

* 为什么需要将信息写入session，而在之后用session的信息进行验证，而不每次都通过统一登录系统进行验证呢？这样会不会导致多个系统间登录态不一致呢？访问认证服务器也是通过HTTP请求，如果每个系统的每个请求都要进行登录验证，那么认证服务器要承载很大的请求量，另外如果每个平台自己维护cooke和session，如果只退出某个系统确实会造成多个系统间登录态的不一致，因此，在认证服务器上进行登录后，认证服务器本身会注册登录的系统，当有用户要进行退出时会调用统一登录系统S的退出服务，然后统一登录系统S会通知其他系统退出对应的系统。
* 关于跨域：当浏览器自身要访问不同域名的服务时，浏览器会阻止。在cookie方面，每次发送请求时只会携带自身域名的cookie，如果所有的系统都在.oa.com域，那么所有的XXX.oa.com系统在访问时都会带上相应的cookie，这样确实就实现了登录态的共享。如果是不同域名的话，就只能用上面的CAS中的ticket方案。
* 统一登录系统S的验证接口通常通过webservice的方式提供服务。
* 为什么ticket就可以进行安全验证？如果某个用户用了其他用户的ticket呢？确实会有这个问题，所以网站通常都会将这个参数去掉，另外ticket验证系统自身也会保证该字符串的安全性，比如，该票据只能被验证一次，设置过期时间等。

### 3 django中如何实现登录

django中的登录通常有两种方式：login_required装饰器或者中间件。此处用中间件实现。

django本身有一套认证系统，如果要接入其他的认证机制，需要自定义验证后端，当调用authenticate()函数进行验证时会依次遍历所有的验证后端，直到验证成功或者都失败。

#### 3.1 验证后端

首先创建负责认证的app：`django-admin startapp oaauth`。在其中添加backends.py验证后端文件。

``` python
# backends.py
from django.contrib.auth.models import User
# webservice客户端库
from suds.client import Client
# 获取django的配置
from django.conf import settings


class TicketBackend:
    def authenticate(self, request, ticket=None):
        """
        验证是否是合法的ticket
        """
        if ticket:
            # 调用接口对ticket进行验证
            soap_client = Client(settings.LOGIN_WSDL)
            login_info = soap_client.service.DecryptTicket(ticket)
            if login_info:
                if 'login_info' in request.session:
                    # ticket验证通过，且session中已经有用户信息
                    # 则需要与session中的信息进行对比，如果不相同，则验证失败
                    user_name = login_info.LoginName
                    if user_name != request.session['login_info']['LoginName']:
                        return None
                else:
                    # ticket验证通过，且session没有该用户信息
                    # 则保存用户信息，表明用户登录本系统成功
                    request.session['login_info'] = login_info
                    try:
                        user = User.objects.get(username=login_info.LoginName)
                    except User.DoesNotExist:
                        user = User(username=login_info.LoginName)
                        user.save()
                    return user
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(username=user_id)
        except User.DoesNotExist:
            return None
```

然后在配置文件中配置好验证后端：

``` python
AUTHENTICATION_BACKENDS = ['apps.oaauth.backends.TicketBackend']
```

#### 3.2 中间件验证

``` python
from django.http import HttpResponseRedirect
from suds.client import Client
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth import authenticate
from django.conf import settings


class CheckAuth(MiddlewareMixin):
    def process_request(self, request):
    	# 如果是登录和退出的url则不验证
        path_list = request.path.split('/')
        if 'login' in path_list or 'logout' in path_list:
            return None

        # 获取访问的URL，去掉了参数
        url_path = '{scheme}://{host}{path}'.format(
            scheme=request.scheme,
            host=request.get_host(),
            path=request.path,
        )

        # 只要链接中携带了ticket票据，就进行验证
        ticket = request.GET.get('ticket', '')
        if ticket:
            user = authenticate(request=request, ticket=ticket)
            if user:
            	# 如果票据验证成功，为了去掉链接中的ticket参数，直接跳转到当前URL(不包含参数)
                return HttpResponseRedirect(url_path)
        else:
        	# 如果URL中没有ticket，则直接用session中的信息进行判断
            if request.session and 'login_info' in request.session:
                return None

        # 当满足以下三者时就跳转到登录链接：
        # 1 需要验证的URL
        # 2 携带了ticket，但ticket验证失败
        # 3 未携带ticket，且session中也没有信息
        response = HttpResponseRedirect(settings.LOGIN_URL + '?url=' + request.get_raw_uri())
        response['Access-Control-Allow-Origin'] = '*'
        return response
```

中间件也需要进行配置：

``` python
Middleware = [
    ...
    'middleware.auth.CheckAuth',
]
```

#### 3.3 前端展示用户信息

当用户确实已经登录了网站后，就需要在前端展示用户信息。直接向后端发起获取用户信息的请求，然后从session中获取用户信息，根据用户信息拼接邮箱或者图片链接进行展示即可。

### 4 总结

从上面可以直到，登录这块是工作量少，但是技术性强的部分，我们主要是要理解几个部分：

* webservice是一种RPC技术，在SSO登录这块主要用于验证ticket的有效性
* CAS是单点登录解决方案，主要由中央认证服务器进行统一登录验证，并生成ticket，各平台需要调用中央认证服务器提供的服务对ticket进行验证，并将用户信息缓存在session中，同时为session设置过期时间，这样不用每个请求都去请求中央认证服务器。