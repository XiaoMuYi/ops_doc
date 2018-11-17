## 关于 centos 7.x 时间同步
在CentOS 6版本，时间设置有date、hwclock命令，从CentOS 7开始，完全可以使用了一个新的命令timedatectl来替换。

### 一、基本概念
#### 1.1 GMT、UTC、CST、DST 时间
#### (1) UTC
整个地球分为二十四时区，每个时区都有自己的本地时间。在国际无线电通信场合，为了统一起见，使用一个统一的时间，称为通用协调时(UTC, Universal Time Coordinated)。
#### (2) GMT
格林威治标准时间 (Greenwich Mean Time)指位于英国伦敦郊区的皇家格林尼治天文台的标准时间，因为本初子午线被定义在通过那里的经线。(UTC与GMT时间基本相同，本文中不做区分)
#### (3) CST
中国标准时间 (China Standard Time)
Default
GMT + 8 = UTC + 8 = CST
#### (4) DST
夏令时(Daylight Saving Time) 指在夏天太阳升起的比较早时，将时钟拨快一小时，以提早日光的使用。（中国不使用）

#### 1.2 硬件时钟和系统时钟
#### (1) 硬件时钟  
RTC(Real-Time Clock)或CMOS时钟，一般在主板上靠电池供电，服务器断电后也会继续运行。仅保存日期时间数值，无法保存时区和夏令时设置。
#### (2) 系统时钟  
一般在服务器启动时复制RTC时间，之后独立运行，保存了时间、时区和夏令时设置。

### 二、时间同步方式
#### 2.1 使用 NTP 进行时间同步
NTP在linux下有两种时钟同步方式，分别为直接同步和平滑同步：
+ 直接同步  
使用ntpdate命令进行同步，直接进行时间变更。如果服务器上存在一个12点运行的任务，当前服务器时间是13点，但标准时间时11点，使用此命令可能会造成任务重复执行。因此使用ntpdate同步可能会引发风险，因此该命令也多用于配置时钟同步服务时第一次同步时间时使用。

+ 平滑同步  
使用ntpd进行时钟同步，可以保证一个时间不经历两次，它每次同步时间的偏移量不会太陡，是慢慢来的，这正因为这样，ntpd平滑同步可能耗费的时间比较长。

#### 2.1.1 查看是否安装
```
$ rpm -qa|grep ntp
ntpdate-4.2.6p5-25.el7.centos.2.x86_64
ntp-4.2.6p5-25.el7.centos.2.x86_64
```

#### 2.1.2 如未安装请执行如下命令
```
$ yum -y install ntp ntpdate
```

#### 2.1.3 修改 NTP 配置
```
$ /etc/ntp.conf 
# For more information about this file, see the man pages
# ntp.conf(5), ntp_acc(5), ntp_auth(5), ntp_clock(5), ntp_misc(5), ntp_mon(5).

driftfile /var/lib/ntp/drift
disable monitor

#新增:日志目录.
logfile /var/log/ntpd.log

# Permit time synchronization with our time source, but do not
# permit the source to query or modify the service on this system.
restrict default kod nomodify notrap nopeer noquery
restrict -6 default kod nomodify notrap nopeer noquery

# Permit all access over the loopback interface.  This could
# be tightened as well, but to do so would effect some of
# the administrative functions.
restrict 127.0.0.1 
restrict -6 ::1

# Hosts on local network are less restricted.
#restrict 192.168.1.0 mask 255.255.255.0 nomodify notrap

# Use public servers from the pool.ntp.org project.
# Please consider joining the pool (http://www.pool.ntp.org/join.html).
#server 0.centos.pool.ntp.org iburst
#server 1.centos.pool.ntp.org iburst
#server 2.centos.pool.ntp.org iburst
#server 3.centos.pool.ntp.org iburst

server time.pool.aliyun.com prefer
server 0.cn.pool.ntp.org
server 1.cn.pool.ntp.org
server 0.asia.pool.ntp.org

#broadcast 192.168.1.255 autokey	# broadcast server
#broadcastclient			# broadcast client
#broadcast 224.0.1.1 autokey		# multicast server
#multicastclient 224.0.1.1		# multicast client
#manycastserver 239.255.254.254		# manycast server
#manycastclient 239.255.254.254 autokey # manycast client

#新增:允许上层时间服务器主动修改本机时间.
restrict time.pool.aliyun.com nomodify notrap noquery
restrict 0.cn.pool.ntp.org nomodify notrap noquery
restrict 1.cn.pool.ntp.org nomodify notrap noquery

# Enable public key cryptography.
#crypto

includefile /etc/ntp/crypto/pw

# Key file containing the keys and key identifiers used when operating
# with symmetric key cryptography. 
keys /etc/ntp/keys

# Specify the key identifiers which are trusted.
#trustedkey 4 8 42

# Specify the key identifier to use with the ntpdc utility.
#requestkey 8

# Specify the key identifier to use with the ntpq utility.
#controlkey 8

# Enable writing of statistics records.
#statistics clockstats cryptostats loopstats peerstats
```
#### 2.1.4 启动相关服务
```
$ systemctl start ntpd
$ systemctl enable ntpd
```
#### 2.2 chrony
Chrony是一个开源的自由软件，像CentOS 7或基于RHEL 7操作系统，已经是默认服务，默认配置文件在 /etc/chrony.conf 它能保持系统时间与时间服务器（NTP）同步，让时间始终保持同步。相对于NTP时间同步软件，占据很大优势。其用法也很简单。

Chrony有两个核心组件，分别是：
+ chronyd：是守护进程，主要用于调整内核中运行的系统时间和时间服务器同步。它确定计算机增减时间的比率，并对此进行调整补偿。
+ chronyc：提供一个用户界面，用于监控性能并进行多样化的配置。它可以在chronyd实例控制的计算机上工作，也可以在一台不同的远程计算机上工作。

#### 2.2.1 安装Chrony
系统默认已经安装，如未安装，请执行以下命令安装：
```
$ yum install chrony -y
```
#### 2.2.2 配置Chrony
```
$ cat /etc/chrony.conf
# 使用pool.ntp.org项目中的公共服务器。以server开，理论上你想添加多少时间服务器都可以。
# Please consider joining the pool (http://www.pool.ntp.org/join.html).
server time.pool.aliyun.com iburst
server 0.cn.pool.ntp.org iburst
server 1.cn.pool.ntp.org iburst
server 0.asia.pool.ntp.org iburst

# 根据实际时间计算出服务器增减时间的比率，然后记录到一个文件中，在系统重启后为系统做出最佳时间补偿调整。
driftfile /var/lib/chrony/drift

# chronyd根据需求减慢或加速时间调整，
# 在某些情况下系统时钟可能漂移过快，导致时间调整用时过长。
# 该指令强制chronyd调整时期，大于某个阀值时步进调整系统时钟。
# 只有在因chronyd启动时间超过指定的限制时（可使用负值来禁用限制）没有更多时钟更新时才生效。
makestep 1.0 3

# 将启用一个内核模式，在该模式中，系统时间每11分钟会拷贝到实时时钟（RTC）。
rtcsync

# Enable hardware timestamping on all interfaces that support it.
# 通过使用hwtimestamp指令启用硬件时间戳
#hwtimestamp eth0
#hwtimestamp eth1
#hwtimestamp *

# Increase the minimum number of selectable sources required to adjust
# the system clock.
#minsources 2

# 指定一台主机、子网，或者网络以允许或拒绝NTP连接到扮演时钟服务器的机器
#allow 192.168.0.0/16
#deny 192.168/16

# Serve time even if not synchronized to a time source.
local stratum 10

# 指定包含NTP验证密钥的文件。
#keyfile /etc/chrony.keys

# 指定日志文件的目录。
logdir /var/log/chrony

# Select which information is logged.
#log measurements statistics tracking
```

#### 2.2.3 启动服务
```
$ systemctl start chronyd
$ systemctl enable chronyd
```
设置完时区后，强制同步下系统时钟：
```
$ chronyc -a makestep
200 OK
```
查看时间同步源状态：
```
$ chronyc sourcestats -v
```

### 其他
关于 timedatecatl 命令使用
```
timedatectl 或 timedatectl status           # 读取时间
timedatectl set-time "YYYY-MM-DD HH:MM:SS"  # 设置时间
timedatectl list-timezones                  # 列出时区
timedatectl set-timezone Asia/Shanghai      # 设置时区
timedatectl set-ntp yes                     # 同步NTP服务器，可以no
timedatectl set-local-rtc 1                 # 将硬件时钟调整为与本地时钟一致
```
硬件时钟默认使用UTC时间，因为硬件时钟不能保存时区和夏令时调整，修改后就无法从硬件时钟中读取出准确标准时间，因此不建议修改。修改后系统会出现警告。安装完服务器之后，首先到官方 NTP 公共时间服务器池NTP Public Pool Time Servers（www.pool.ntp.org） ，选择你服务器物理位置所在的洲，然后搜索你的国家位置，然后会出现 NTP 服务器列表。
