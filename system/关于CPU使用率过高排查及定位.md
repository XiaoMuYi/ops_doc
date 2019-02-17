---
# CPU上下文切换 
**CPU上下文切换是什么意思？**  
Linux在同时运行多任务时，是通过轮流分配CPU的方式造成多任务同时运行的错觉。并通过`CPU寄存器` 和 `程序计数器`来记录任务从哪里加载、又从哪里运行。**CPU寄存器** 是CPU中内置的容量小，但速度极快的内存。而**程序计数器** 则是记录CPU正在执行的指令或者即将执行的下一条指令。他们是CPU执行任务前必须依赖的环境，因此称为 `CPU上下文`。

进程从用户态到内核态的转变，需要通过系统调用来完成。系统调用的过程中，并不会涉及到虚拟内存等进程用户态的资源，也不会进程切换。需要注意的是系统调用过程通常称为特权模式切换，而不是上下文切换。但实际上，系统调用过程中，CPU 的上下文切换还是无法避免的。当然我们还需要知道 `进程和线程的区别`：
 * 1.进程是资源分配和执行的基本单位。  
 * 2.线程是任务调度和运行的基本单位。
 * 3.线程没有资源，进程给线程提供虚拟内存、栈、全局变量等共享资源，而线程可以共享进程的资源。

**CPU上下文切换** 就是将上一个CPU上下文保存到系统内核中，并在任务重新运行时加载进来。进程从用户态到内核态的转变，需要通过系统调用来完成。那么在什么情况下会触发上下文切换？系统调用、进程状态转换(运行、就绪、阻塞)、时间片耗尽、系统资源不足、sleep、优先级调度、硬件中断等都会引发上下文切换。根据任务的不同，CPU 的上下文切换又分为 `进程上下文切换`、`线程上下文切换` 和 `中断上下文切换`。
  * **进程上下文切换**，指的是一个进程切换到另一个进程。**系统调用** 的过程只有一个进程运行，但是一次系统调用的过程将发生两次CPU上下文切换。
  * **线程上下文切换**，一般分为2种情况，前后线程属于同一进程，另一个情况是前后两个进程不属于同一个进程。当前者的情况出现时，只需切换不同享的数据即可；后而后者因为资源不共享，因此和进程切换相似。  
    * 1. 当进程只有一个线程时，进程等于线程；
    * 2. 当进程拥有多个线程时，将共享同一虚拟内存、栈以及全局变量等资源。该资源在发生上下文切换时是不需要保存；
    * 3. 线程也拥有自己的私有数据，比如栈和寄存器等。当发生上下文切换时，是需要保存的；
  * **中断上下文切换**，快速响应硬件的事件，中断处理会打断进程的正常调度和执行。同一CPU内，硬件中断优先级高于进程。切换过程类似于系统调用的时候，不涉及到用户运行态资源。但大量的中断上下文切换同样可能引发性能问题。

**有哪些减少上下文切换的技术用例？**  
数据库连接池（复用连接）、合理设置应用的最大进程，线程数、直接内存访问DMA、零拷贝技术等。

**查看上下文切换**  
vmstat 是一个常用的系统性能分析工具，主要用来分析系统的内存使用情况，也常用来分析 CPU 上下文切换和中断的次数。
```
$ vmstat 5
procs -----------memory---------- ---swap-- -----io---- -system-- ------cpu-----
 r  b   swpd   free   buff  cache   si   so    bi    bo   in   cs us sy id  wa st
 0  0      0 7005360  91564 818900  0    0     0     0    25   33 0   0 100  0  0
```
**提示：**  
> * r（Running or Runnable）: 就绪队列的长度，也就是正在运行和等待 CPU 的进程数；  
> * b（Blocked）: 处于不可中断睡眠状态的进程数；  
> * swpd: 虚拟内存已使用的大小，如果大于0，表示你的机器物理内存不足了，如果不是程序内存泄露的原因，那么你该升级内存了或者把耗内存的任务迁移到其他机器；  
> * si: 每秒从磁盘读入虚拟内存的大小，如果这个值大于0，表示物理内存不够用或者内存泄露了，要查找耗内存进程解决掉。我的机器内存充裕，一切正常。  
> * so: 每秒虚拟内存写入磁盘的大小，如果这个值大于0，同上；  
> * bi: 块设备每秒接收的块数量，这里的块设备是指系统上所有的磁盘和其他块设备，默认块大小是1024byte，我本机上没什么IO操作，所以一直是0，但是我曾在处理拷贝大量数据(2-3T)的机器上看过可以达到140000/s，磁盘写入速度差不多140M每秒；  
> * bo: 块设备每秒发送的块数量，例如我们读取文件，bo就要大于0。bi和bo一般都要接近0，不然就是IO过于频繁，需要调整；  
> * in（interrupt）: 则是每秒中断的次数；  
> * cs（context switch）: 每秒上下文切换的次数；  
> * st: cpu在虚拟化环境上在其他租户上的开销;  

**vmstat 只给出了系统总体的上下文切换情况，要想查看每个进程的上线文切换次数，需要通过`pidstat -wt 5 `命令（pidstat是进程分析工具）。**
```
# 每隔 5 秒输出 1 组数据
$ pidstat -w 5
pidstat -wt 5
Linux 4.4.0-1065-aws (ip-172-31-25-95) 	02/16/19 	_x86_64_	(1 CPU)

13:22:22      UID      TGID       TID   cswch/s nvcswch/s  Command
13:22:27        0         3         -      0.60      0.00  ksoftirqd/0
13:22:27        0         -         3      0.60      0.00  |__ksoftirqd/0
13:22:27        0         7         -      2.00      0.00  rcu_sched
13:22:27        0         -         7      2.00      0.00  |__rcu_sched
```
**提示**：  
> * cswch：表示每秒自愿上下文切换（voluntary context switches）的次数。是指无法获取所需资源（比如，内存、I/O等资源），导致的上下文切换。  
> * nvcswch：表示每秒非自愿上下文切换（non voluntary context switches）的次数。指进程由于时间片已到等原因，被系统强制调度而发生的上下文切换。比如大量进程争抢CPU资源。  

**获取中断类型**
```
 $ watch -d cat /proc/interrupts
  48:  836243176  xen-percpu-virq      timer0
LOC:          0   Local timer interrupts
SPU:          0   Spurious interrupts
PMI:          0   Performance monitoring interrupts
IWI:         22   IRQ work interrupts
RTR:          0   APIC ICR read retries
RES:          0   Rescheduling interrupts
CAL:          0   Function call interrupts
```
**查看每个CPU统计信息**  
多处理器统计信息工具，能够报告每个CPU的统计信息。
```
mpstat -P ALL 1
Linux 2.6.32-573.el6.x86_64 (zbredis-30104)     09/14/2017  _x86_64_    (12 CPU)
 
03:14:03 PM  CPU    %usr   %nice    %sys %iowait    %irq   %soft  %steal  %guest   %idle
03:14:04 PM  all    0.00    0.00    0.08    0.00    0.00    0.00    0.00    0.00   99.92
03:14:04 PM    0    0.00    0.00    0.00    0.00    0.00    0.00    0.00    0.00  100.00
03:14:04 PM    1    0.00    0.00    0.00    0.00    0.00    0.00    0.00    0.00  100.00
```
**提示：**  
> * irq: 代表处理硬中断的 CPU 时间；  
> * sofr: 代表处理软中断的 CPU 时间；  
> * steal: 代表当系统运行在虚拟机中的时候，被其他虚拟机占用的 CPU 时间；  
> * guest: 代表通过虚拟化运行其他操作系统的时间，也就是运行虚拟机的 CPU 时间；  

重要关注列有 %user、%sys、%idle 。显示了每个 CPU 的用量以及用户态和内核态的时间比例。可以根据这些值查看那些跑到100%使用率（%user + %sys）的 CPU，而其他 CPU 并未跑满可能是由单线程应用程序的负载或者设备中断映射造成。

# CPU使用率过高排查思路及方式 
---
Linux 作为一个多任务操作系统，将每个 CPU 的时间划分为很短的时间片，再通过调度器轮流分配给各个任务使用
通过实先定义的节拍率(内核用赫兹HZ标示)触发时间判断(全局变量jiffies记录)来进行维护 CPU 。节拍率是内核态运行，属于内核空间节拍率（可设置为 100、250、1000 等
），而用户空间节拍率( USER_HZ)是一个固定设置（总是为100）。
```
$ grep 'CONFIG_HZ=' /boot/config-$(uname -r)    # 内核空间节拍率值
CONFIG_HZ=1000
```

**方式一. perf 命令使用**
```
$ perf top
Samples: 833  of event 'cpu-clock', Event count (approx.): 97742399
Overhead  Shared Object       Symbol
   7.28%  perf                [.] 0x00000000001f78a4
   4.72%  [kernel]            [k] vsnprintf
   4.32%  [kernel]            [k] module_get_kallsym
   3.65%  [kernel]            [k] _raw_spin_unlock_irqrestore
# -g 开启调用关系分析，-p 指定 php-fpm 的进程号 21515
$ perf top -g -p 21515

# 使用 grep 查找函数调用
$ grep $func_name -r $/code_path/
```
**提示:**  
> * Overhead：是该符号的性能事件在所有采样中的比例，用百分比来表示；  
> * Shared：是该函数或指令所在的动态共享对象（Dynamic Share Object），如内核、进程名、动态链接库名、内核模块名等；  
> * Object：动态共享对象的类型。比如 [.] 表示用户空间的可执行程序或者动态链接库，而 [k] 则表示内核空间；  
> * Symbol：是符号名，也就是函数名。当函数名未知时，用十六进制的地址来表示；  

**方法二. Java 应用通过 jstat 命令**

查找 PID 消耗 cpu 最高的进程号 
```
# 显示进程运行信息列表，按 P 安装 cpu 使用率排序
$ top -c
Tasks: 120 total,   1 running, 119 sleeping,   0 stopped,   0 zombie
%Cpu(s):  0.0 us,  0.0 sy,  0.0 ni,100.0 id,  0.0 wa,  0.0 hi,  0.0 si,  0.0 st
KiB Mem :  1014500 total,   114780 free,   236168 used,   663552 buff/cache
KiB Swap:        0 total,        0 free,        0 used.   538608 avail Mem 

  PID USER      PR  NI    VIRT    RES    SHR S %CPU %MEM     TIME+ COMMAND                                                                                                                                       
10617 500       20   0 2239628  63184      0 S  0.3  6.2 123:27.71 /usr/local/java/bin/java -Djava.util.logging.config.file=/opt/tomcat/conf/logging.properties -Djava.util.logging.manager=org.apache.juli.Clas+
```

查找 PID 消耗 cpu 最高的线程号
```
# 显示进程运行信息列表，按 P 安装 cpu 使用率排序
$ top -Hp 10617
top -Hp 10617
top - 03:30:57 up 152 days,  2:00,  1 user,  load average: 0.00, 0.01, 0.00
Threads:  41 total,   4 running,  37 sleeping,   0 stopped,   0 zombie
%Cpu(s):  0.0 us,  0.0 sy,  0.0 ni,100.0 id,  0.0 wa,  0.0 hi,  0.0 si,  0.0 st
KiB Mem :  1014500 total,   114284 free,   236568 used,   663648 buff/cache
KiB Swap:        0 total,        0 free,        0 used.   538200 avail Mem 

  PID USER      PR  NI    VIRT    RES    SHR S %CPU %MEM     TIME+ COMMAND                                                               
10617 500       20   0 2239628  63184      0 S  0.0  6.2   0:00.02 java                                                                 
10666 500       20   0 2239628  63184      0 S  0.0  6.2   0:00.63 java                                                                 
10667 500       20   0 2239628  63184      0 S  0.0  6.2   1:09.09 java                                                                 
10668 500       20   0 2239628  63184      0 S  0.0  6.2   0:00.00 java                                      
10669 500       20   0 2239628  63184      0 S  0.0  6.2   0:00.00 java                                                                 
10670 500       20   0 2239628  63184      0 S  0.0  6.2   0:00.00 java

# 将消耗 cpu 最高的线程号从十进制转成十六进制，举例将线程号 `10666` 转为十六进制为 `29aa`;
$ jstack -l 29aa > ./10666.stack
$ cat ./10666.stack |grep '29aa' -C 8
```
**提示：**通过 top 、pidstat 等工具可以确认引发 CPU 性能问题的来源，然后再通过 perf 等工具排查引起性能问题的具体函数，java 应用关于 CPU 排查已经有淘宝大神编写成 shell 脚本，可以通过[脚本工具快速定位](https://github.com/oldratlee/useful-scripts)。

**总结：**
* 用户 CPU 和 Nice CPU 高，说明用户态进程占用了较多的 CPU ，所以应该着种排查进程的性能问题。  
* 系统 CPU 高，说明内核态占用了较多 CPU ，所以应该着重排查内核线程或者系统调用的性能问题。  
* I/O 等待 CPU 过高，说明等待 I/O 的时间比较长，所以应该这种排查磁盘是否出现了 I/O 问题。  
* 软中断和硬中断高，说明软中断或硬中断的处理程序占用了较多CPU，所以应该排查内核中的中断服务程序。 

---
# 系统的 CPU 使用率很高，但为啥却找不到高 CPU 的应用？
遇到这样的非常规问题，我们可以猜想是否是短时应用导致。比如应用可能直接调用其他二进制程序，而这些程序通常运行时间比较短，无法通过 top 等工具发现。而另一种可能就是应用本身不停的重启，而启动过程的资源初始化占据了大量的CPU资源。  

对于以上问题，我们可以通过 pstree 或者 [execsnoop](https://github.com/brendangregg/perf-tools) 找到它们的父进程，再从父进程所在的应用入手，排查问题的根源。
