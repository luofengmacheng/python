## 阅读Tornado源码时的一些问题

### 1 指定函数的返回类型

在函数或者类方法的后面使用`->`指定函数值的返回类型，但是它并没有强制函数必须返回该类型的值，而只是一种声明。例如：

``` python
def func() -> str:
    return "Hello world"
```

### 2 property

property是一个装饰器，用于对属性访问的限制，并在进行属性访问时可以添加特殊逻辑。

``` python
class Man:
    def __init__(self, name):
        self._name = name

    @property
    def name(self):
        # 用@property装饰name函数，就可以通过点号访问name属性
        # 注意，此时只能对属性进行访问，而不能对属性进行修改
        return self._name

    @name.setter
    def name(self, name):
        # 用@name.setter装饰name函数，就可以修改属性值
        self._name = name

m = Man("abc")

print(m.name)
m.name = "def"
print(m.name)
```

### 3 函数注解(Function Annotation)

函数注解起到提示的作用，不会对程序产生任何影响，只是供程序员查看。

``` python
# 声明函数的name参数的类型是str，返回值类型是int
# 但是，即时不按照这种规范来，执行时也不会报错
# 因此，函数注解只是一种提示，供程序员阅读
def func(name: str) -> int:
    print(name)
    return 0

print(func("abc"))
```

### 4 typing.overload

overload的含义是重载，但是与其它如C++/java不同，overload是一个装饰器，而且只是给类型检查工具使用，而对程序的执行没有任何影响。

``` python
from typing import overload

@overload
def func(name: str):
    print("in str")

@overload
def func(name: int):
    print("in int")

def func(name):
    print("in general")

func("abc")

func(3)
```

如上，定义了三个函数，其中上面的两个用overload进行装饰，最后一个函数定义没有用overload进行装饰，并且也没有函数注解，需要注意的是，在使用overload时，最后一个函数一定不能有注解。但是，在运行程序时，上面的两个overload函数不会对程序有任何影响，它们只会给类型检查工具使用。比如，类型检查工具检查到func()函数只能接受str和int，如果有其它的类型的调用就会发出提示。