# 如何快速定位内存性能瓶颈

## Linux 系统是如何分配内存的以及回收内存
Linux 内核为每个进程提供一个独立的虚拟地址空间（又分为内核空间和用户空间）。通过将虚拟内存地址映射到物理内存地址，为了完成内存映射，内核进程维护了一张页表（存储在 CPU 的内存管理单元 MMU 中）来记录虚拟地址与物理地址的映射关系。MMU 是以内存映射的最小单位“页”来管理内存，通常是 4KB，不过目前支持多级页表和大页。
  
malloc() 是 C 标准库提供的内存分配函数，对应到系统调用上，有两种实现方式，即 brk()  和 mmap() 函数。小于 128k 通过 brk()来分配。大于 128k 使用 mmap（）来分配。而回收内存则有如下3种方式：
 * 回收缓存，通过 LRU 算法回收最近最少使用的内存页面；
 * 基于 Swap机制，回收不常访问的匿名页，把不常用的内存通过交换分区直接写到磁盘中；
 * 杀死进程，通过 OOM 方式直接干掉占用内存较大的进程；


## 如何理解 buffer 和 cache 内存?
### 通过 free 命令查看系统内存信息
```
$ free
              total        used        free      shared  buff/cache   available
Mem:        8169348      263524     6875352         668     1030472     7611064
Swap:             0           0           0

$ man free
buffers
        Memory used by kernel buffers (Buffers in /proc/meminfo)

cache  
        Memory used by the page cache and slabs (Cached and SReclaimable in /proc/meminfo)

buff/cache
        Sum of buffers and cache
```
Buffer 是对磁盘数据的缓存，而 Cache 是文件数据的缓存，它们既会用在读请求中，也会用在写请求中。关于磁盘和文件的区别，磁盘是一个块设备，可以划分为不同的分区；在分区之上再创建文件系统，挂载到某个目录，之后才可以在这个目录中读写文件。
  
在读写普通文件时，会经过文件系统，由文件系统负责与磁盘交互；而读写磁盘或者分区时，就会跳过文件系统，也就是所谓的“裸I/O”。这两种读写方式所使用的缓存是不同的，也就是文中所讲的 Cache 和 Buffer 区别。


### 查看内存缓存命中率工具
 * cachestat 提供了整个操作系统缓存的读写命中情况；
 * cachetop 提供了每个进程的缓存命中率情况；

这两个工具都是 [bcc](https://github.com/iovisor/bcc) 软件包的一部分，基于 Linux 内核的 eBPF 机制，来跟踪内核中管理的缓存并输出缓存的使用和命中情况。
该工具包需要内核版本为 4.1 或 4.1以上版本。

[pcstat](https://github.com/tobert/pcstat) 工具可以用来查看文件在内存中的缓存大小以及缓存比例。

memleak （ bcc 软件包中的一个工具）用来检测内存泄漏工具，可以跟踪系统或指定进程的内存分配、释放请求，定期输出一个未释放内存和相应调用栈的汇总情况。其他机器可以使用 valgrind 工具来检测内存问题。
```
# -a 表示显示每个内存分配请求的大小以及地址
# -p 指定案例应用的 PID 号
$ /usr/share/bcc/tools/memleak -a -p $(pidof app)
WARNING: Couldn't find .text section in /app
WARNING: BCC can't handle sym look ups for /app
    addr = 7f8f704732b0 size = 8192
    addr = 7f8f704772d0 size = 8192
    addr = 7f8f704712a0 size = 8192
    addr = 7f8f704752c0 size = 8192
    32768 bytes in 4 allocations from stack
        [unknown] [app]
        [unknown] [app]
        start_thread+0xdb [libpthread-2.27.so] 

```

### 内存回收原理
在内存资源紧张时，linux 通过直接内存回收和定期扫描的方式来释放文件页和匿名页，以便把内存分配给更需要的进程使用。linux 内核通过 kswapd0 进程根据剩余内存的三个阈值（high/log/min，可通过 /proc/sys/vm/min_free_kbytes 进行设置，并可以通过 /proc/zoneinfo 来查看内存阈值。）来进行内存的回收操作。

**提示：** 关于 hadoop 集群建议关 swap 提升性能。事实上不仅 hadoop，包括 ES 在内绝大部分 Java 的应用都建议关 swap，这个和 JVM 的 gc 有关，它在 gc 的时候会遍历所有用到的堆的内存，如果这部分内存是被 swap 出去了，遍历的时候就会有磁盘IO。
  
**可以参考这两篇文章：**  
https://www.elastic.co/guide/en/elasticsearch/reference/current/setup-configuration-memory.html  
https://dzone.com/articles/just-say-no-swapping  

## 内存使用率高定位方式
> * 1. 通过 free 工具确认当前系统已使用内存、buffer、cache等指标参数；
> * 2. 如果发现大部分内存都被缓存占用，可以使用 vmstat 或者 sar 观察缓存的变化趋势，确认缓存是否继续增大；
> * 3. 如果继续增大，说明导致缓存升高的进程还在运行，此时通过 buffer/cacahe 分析工具 cachestat/cachetop/slabtop 等分析缓存被哪里占用；
> * 4. 如果未发现内存被 buffer/cache 占用，此时通过 top/ps/pidstat 工具定位内存最多的进程；
> * 5. 找到进程之后，可通过 pmap 分析进程地址空间中内存使用情况然后针对性优化即可；
> * 6. 通过 vmstat 或者 sar 发现内存不断增长，可以分析是否存在内存泄漏的问题。此时通过内存分析工具 memleak 检查内存是否泄漏；
> * 7. 如果存在内存泄漏，memleak 会输出内存泄漏的进程以及调用堆栈；

