# Centos 8运维基本知识

## 1.Centos8 新特性简介

### 1.1 内核版本
在`Centos8`中的内核版本为`4.18 kernel`，附带了`Google BBR`拥塞控制算法。此时通过一条命令即可开启使用`BBR`作为拥塞控制算法。
```
$ sysctl -w net.ipv4.tcp_congestion_control=bbr
```

### 1.2 新的包管理工具dnf
`dnf`是新一代的`rpm`包管理工具，在使用上与`yum`命令的操作没有太多的不同。

### 1.3 Base OS与App Stream
`CentOS 8`将传统的包仓库一分为二，`Base OS`提供与操作系统相关的底层组件，而`App Stream`则提供用户使用的应用程序。`App Stream`可以快速的安装指定版本的应用程序，例如`dnf install @postgresql:5.6`，完整的应用程序列表可以使用 dnf module list 命令查看，遗憾的是目前仅为少数几个应用程序提供了多个版本。


## 2.使用 nmcli 命令进行网络管理
在`rhel7`上，同时支持`network.service`和`NetworkManager.service`（简称NM）。默认情况下，这2个服务都有开启，但许多人都会将`NM`禁用掉。但是在`rhel8`上，已废弃`network.service`，因此只能通过`NM`进行网络配置，包括动态`ip`和静态`ip`。换言之，在`rhel8`上，必须开启`NM`，否则无法使用网络。

**提示**: `rhel8`依然支持`network.service`，只是默认没安装。`nmcli`该命令可以完成网卡上所有的配置工作，并且可以写入配置文件，永久生效。

### 2.1 查看网卡信息命令
```
# 查看所有网络连接
$ nmcli connection show

# 查看活动的网络连接
$ nmcli connection show -active

# 查看指定网卡的详细信息
$ nmcli connection show enp0s5

# 显示指定网络设备的详细信息
$ nmcli device show enp0s5
```

### 2.2 网卡状态修改命令
```
# 启用/停用网络连接
$ nmcli connection up enp0s5
$ nmcli connection down enp0s5

# 重新加载网络配置
$ nmcli connection reload

# 删除/添加网卡
$ nmcli connection delete enp0s5
$ nmcli connection add type ethernet con-name enp0s5
```

### 2.3 修改网卡配置
```
# 设置自动启动网卡，实际修改的是网卡配置文件ONBOOT=yes
$ nmcli connection modify enp0s5 connection.autoconnect yes

# 设置IP地址获取方式是手动或者DHCP
$ nmcli connection modify enp0s5 ipv4.method manual ipv4.addresses 172.16.10.1/16

# 设置IP地址为DHCP，BOOTPROTO=static/none
$ nmcli connection modify enp0s5 ipv4.method auto

# 修改IP地址
$ nmcli connection modify enp0s5 ipv4.addresses 172.16.10.100/16

# 修改网关
$ nmcli connection modify enp0s5 ipv4.gateway 172.16.1.1

# 添加DNS
$ nmcli connection modify enp0s5 ipv4.dns 114.114.114.114
$ nmcli connection modify enp0s5 +ipv4.dns 8.8.8.8

# 创建connection，配置静态ip（等同于配置ifcfg，其中BOOTPROTO=none，并ifup启动）
$ nmcli c add type ethernet con-name enp0s5 ifname enp0s5 ipv4.addr 192.168.1.100/24 ipv4.gateway 192.168.1.1 ipv4.method manual

# 删除DNS
$ nmcli connection modify enp0s5 -ipv4.dns 8.8.8.8
```

### 2.4 重启服务
```
# 重载指定ifcfg或route到connection（不会立即生效）
$ nmcli c load /etc/sysconfig/network-scripts/ifcfg-enp0s5
$ nmcli c load /etc/sysconfig/network-scripts/route-enp0s5

# 重载所有ifcfg或route到connection（不会立即生效）
$ nmcli c reload

# 立即生效connection，有3种方法
$ nmcli c up enp0s5
$ nmcli d reapply enp0s5
$ nmcli d connect enp0s5
```
**提示**： 通过`NM`进行网络配置时候，会自动将`connection`同步到`/etc/sysconfig/network-scripts/ifcfg-enp0s5`配置文件中。此时需要通过命令`nmcli c reload`或者`nmcli c load /etc/sysconfig/network-scripts/ifcfg-enp0s5`的方式来让`NM`读取配置文件。

#### 需要注意的点：
* `NetworkManager`支持3种获取`dhcp`的方式：`dhclient`、`dhcpcd`、`internal`，当`/etc/NetworkManager/NetworkManager.conf`配置文件中的[main]部分没配置`dhcp=`时候，默认使用`internal`（rhel7/centos7默认是dhclient）。`internal`是`NM`内部实现的`dhcp`客户端。
* 指定网关时，经过实测`/etc/sysconfig/network`中的`GATEWAY`仅在3种情况下有效：`NM_CONTROLLED=no`或`ipv4.method manual`或从`ipv4.method manual`。建议：当`NM_CONTROLLED=no`时，将网关写在`/etc/sysconfig/network`；当使用NM时候，使用`nmcli c modify ethX ipv4.gateway 192.168.1.1`命令配置网关。
* `NM`默认会从`dhcp`里获取`dns`信息，并修改`/etc/resolv.conf`，如果不想让`NM`管理`/etc/resolv.conf`，则只需在`/etc/NetworkManager/NetworkManager.conf`里的[main]里增加`dns=none`即可。