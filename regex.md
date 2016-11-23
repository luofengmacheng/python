## python中的正则表达式使用方法

> 前言：这里不会讲解正则表达式，而只是讲解下python中正则表达式所使用的方法。

### 1 搜索

* findall(pattern, string, flags = 0): 在string中查找匹配pattern的所有模式，并将匹配的字符串保存在数组中
* finditer(pattern, string, flags = 0): 在string中查找匹配pattern模式的所有字符串，