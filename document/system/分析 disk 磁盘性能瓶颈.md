## 索引节点和目录项
在 Linux 系统中一切皆文件（文件、目录、块设备、套接字、管道等）。Linux 文件系统为每个文件都分配两个数据结构，索引节点（index node）和目录项（directory entry）。具体含义如下：
 * 索引节点，简称 inode，用来记录文件的元数据，比如 inode 编号、文件大小、访问权限、修改日期、数据的位置等。索引节点也会被持久化到磁盘中，因为它同样占用磁盘空间。
 * 目录项，简称为 dentry，用来记录文件的名字、索引节点指针以及与其他目录项的关联关系。目录项是由内核维护的一个内存数据结构，也被称为目录项缓存。

索引节点是每个文件的唯一标志，而目录项维护的是文件系统的树状结构。磁盘在执行文件系统格式化时，会被分成三个存储区域，超级块、索引节点区、数据块区。目录项、索引节点、逻辑块以及超级块，构成 linux 文件系统的四大基本要素。

## 虚拟文件系统
文件系统，是对存储设备上的文件进行组织管理的一种机制。为了支持各类不同的文件系统，linux 在各种文件系统上，抽象一层虚拟文件系统 VFS。它定义了一组所有文件系统都支持的数据结构和标准接口。这样应用程序和内核其他子系统只需要跟 VFS 提供的统一接口进行交互，而不需要关心地层文件系统实现细节。

## 通用层块
通用层块为文件系统和应用程序提供了访问块设备的标准接口。同时，也为各种块设备的驱动程序提供统一的框架。此外，它还会对文件系统和应用程序发送过来的 I/O 请求进行排队，并通过重新排序、请求合并等方式，提高磁盘读写效率。  

设备层，主要包括各种块设备的驱动程序以及物理存储设备。

## 文件系统 I/O
常见 I/O 有，缓冲与非缓冲 I/O、直接与非直接 I/O、阻塞与非阻塞 I/O 、同步与异步 I/O 等。它们的含义如下：
 * 第一种，根据是否利用标准库缓存来进行区分。如果利用标准库缓存来加速文件的访问，然后标准库内部再通过系统调度访问文件，这种方式称为缓冲 I/O 。而非缓冲 I/O 是指直接通过系统调用来访问文件，不经过标准库缓存。
 * 第二种，根据是否利用操作系统的页缓存区分。直接 I/O 是指跳过操作系统的页缓存，直接跟文件系统交互来访问文件。而非直接 I/O 是先经过系统的页缓存，然后再由内核或额外的系统调用真正写入磁盘。
 * 第三种，根据应用程序是否阻塞自身运行区分。阻塞 I/O 是指应用程序执行 I/O 操作后，如果没有获得响应就会阻塞当前线程，此时不能执行其他任务。而非阻塞 I/O 是指应用程序执行 I/O 操作后，不会阻塞当前线程，可以继续执行其他任务，随后在通过轮训或者事件通知的形式，获取调用的结果。
 * 第四种，根据是否等待响应结果来进行却分。同步 I/O 是在应用程序执行 I/O 操作后，要一直等待整个 I/O 完成后，才能获得 I/O 响应。异步 I/O 是指应用程序执行 I/O 操作后，无需等待结果而是继续执行。等 I/O 完成后，响应会用事件通知方式，告诉应用程序。

文件系统、通用层块层、设备层，就构成了 Linux 的存储的 I/O 栈。linux 有多种缓存机制，来优化 I/O 效率。比如说：
 * 为了优化文件访问的性能，采用页缓存、索引节点缓存、目录项缓存等多种缓存机制，减少对下层块设备的直接调用。
 * 同样的，为了优化块设备的访问效率，使用缓冲区来缓存块设备的数据。

**磁盘空间**
```
$ df -h /dev/sda1   # 查看磁盘空间使用情况
$ df -i /dev/sda1   # 查看磁盘 inode 情况
```

**缓存**  
此时可以通过 free 或 vmstat 来观察页缓存的大小。但 free 属于的 Cache 是页缓存和可回收 slab 缓存的总和； 
```
$ cat /proc/meminfo | grep -E "SReclaimable|Cached" 
Cached:           748316 kB 
SwapCached:            0 kB 
SReclaimable:     179508 kB 
```
而 `/proc/slabinfo` 能够具体到每一种 slab 缓存。
```
$ cat /proc/slabinfo | grep -E '^#|dentry|inode' 
# name            <active_objs> <num_objs> <objsize> <objperslab> <pagesperslab> : tunables <limit> <batchcount> <sharedfactor> : slabdata <active_slabs> <num_slabs> <sharedavail> 
xfs_inode              0      0    960   17    4 : tunables    0    0    0 : slabdata      0      0      0 
... 
ext4_inode_cache   32104  34590   1088   15    4 : tunables    0    0    0 : slabdata   2306   2306      0hugetlbfs_inode_cache     13     13    624   13    2 : tunables    0    0    0 : slabdata      1      1      0 
sock_inode_cache    1190   1242    704   23    4 : tunables    0    0    0 : slabdata     54     54      0 
shmem_inode_cache   1622   2139    712   23    4 : tunables    0    0    0 : slabdata     93     93      0 
proc_inode_cache    3560   4080    680   12    2 : tunables    0    0    0 : slabdata    340    340      0 
inode_cache        25172  25818    608   13    2 : tunables    0    0    0 : slabdata   1986   1986      0 
dentry             76050 121296    192   21    1 : tunables    0    0    0 : slabdata   5776   5776      0 
```
由于 `/proc/slabinfo` 输出信息太多。在实际生产中，建议使用 slabtop 命令。
```
# 按下 c 按照缓存大小排序，按下 a 按照活跃对象数排序 
$ slabtop 
Active / Total Objects (% used)    : 277970 / 358914 (77.4%) 
Active / Total Slabs (% used)      : 12414 / 12414 (100.0%) 
Active / Total Caches (% used)     : 83 / 135 (61.5%) 
Active / Total Size (% used)       : 57816.88K / 73307.70K (78.9%) 
Minimum / Average / Maximum Object : 0.01K / 0.20K / 22.88K 

  OBJS ACTIVE  USE OBJ SIZE  SLABS OBJ/SLAB CACHE SIZE NAME 
69804  23094   0%    0.19K   3324       21     13296K dentry 
16380  15854   0%    0.59K   1260       13     10080K inode_cache 
58260  55397   0%    0.13K   1942       30      7768K kernfs_node_cache 
   485    413   0%    5.69K     97        5      3104K task_struct 
  1472   1397   0%    2.00K     92       16      2944K kmalloc-2048 
```

Linux 内核支持以下 4 种 I/O 调度算法，如下所示：
 * NONE，完全不使用任何 I/O 调度器，对文件系统和应用程序的 I/O 不做任何处理，常用在虚拟机中；
 * NOOP，先入先出的规则，只做最基本的请求合并，常用于 SSD 磁盘；
 * CFQ（Completely Fair Scheduler），完全公平调度，默认调度器。它为每个进程维护了一个 I/O 调度队列，并按照时间片来均匀分布每个进行的 I/O 请求；
 * DeadLine，分别为读、写请求创建不同的 I/O 队列，提供机械磁盘的吞吐量，并确保达到最终期限的请求被优先处理，常用语数据库等；

## 机械硬盘（HHD）为什么会比固态硬盘（SSD）慢呢？
这里简单说一下我对它们的理解。机械硬盘是由读写磁头和盘片组成，而固态硬盘是由固态电子元器件组成。固态硬盘性能好，主要有以下2点：
 * 固态硬盘，不需要磁道寻址；
 * 固态硬盘的最小读写单位是页，通常大小为 4KB/8KB，而机械磁盘的最小读写单位是扇区，一般大小为 512 字节；

## 磁盘性能指标
判断磁盘是否存在性能瓶颈，可参考如下指标：
 * 使用率，磁盘处理 I/O 的时间百分比。
 * 饱和度，磁盘处理 I/O 的繁忙程度。
 * IOPS（input/output Per Second），每秒的 I/O 请求数。
 * 吞吐量，是指每秒的 I/O 请求大小。
 * 响应时间，是指 I/O 请求发出到收到响应时间的间隔时间。

## 磁盘 I/O 观测
首先观测每块磁盘的使用情况。`iostat` 是最常用的磁盘 I/O 性能观测工具，也可以通过 `/proc/diskstats` 文件进行查看。 
```
# -d -x 表示显示所有磁盘 I/O 的指标
$ iostat -d -x 1 
Device            r/s     w/s     rkB/s     wkB/s   rrqm/s   wrqm/s  %rrqm  %wrqm r_await w_await aqu-sz rareq-sz wareq-sz  svctm  %util 
loop0            0.00    0.00      0.00      0.00     0.00     0.00   0.00   0.00    0.00    0.00   0.00     0.00     0.00   0.00   0.00 
loop1            0.00    0.00      0.00      0.00     0.00     0.00   0.00   0.00    0.00    0.00   0.00     0.00     0.00   0.00   0.00 
sda              0.00    0.00      0.00      0.00     0.00     0.00   0.00   0.00    0.00    0.00   0.00     0.00     0.00   0.00   0.00 
sdb              0.00    0.00      0.00      0.00     0.00     0.00   0.00   0.00    0.00    0.00   0.00     0.00     0.00   0.00   0.00 
```
每列信息参考如下表格：  
![iostat每列含义说明](images/iostat%20指标解读.png)

重要指标提示：
 * %util，就是磁盘 I/O 使用率；
 * r/s + w/s，就是 IOPS；
 * rkB/s + wkB/s，就是吞吐量；
 * r_await + w_await，就是响应时间；

在观测指标时，还需要结合请求大小（rareq-sz 和 wareq-sz）一起分析。

## 进程 I/O 观测
`iostat` 只能够看到磁盘整体的 I/O 性能，而 `pidstat` 和 `iotop` 可以观察进程的 I/O 情况。
```
$ pidstat -d 1 
13:39:51      UID       PID   kB_rd/s   kB_wr/s kB_ccwr/s iodelay  Command 
13:39:52      102       916      0.00      4.00      0.00       0  rsyslogd
```
每列含义解释，如下：
> * kB_rd/s，每秒读取的数据大小，单位为 KB；
> * kB_wr/s，每秒发出的读请求数据大小，单位为 KB；
> * kB_ccwr/s，每秒取消的写请求数据大小，单位为 KB；
> * iodelay，块 I/O 延迟，包括等待同步 I/O 和换入块 I/O 结束的时间，单位是时钟固定周期；

`iotop` 根据 I/O 大小对进程排序。
```
$ iotop
Total DISK READ :       0.00 B/s | Total DISK WRITE :       7.85 K/s 
Actual DISK READ:       0.00 B/s | Actual DISK WRITE:       0.00 B/s 
  TID  PRIO  USER     DISK READ  DISK WRITE  SWAPIN     IO>    COMMAND 
15055 be/3 root        0.00 B/s    7.85 K/s  0.00 %  0.00 % systemd-journald 
```

## 磁盘性能查询思路
> * 通过 top 命令查看整个系统资源使用情况，过滤出此时有关磁盘性能的指标，比如 CPU 较高的内存、系统 iowait、资源使用较高的进程等；
> * 通过 iostat 命令获取磁盘使用情况，比如磁盘 I/O 使用率、吞吐量、请求队列等信息；
> * 如果通过 iostat 发现磁盘读写请求较高，那么可以通过 pidstat 查看具体进程；
> * 找到 pid 之后就可以通过命令 `strace -p $PID -f 2>&1 | grep write` 来确认是否有 write 系统调用。如果有系统调用，此时可以通过命令 `lsof -p $PID` 找出该进程写入的文件；
> * 如果未找到 write 系统调用，此时可以通过 filetop 命令找出当前系统读写文件较高的线程。由于 filetop 这是输出的文件名，因此接下来还需要通过 opensoonp 找出具体文件路径；

此时也可以参考如下示意图，进行排查：  
![iostat每列含义说明](images/磁盘性能分析示意图.png)

## 磁盘性能基准测试
fio（flexible I/O test）是最常用的文件系统和磁盘 I/O 性能基准测试工具。它提供大量的可定制化选项，可用用来测试裸盘或者文件系统在各种场景下的 I/O 性能，包括不同块大小、不同 I/O 引擎以及是否使用缓存等场景。具体实例如下：

```shell
# 随机读
fio -name=randread -direct=1 -iodepth=64 -rw=randread -ioengine=libaio -bs=4k -size=1G -numjobs=1 -runtime=1000 -group_reporting -filename=/dev/sdb

# 随机写
fio -name=randwrite -direct=1 -iodepth=64 -rw=randwrite -ioengine=libaio -bs=4k -size=1G -numjobs=1 -runtime=1000 -group_reporting -filename=/dev/sdb

# 顺序读
fio -name=read -direct=1 -iodepth=64 -rw=read -ioengine=libaio -bs=4k -size=1G -numjobs=1 -runtime=1000 -group_reporting -filename=/dev/sdb

# 顺序写
fio -name=write -direct=1 -iodepth=64 -rw=write -ioengine=libaio -bs=4k -size=1G -numjobs=1 -runtime=1000 -group_reporting -filename=/dev/sdb 
```
**参数说明：**  
* direct，表示是否跳过系统缓存。默认不跳过，1 表示跳过系统缓存。
* iodepth，表示使用异步 I/O （asynchronous I/O，简称AIO）时，同时出发的 I/O 请求上限。
* rw，表示 I/O 模式。read/write 表示为顺序读/写。而 randread/randwrite 则分别表示随机读/写。
* ioengine，表示 I/O 引擎，它支持同步（sync）、异步（libaio)、内存映射（mmap）、网络（net）等各种 I/O 引擎。
* bs，表示 I/O 的大小，表示单次I/O的块文件大小为4 KB。未指定该参数时的默认大小也是4 KB。
测试IOPS时，建议将bs设置为一个比较小的值，如本示例中的4k。
测试吞吐量时，建议将bs设置为一个较大的值，如本示例中的1024k。
* size，表示测试文件大小为1GiB。
* numjobs，表示测试线程数为1。
* runtime，表示测试时间为1000秒。未配置，则持续将前述size指定大小的文件，以每次bs值为分块大小写完。
* group_reporting，表示测试结果里汇总每个进程的统计信息，而非以不同的job汇总展示信息。
* filename，表示文件路径。可以是磁盘路径，也可以是文件路径。在使用磁盘路径测试时，会破坏整个磁盘中的文件系统，所以在使用前，需要做好数据备份。

fio 测试顺序读的报告示例，如下：
```
read: (g=0): rw=read, bs=(R) 4096B-4096B, (W) 4096B-4096B, (T) 4096B-4096B, ioengine=libaio, iodepth=64
fio-3.1
Starting 1 process
Jobs: 1 (f=1): [R(1)][100.0%][r=16.7MiB/s,w=0KiB/s][r=4280,w=0 IOPS][eta 00m:00s]
read: (groupid=0, jobs=1): err= 0: pid=17966: Sun Dec 30 08:31:48 2018
   read: IOPS=4257, BW=16.6MiB/s (17.4MB/s)(1024MiB/61568msec)
    slat (usec): min=2, max=2566, avg= 4.29, stdev=21.76
    clat (usec): min=228, max=407360, avg=15024.30, stdev=20524.39
     lat (usec): min=243, max=407363, avg=15029.12, stdev=20524.26
    clat percentiles (usec):
     |  1.00th=[   498],  5.00th=[  1020], 10.00th=[  1319], 20.00th=[  1713],
     | 30.00th=[  1991], 40.00th=[  2212], 50.00th=[  2540], 60.00th=[  2933],
     | 70.00th=[  5407], 80.00th=[ 44303], 90.00th=[ 45351], 95.00th=[ 45876],
     | 99.00th=[ 46924], 99.50th=[ 46924], 99.90th=[ 48497], 99.95th=[ 49021],
     | 99.99th=[404751]
   bw (  KiB/s): min= 8208, max=18832, per=99.85%, avg=17005.35, stdev=998.94, samples=123
   iops        : min= 2052, max= 4708, avg=4251.30, stdev=249.74, samples=123
  lat (usec)   : 250=0.01%, 500=1.03%, 750=1.69%, 1000=2.07%
  lat (msec)   : 2=25.64%, 4=37.58%, 10=2.08%, 20=0.02%, 50=29.86%
  lat (msec)   : 100=0.01%, 500=0.02%
  cpu          : usr=1.02%, sys=2.97%, ctx=33312, majf=0, minf=75
  IO depths    : 1=0.1%, 2=0.1%, 4=0.1%, 8=0.1%, 16=0.1%, 32=0.1%, >=64=100.0%
     submit    : 0=0.0%, 4=100.0%, 8=0.0%, 16=0.0%, 32=0.0%, 64=0.0%, >=64=0.0%
     complete  : 0=0.0%, 4=100.0%, 8=0.0%, 16=0.0%, 32=0.0%, 64=0.1%, >=64=0.0%
     issued rwt: total=262144,0,0, short=0,0,0, dropped=0,0,0
     latency   : target=0, window=0, percentile=100.00%, depth=64

Run status group 0 (all jobs):
   READ: bw=16.6MiB/s (17.4MB/s), 16.6MiB/s-16.6MiB/s (17.4MB/s-17.4MB/s), io=1024MiB (1074MB), run=61568-61568msec

Disk stats (read/write):
  sdb: ios=261897/0, merge=0/0, ticks=3912108/0, in_queue=3474336, util=90.09% 
```
重要注意 slat、clat、lat 以及 bw 和 iops 行。slat、clat、lat 都是指 I/O 延迟，不同之处在于：
 * slat，是指从 I/O 提交到实际执行 I/O 的时长。
 * clat，是指从 I/O 提交到 I/O 完成的时长。
 * lat，是指从 fio 创建 I/O 到 I/O 完成的总时长。

 
