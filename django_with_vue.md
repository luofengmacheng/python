## vue+django搭建web开发环境

### 1 部署django开发环境

#### 1.1 升级python

安装python3会遇到3个问题：

* 编译时报错：`ModuleNotFoundError: No module named '_ctypes'`，这是由于缺少包libffi-devel，安装该包即可：`yum install -y libffi-devel`。
* 安装完成后执行pip3报ssl出错，需要更新openssl：http://blog.51cto.com/13544424/2149473
* 安装完成后需要修改默认的python：`ln -s /usr/local/bin/python3 /usr/bin/python`，而yum使用的是python2，因此执行yum命令时会报语法错误，可以修改/usr/bin/yum中的python的路径。

#### 1.2 安装django

为了保持开发环境的独立(特别是多人共用一台开发机时)，在安装django之前，需要安装virtualenv，并创建独立的python环境：

```
pip3 install virtualenv
virtualenv mysite_proj
```

进入独立的python环境，安装django：

```
pip3 install Django
python -m django --version
```

#### 1.3 demo部署

初学django时要初步了解的内容：

* 目录结构规范
* urls路由方式
* settings配置
* 静态文件配置
* ORM
* 模版渲染
* MVC

##### 1.3.1 目录结构规范

安装好django后，就可以使用自带的命令创建项目：

```
django-admin startproject mysite
```

创建好项目后，会存在一个项目的目录和一个manage.py文件，manage.py可以用于启动一个测试环境的web服务器：

```
python manage.py runserver 0:8080
```

为了在其它机器上可以访问，需要设置项目目录下的settings.py中的ALLOWED_HOSTS变量：

``` python
# 该变量用于保护服务器免收攻击，正式环境不建议使用*，而是使用前端服务器的域名/IP
ALLOWED_HOSTS = ['*']
```

就这样，基于django的后台框架运行起来了，接下来就需要在项目中创建各种应用，搭建更加复杂的系统。

使用django-admin命令创建的项目的目录结构非常简单，为了以后能够更好地扩展，就需要规划好目录结构，以下是一些最佳实践：

* 在项目中添加requirements.txt，使得系统迁移部署时可以快速安装依赖，如果系统在不同的环境下需要安装不同的包，可以针对不同的环境创建不同的依赖文件
* 为了管理项目中的应用，在项目的目录(mysite/mysite)下创建apps目录用于存放项目的所有应用

项目的目录结构如下：

```
project_name/
        manage.py
        project_name/
                __init__.py
                settings.py
                urls.py
                wsgi.py

        apps/
                app1/
                app2/
        static/
                css/
                js/
                images/
        templates/
```

应用的目录结构如下：

```
app_name/
        __init__.py
        admin.py
        apps.py
        migrations/
        models.py
        tests.py
        views.py

        urls.py
        models/
        views/
        static/
                css/
                js/
                images/
        templates/
```

##### 1.3.2 urls路由方式

urls路由其实相当于MVC中的控制器，将请求路由到处理逻辑。

根据上面对项目结构的说明，项目是由若干个app以及其它的配置组成，因此，针对一个url而言，首先会路由到项目的urls.py，然后urls.py再路由到app的urls.py，而app的urls.py则会到具体的处理函数。

项目的urls.py：

``` python
from django.urls import path

urlpatterns = [
    path('app1/', include('app1.urls'))
]
```

应用的urls.py：

``` python
from django.urls import path

urlpatterns = [
    path('index', views.news.index)
]
```

##### 1.3.3 settings配置

settings配置中，除了上面提到的ALLOWED_HOSTS，下面提到的DATABASES，还需要注意的有三个配置：

* INSTALLED_APPS 项目要使用的app都需要在这里配置，例如在apps目录下创建了app1应用，可以在该配置中添加apps/app1，该配置的一个用处是数据库的迁移migrate，当执行`python manage.py migrate`时，会为INSTALLED_APPS中的应用创建表结构
* LANGUAGE_CODE/TIME_ZONE 当要使用中文时，可以设置`LANGUAGE_CODE = 'zh-Hans'`，同时将时区设置为上海`TIME_ZONE = 'Asia/Shanghai'`
* STATIC_URL 静态文件配置见1.3.4

##### 1.3.4 静态文件配置

下面分开发环境和正式环境分别进行静态文件的设置。

开发环境下：

根据范围可以将静态文件分成两种：项目级别和应用级别。

django默认的搜索路径是：先在STATICFILES_DIRS中搜索，然后在应用的static目录中搜索。因此，在开发时设置STATICFILES_DIRS变量即可：

``` python
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]
```

生产环境下的静态文件交给nginx或者apache。

##### 1.3.5 ORM

django中的模型主要是通过ORM操作实现的，要想使用ORM，需要先创建好数据库，然后进行相应的配置。

python中数据库相关的库主要有MySQLdb和pymysql，由于MySQLdb不支持python3，因此这里使用pymysql。

```
# 安装pymysql库
pip3 install pymysql
```

配置mysql：

``` python
DATABASES = {
     'default': {
         'ENGINE': 'django.db.backends.mysql', #数据库引擎
         'NAME': 'mysite',                     #数据库名
         'USER': 'root',                       #用户名
         'PASSWORD': 'root',                   #密码
         'HOST': 'localhost',                  #数据库主机，默认为localhost
         'PORT': '3306',                       #数据库端口，MySQL默认为3306
     }
 }
```

然后在项目的__init__.py中添加如下代码即可：

``` python
import pymysql
pymysql.install_as_MySQLdb()
```

使用django ORM的好处：

* 业务逻辑只与django的API与数据库交互，切换数据库是很方便的
* 通过定义模型，django可以自动生成表结构，在系统迁移时可以方便地创建数据库

##### 1.3.6 模版渲染

为了分离页面和数据，当需要返回页面时需要使用模版引擎进行渲染。

模版的配置是通过配置文件中的TEMPLATES变量实现的，里面有两个配置需要关注：

* DIRS 
* APP_DIRS 将该变量设置为True后，就会在INSTALLED_APPS目录中查找templates子目录

因此，使用模版时需要在每个应用中创建templates目录，这里要注意的是，由于DjangoTemplates在查找模版时，是直接从所有的templates中查找，如果直接将模版文件放在templates目录中，由于不同的应用有可能使用相同的模版名(这是非常有可能的)，就可能造成查找到错误的同名模版，因此，在放置模版文件时，在templates目录下创建与应用同名的目录，然后把应用的模版放置在该目录中，即应用的模版放到APP_NAME/templates/APP_NAME中。

django的模版引擎的语法与jinja2类似，模版渲染需要注意三个方面：

* 模版文件的语法，这个可以在使用中再去搜索
* 在view中获取数据后，通过render()将数据载入到模版中返回给前端
* 模版文件中还要将链接变量化，其中包含静态文件和动态链接，分别使用`static`和`url`实现

##### 1.3.7 MVC

django也是一个MVC模式的框架，控制器通过urls实现，模型通过ORM实现，于是大部分的逻辑都在视图中：控制器将请求转发给视图，视图通过调用模型处理请求，然后确认是否要通过模版渲染返回页面还是直接返回数据。

### 2 部署vue开发环境(vue+yarn+webpack)

安装开发工具：

* nodejs
* yarn(包管理器，类似于npm、yum等)

关于前端构建工具：构建工具就是为了简化我们日常的机械重复的事情。

用户从浏览器中看到的网站只有HTML+JS+CSS，但是开发人员在开发时可以用其它不同的语言，例如，可以用Less开发CSS，用Jade开发HTML，那么在开发完成后就需要将这些文件编译成浏览器可以识别的HTML+JS+CSS，而且在生成这些文件的同时也会进行压缩合并，完成这项任务的就是前端构建工具。

下面正式开始进行开发环境的搭建吧!!!

安装好nodejs和yarn后，在全局环境安装vue-cli：

``` shell
yarn global add vue-cli
```

然后就可以查看vue的版本号：

``` shell
vue -V
```

安装好了vue-cli，接下来就是创建工程，创建的方式可以参看vue-cli中的README.md，具体有三种方式：

* vue init <template-name> <project-name> 该命令会从github上vue的官方模版中下载
* vue init username/repo <project-name> 该命令会从github上下载对应的仓库中的模版
* vue init ~/fs/path/to-custom-template <project-name> 该命令会使用本地的模版

由于网络策略限制，用vue下载模版时不能连接到github，又没有找到配置代理的方式，因此，这里使用本地的模版：

从[github](https://github.com/vuejs-templates/webpack)上下载模版，并放到本地的D:\www\vue_demo目录下，然后解压就会得到目录D:\www\vue_demo\webpack-develop，然后执行init命令即可(初始化命令执行过程中需要确认各种配置，一路enter就行)：

``` shell
vue init D:\www\vue_demo\webpack-develop vue_test
```

然后进入vue_test目录执行npm就可以启动项目：

``` shell
cd vue_test
npm install
npm run dev
```

接下来就可以看到以下文字：

```
DONE Compiled successfully in 4208ms

Your application is running here: http://localhost:8080
```

然后在浏览器中打开http://localhost:8080，就可以看到vue的欢迎界面，开始vue之旅吧。

### 3 使用vue进行基本的前端开发

这里使用vscode进行开发，在开始开发之前，还需要安装几个插件：

* eslint
* prettier-Code formatter
* vetur

然后进行以下配置：

``` javascript
{
  "editor.fontSize": 18,
  "workbench.editor.enablePreview": false, //打开文件不覆盖
  "search.followSymlinks": false, //关闭rg.exe进程
  "editor.minimap.enabled": false, //关闭快速预览
  "files.autoSave": "onFocusChange", //打开自动保存
  "editor.lineNumbers": "on", //开启行数提示
  "editor.quickSuggestions": {
    //开启自动显示建议
    "other": true,
    "comments": true,
    "strings": true
  },
  "editor.tabSize": 2, //制表符符号eslint
  "editor.formatOnSave": true, //每次保存自动格式化
  "eslint.autoFixOnSave": true, // 每次保存的时候将代码按eslint格式进行修复
  "prettier.eslintIntegration": true, //让prettier使用eslint的代码格式进行校验
  "prettier.semi": false, //去掉代码结尾的分号
  "prettier.singleQuote": false, //使用带引号替代双引号
  "javascript.format.insertSpaceBeforeFunctionParenthesis": true, //让函数(名)和后面的括号之间加个空格
  "vetur.format.defaultFormatter.html": "js-beautify-html", //格式化.vue中html
  "vetur.format.defaultFormatter.js": "vscode-typescript", //让vue中的js按编辑器自带的ts格式进行格式化
  "vetur.format.defaultFormatterOptions": {
    "js-beautify-html": {
      "wrap_attributes": "force-aligned" //属性强制折行对齐
    }
  },
  "eslint.validate": [
    //开启对.vue文件中错误的检查
    "javascript",
    "javascriptreact",
    {
      "language": "html",
      "autoFix": true
    },
    {
      "language": "vue",
      "autoFix": true
    }
  ],
  "editor.wordWrap": "on",
}
```

此时，只要ctl+s保存文件就可以进行格式化了，而且格式化后的代码可以通过eslint的检查。

进行前端开发需要安装ui库，这里使用element-ui。

```
npm i element-ui -S
```

#### 3.1 首页导航及路由配置

开发一个网站，最开始需要完成的就是网站的首页导航结构。

网站的首页打开的是index.html，可以在里面修改网站的title。

然后剩下的就是4个比较重要的内容：

* main.js 入口文件，在里面加载需要用到的组件，例如，上面在安装element-ui后，需要在main.js中导入该组件：

``` javascript
import ElementUI from 'element-ui'
import 'element-ui/lib/theme-chalk/index.css'

Vue.use(ElementUI)
```

* App.vue 在vue中，每个vue文件都是一个页面模版，其中包含该页面的所有内容，而App.vue就是整个网站的顶级组件
* router/index.js 在其中可以进行路由配置，定义路由和组件的关联关系
* components/ 组件目录，为了模块化管理整个网站，将整个网站分割成了很多个组件，每个组件就是一个模块，一个模块中包含若干个vue文件

了解了上述内容后，就开始进行网站导航的实现。

安装好element-ui后，可以到element-ui官网查看导航的代码，在components/Home.vue中用el-menu添加侧边栏菜单：

``` html
<template>
  <el-container id="app">
    <el-aside width="200px" style="background-color: rgb(238, 241, 246)">
      <el-menu router default-active="schema_config" theme="dark">
        <el-menu-item>自动化容灾演练平台</el-menu-item>
        <el-menu-item index="schema_config">演练方案</el-menu-item>
        <el-menu-item index="history">演练记录</el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <router-view></router-view>
    </el-container>
  </el-container>
</template>
```

上述代码中与el相关的可以到element-ui官网查看，这里主要关注的是router-view。在开发导航菜单时，经常需要实现的是点击某个菜单时，只有其中的展示数据的区域的页面切换，菜单是不变化的，而且通过这种方式，也可以将整个网站组成一个有层级关系的架构，而router-view就是用来实现这个功能的。当用户点击演练方案这个菜单时，就会打开/schema_config路由，根据路由配置找到需要渲染的组件，然后会将组件渲染在router-view中，从而实现点击不同菜单就可以打开不同页面。

通过上面的方式就可以实现一个导航菜单，剩下一个问题就是路由配置。

初始的webpack框架中路由是写在router/index.js中的，但是当页面很多路由比较复杂时就需要按照模块分开放置每个模块的路由：

例如，登录的路由配置如下：

router/auth.js
``` javascript
import Login from '@/components/auth/Login'
import Logout from '@/components/auth/Logout'

export default [
  {
    path: 'auth',
    name: 'auth',
    children: [{
      path: 'login',
      component: Login
    }, {
      path: 'logout',
      component: Logout
    }
    ]
  }
]
```

然后将该路由配置整合到总路由配置中：

router/routerConfig.js
``` javascript
import authRoutes from './auth'

var routes = []
routes = routes.concat(authRoutes)

export default routes
```

最后，将该路由配置

router/index.js
``` javascript
import Vue from 'vue'
import VueRouter from 'vue-router'
import home from '@/components/Home'
import routerConfig from './routerConfig'

Vue.use(VueRouter)

export default new VueRouter({
  mode: 'history',
  routes: [{
    path: '/',
    component: home,
    children: routerConfig
  }]
})
```

#### 3.2 表单操作

表单和表格是最常用的需要与后台交互的组件，关于前端的方式不再赘述，可以参看element-ui官网，当前台页面搞好后，剩下的就是如何与后台交互进行数据的填充。


#### 3.3 表格操作

### 4 前后端分离和前后端调用

