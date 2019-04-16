## 问和答

### 1 如何理解free命令的输出？

```
             total       used       free     shared    buffers     cached
Mem:         31868      31025        843          0       5943      12533
-/+ buffers/cache:      12548      19319
Swap:         2039        280       1759
```

理解free的输出需要理解两个概念：缓冲区和交换分区。

linux为了尽可能最大化内存的使用，并且在访问文件时减少对磁盘的操作，尽可能对内存进行访问，将磁盘上的内容缓存在页高速缓冲区中，当然这里面又分为了buffer和cache，这里不详细讲解，只要记住：buffers和cached是内核用于优化对磁盘的访问进行的缓存优化，在内存不足时可以进行回收。因此，一方面可以算做被内核给使用了，另一方面，也可以再次被应用程序使用。

交换分区是为了缓解内存不足时将部分数据放到磁盘上，待下次再次访问时可以再次放到内存，如果交换分区使用过多，说明系统有设计不合理之处。

以下就是上面输出的值的关系表达式：

```
total(Mem) = used(Mem) + free(Mem)
used(buffers/cache) = used(Mem) - buffers(Mem) - cached(Mem)
free(buffers/cache) = free(Mem) + buffers(Mem) + cached(Mem)
total(Swap) = used(Swap) + free(Swap)
```

### 2 redis的string类型如何区分数字和字符串？