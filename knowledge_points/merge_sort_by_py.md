## 使用python实现链表的归并排序

### 1 前言

在所有的排序算法中，链表的排序是比较适合使用归并排序的，而且时间复杂度能够达到O(nlogn)。

### 2 python中链表结构的构建

``` python
class ListNode:
  """ 链表节点的定义
  """
  def __init__(self, val):
    self.value = val
    self.next = None
  
  def __str__(self):
    return "[ListNode]" + str(self.value)

class ListIter:
  """ 链表迭代器的定义
  """
  def __init__(self, node):
    self.node = node
  
  def __str__(self):
    return str(self.node.value)
  
  def __next__(self):
    if self.node is None:
      raise StopIteration
    else:
      prev = self.node
      self.node = self.node.next
      return ListIter(prev)

class List:
  """
  链表的定义
  """
  def __init__(self, l):
    self.head = None
    self.tail = None
    for v in l:
      n = ListNode(v)
      if self.head is None:
        self.head = n
        self.tail = n
      else:
        self.tail.next = n
        self.tail = n
  
  @staticmethod
  def make_from_node(node):
    l = List([])
    l.head = node
    return l
  
  def __str__(self): 
    n = self.head
    s = ""
    while n is not None:
      s += " " + str(n.value)
      n = n.next
    return s
  
  def __iter__(self):
    return ListIter(self.head)
```

上面就是链表的定义，其中包含三个部分：链表的节点，链表以及链表的迭代器。里面有两个地方需要解释下：

1 `__str__`与`__repr__`

`__str__`和`__repr__`都可以用于将对象转换为字符串，通常用于人们查看对象的信息。而在使用这两个函数时有一些规则：

* 这两个函数分别可以通过str()和repr()显示调用
* 当没有定义`__str__`时，使用str()时会去调用`__repr__`，因此，类应该始终定义`__repr__`

2 `__iter__`与`__next__`

* 有`__iter__`的类对象称为可迭代对象，有`__next__`的类称为迭代器
* 这两个函数的使用方式可以用类似下面的for循环进行理解：

``` python
l = List([1, 2, 3])

# 使用for循环遍历链表
for v in l:
  print(v)

# 使用迭代器遍历链表
it = iter(l)
while True:
  try:
    cur = next(it)
  except StopIteration as error:
    break
  else:
    print(cur)
```

在上面的while True死循环中，通过StopIteration异常退出循环，如果没有发生异常，则打印当前值。

### 3 归并排序

归并排序的原理是，给定一个链表，将该链表分成等长的两个子链表，对两个子链表分别进行排序，然后再归并，因此，这里的排序是一个递归。

``` python
def mergeSort(l):
  """归并排序的对外的接口
  """
  return List.make_from_node(sortList(l.head))

def sortList(node):
  """归并排序的主函数，其中会递归调用自身
  """
  if node is None or node.next is None:
    return node
  if node.next.next is None:
    if node.value > node.next.value:
      node.value, node.next.value = node.next.value, node.value
    return node
  one = node
  two = node.next
  while two is not None:
    one = one.next
    two = two.next
    if two is not None:
      two = two.next
    else:
      break
  middle_node = one.next
  one.next = None
  one_l = sortList(node)
  two_l = sortList(middle_node)
  return merge(one_l, two_l)

def merge(l1, l2):
  """合并逻辑，对两个已排序链表进行合并
  """
  if l1 is None:
    return l2
  if l2 is None:
    return l1
  n1 = l1
  n2 = l2
  head = None
  n = None
  while n1 is not None and n2 is not None:
    if n1.value <= n2.value:
      if n is None:
        head = n = n1
      else:
        n.next = n1
        n = n1
      n1 = n1.next
    else:
      if n is None:
        head = n = n2
      else:
        n.next = n2
        n = n2
      n2 = n2.next
  if n1 is not None:
    if n is None:
      head = n = n1
    else:
      n.next = n1
  if n2 is not None:
    if n is None:
      head = n = n2
    else:
      n.next = n2
  return head
```