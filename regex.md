## python中的正则表达式使用方法

> 前言：这里不会讲解正则表达式，而只是讲解下python中正则表达式所使用的方法。

### 1 搜索

* findall(pattern, string, flags = 0): 在string中查找匹配pattern的所有模式，并将匹配的字符串保存在数组中
* finditer(pattern, string, flags = 0): 在string中查找匹配pattern模式的所有字符串，并返回match对象(只返回第一次匹配的结果)
* match(pattern, string, flags): 在string中查找匹配pattern模式的所有字符串，并返回match对象(只返回从开头匹配的结果)
* search(pattern, string, flags): 在string中查找匹配pattern模式的字符串，并返回match对象(只返回第一次匹配的结果)

### 2 分割

* split(pattern, string, maxsplit, flags): 用pattern模式对string进行分割，返回分割后的列表

### 3 替换

* sub(pattern, repl, string, count, flags): 将string中符合pattern的子串替换成repl

### 4 常见用法

上面是python针对搜索、分割、替换给出的API，常见的用法是：

方式一：

```python
s = "test case"
regex = re.compile("\w+")
res_arr = regex.findall(s)
```

方式二：

```python
s = "test case"
res_arr = re.findall("\w+", s)
```

以上API都可以用上面这两种方式进行调用。