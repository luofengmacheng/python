## python面试题

1 (2019年1月28日)给定一个整数N，返回1~N之间二进制是回文的整数构成的数组

最简单的处理方式就是依次遍历每个整数，判断它的二进制是否是回文。

``` python
def check_palindrome(num):
    s = bin(num)[2:]
    if s == s[::-1]:
        return True
    else:
        return False

def get_all_palindrome(num):
    res = []
    for i in range(1, num):
        if check_palindrome(i):
            res.append(i)
    return res

print(get_all_palindrome(1000))
```

第二种方式可以用自动生成的方式：

假如已经知道了3位的回文整数：101，那么可以用该回文整数生成以下两种回文整数：

* 可以在两边增加1，生成5位的回文整数：10101
* 可以在两边增加0，然后在两边再添加1：100001

规则可以如上执行，但是还有个问题：何时应该结束生成下一组回文呢？也就是下面代码中外层for循环的终止条件。

首先可以明确的是，每次for循环至少会在上一次生成的所有的回文整数前后加1位，也就是每次至少会增加2位，另一方面，n位的最小的回文一定是中间n-2个0，首尾都是1，那么对输入的整数求2的对数就可以得到`大于num的最小的位数`，然后除以2就得到for循环的次数。

``` python
def get_all_palindrome2(num):
    init_num = ["0", "1", "00", "11"]
    res = [1, 3]

    for i in range(int(math.log2(num))//2):
        new_init_num = []
        for s in init_num:
            s1 = "10" + s[1:-1] + "01"
            n1 = int(s1, 2)
            if s1 not in new_init_num:
                new_init_num.append(s1)
            if n1 < num and n1 not in res:
                res.append(n1)

            s2 = "1" + s + "1"
            n2 = int(s2, 2)
            if s2 not in new_init_num:
                new_init_num.append(s2)
            if n2 < num and n2 not in res:
                res.append(n2)
            
        init_num = new_init_num
    res.sort()
    return res
```

2 (2019年2月22日)如何实现一个LRU？

LRU是Least Recently Used(最近最少使用)的缩写，它是一种缓存换出算法，即当缓存空间满时，选择换出数据的算法。它涉及到局部性原理：如果该数据在最近没有被访问到，那么它在将来被访问到的可能性也很小。

因此，需要实现两种策略：

* 当访问某个元素时，如果它在LRU中，就将它移动到最近可以访问的地方(例如，链头)，如果它不在LRU中，就将它放到最近可以访问的地方
* 当LRU的空间不足时，就需要将元素移出LRU，此时需要找到最久未访问的元素(例如，链尾)

三种实现方式：

* 数组：给每个数据项添加`访问时间戳`，每次新增数据项时，将当前所有数据项的时间戳自增，并将新数据项的时间戳置为0并插入到数组中，每次访问数据项时，将被访问的数据项的时间戳置为0，当数组空间满时，淘汰时间戳最大的数据项。用数组实现的问题在于，数据的插入和访问的时间复杂度都是O(n)。
* 双向链表：每次插入数据时将数据插入到链头，每次访问数据时，将数据移到链头，当需要淘汰数据时，就淘汰链尾。采用双向链表的原因是需要删除链尾时，可以用O(1)时间进行删除操作。同样，用链表实现时，访问的时间复杂度是O(n)。
* 双向链表+哈希表：为了解决访问的时间复杂度，引入了哈希表(python是dict()，java中是hashmap)。当访问某个元素时，通过哈希表进行判断，此时的时间复杂度是O(1)，如果它在哈希表中，则跟上面链表的操作方式一样，移动到链头，如果它不在哈希表中，则直接插入到链头。如果需要将元素移出LRU，则删除链表尾部的元素，并将元素从哈希表中删除。

3 (2019年6月17日)使用python判断矩阵是否满秩，并计算矩阵的秩？

4 (2019年6月17日)使用shell每5分钟获取本机访问其它数据库的程序？

* 使用crontab实现定期获取
* 使用ss命令获取连接，并使用状态和端口进行过滤，就可以得到本机的哪些端口在访问外部的数据库
* 使用lsof命令根据端口获取对应的进程

``` shell
ss -o state established '( dport = :3306 )'|awk '{print $3}'|awk -F':' '{print $2}'|while read port; do if [ x"$port" != x"" ]; then lsof -i:$port; fi; done|grep -v "^COMMAND"
```