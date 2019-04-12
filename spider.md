## 网络爬虫

爬取网页分为以下几个步骤以及常用的库：

* 下载：urllib、urllib2、requests
* 分析：pyquery、beautifulsoup、lxml
* 存储：pymysql、pymongo
* 其它：scrapy(框架)、selenium(自动化)、pyredis(缓存)

### 1 下载

urllib、urllib2、requests的关系：

```
urllib.urlopen()的参数只有url，无法设置headers；而urllib2中没有urlencode()，因此，urllib和urllib2通常会一起使用。
requests的特点：
(1) 基于urllib3开发
(2) API比较人性化，方便使用
```

当选定要爬取的目标网站后，需要将页面下载下来，因此需要用HTTP客户端下载对应的页面。

``` python
class Spider(object):

    pic_dir = "movie_pic"
    store_file = "spider_result"

    def __init__(self, url):
        self.url = url

    def page_load(self, try_cnt=2):
        '''
        下载页面
        '''
        try:
            r = requests.get(self.url)
            if r.status_code >= 400:
                self.page_data= ""
                if try_cnt and 500 <= r.status_code < 600:
                    return self.page_load(url, try_cnt-1)
            else:
                self.page_data = r.content
        except expression as identifier:
            self.page_data = ""
```

### 2 分析

在下载页面之前，可以通过chrome的开发者工具查看页面的结构，确定要获取的字段和内容，在下面页面后，可以通过对应的工具库提取出所需的内容。

``` python
    def pic_load(self, url):
        pic_name = url.split("/")[-1]
        if not os.path.exists("/".join([Spider.pic_dir, pic_name])):
            pic_data = requests.get(url).content
            with open("/".join([Spider.pic_dir, pic_name]), "wb") as fd:
                fd.write(pic_data)

    def page_parse(self):
        '''
        分析页面
        '''
        doc = pyquery.PyQuery(self.page_data)
        
        result = []
        for img in doc('.item img'):
            title = img.attrib['alt']
            img_url = img.attrib['src']
            result.append({
                'title': title,
                'img_url': img_url,
            })
            self.pic_load(img_url)
        return result
```

### 3 存储

获取到所需的内容后，可以将内容存储到文件或者数据库中以便用于后续分析。

