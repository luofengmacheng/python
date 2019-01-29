## 八大排序算法(Python实现)

八大排序算法是面试经常会考的，对于算法的细节以及复杂度应该非常熟悉。

插希冒快选堆归基：

```
插入排序：直接插入排序；希尔排序
交换排序：冒泡排序；快速排序
选择排序：简单选择排序；堆排序
归并排序
基数排序
```

### 1 直接插入排序

要点：每次将一个元素放入一个已排序的数列

``` python
def direct_insert_sort(array_list, reverse=False):
    for i in range(1, len(array_list)):
        tmp = array_list[i]
        for j in range(i-1, -1, -1):
            if array_list[j] > tmp:
                array_list[j+1], array_list[j] = array_list[j], array_list[j+1]
            else:
                array_list[j+1] = tmp
                break
```

### 2 希尔排序

要点：利用插入排序的特性(当数据大致有序时，时间复杂度较低)

``` python
def shell_sort(array_list):
    gap = len(array_list)
    while gap >= 1:

        for i in range(1, len(array_list), gap):
            tmp = array_list[i]
            for j in range(i-gap, -1, -gap):
                if array_list[j] > tmp:
                    array_list[j+gap], array_list[j] = array_list[j], array_list[j+gap]
                else:
                    array_list[j+gap] = tmp
                    break

        gap //= 2
```

### 3 冒泡排序

要点：每轮通过前后比较和交换的方式将当前找到的最大(最小)元素放到数列的最终位置

``` python
def bubble_sort(array_list):
    for i in range(len(array_list)-1, -1, -1):
        for j in range(0, i):
            if array_list[j] > array_list[j+1]:
                array_list[j+1], array_list[j] = array_list[j], array_list[j+1]
```

### 4 快速排序

要点：从待排序数列中挑选一个元素A作为比较的对象，使得比A小的在前面，比A大的在后面，一轮就可以使得A元素在最终的位置，然后对左右的数列进行递归。

``` python
def quick_sort_with_index(array_list, start, stop):
    if start == stop or start+1 == stop:
        return
    val = array_list[start]
    i = start
    j = stop-1
    while i < j:
        print("i: ", i, "j:", j)
        while i < j and array_list[j] > val:
            j -= 1
            print("j:", j)
        if i < j:
            array_list[i] = array_list[j]
        else:
            break
        i += 1
        while i < j and array_list[i] < val:
            i += 1
        if i < j:
            array_list[j] = array_list[i]
        else:
            break
        j -= 1
    if i == j:
        array_list[i] = val
    
    quick_sort_with_index(array_list, start, i)
    quick_sort_with_index(array_list, i+1, stop)

def quick_sort(array_list):
    quick_sort_with_index(array_list, 0, len(array_list))
```

### 5 简单选择排序

要点：每轮从待排序的数列中选择出最大(小)的元素，然后与最终所在的位置的元素进行交换。

``` python
def select_sort(array_list):
    for i in range(len(array_list)-1, -1, -1):
        index = i
        val = array_list[i]
        for j in range(i):
            if array_list[j] > val:
                index = j
                val = array_list[j]
        array_list[i], array_list[index] = array_list[index], array_list[i]
```

### 6 堆排序

要点：

### 7 归并排序

要点：将待排序的序列分成两段等长的序列，分别对两个序列进行递归排序，然后再合并。(对于链表，可以用快慢指针找到中间的位置)

``` python
class Node(object):
    def __init__(self, val, p=None):
        self.data = val
        self.next = p

class ListTypeException(Exception):
    def __init__(self, msg):
        self.msg = msg

class LinkList(object):
    def __init__(self, head=None):
        self.head = head
    
    def create_with_list(self, data):
        if not isinstance(data, list):
            raise ListTypeException("data is not list")
        else:
            if len(data) <= 0:
                return
            else:
                p = Node(data[0])
                self.head = p

                for d in data[1:]:
                    q = Node(d)
                    p.next = q
                    p = q
    
    def __str__(self):
        res = []
        p = self.head
        while p is not None:
            res.append(str(p.data))
            p = p.next
        return "->".join(res)

def merge_sort_func(head):
    if head is None or head.next is None:
        return head
    
    if head.next.next is None:
        if head.data > head.next.data:
            head.data, head.next.data = head.next.data, head.data
        return head
    
    fast_ptr = lower_ptr = head
    lower_pre_ptr = None
    while fast_ptr is not None and fast_ptr.next is not None:
        lower_pre_ptr = lower_ptr
        lower_ptr = lower_ptr.next
        fast_ptr = fast_ptr.next.next
    
    lower_pre_ptr.next = None
    p = merge_sort_func(head)
    q = merge_sort_func(lower_ptr)
    new_head = None
    new_tail = None
    while p is not None and q is not None:
        if p.data <= q.data:
            if new_head is None:
                new_head = p
                new_tail = p
            else:
                new_tail.next = p
                new_tail = new_tail.next
            p = p.next
        else:
            if new_head is None:
                new_head = q
                new_tail = q
            else:
                new_tail.next = q
                new_tail = new_tail.next
            q = q.next
    
    if p is not None:
        new_tail.next = p
    else:
        new_tail.next = q
    return new_head

def merge_sort(ll):
    return LinkList(merge_sort_func(ll.head))

l = LinkList()
l.create_with_list([8, 4, 9, 6, 1, 9, 2])
print(l)
l = merge_sort(l)
print(l)
```

### 8 基数排序

要点：

