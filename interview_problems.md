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