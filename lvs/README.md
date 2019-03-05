# LVS 负载均衡原理及安装配置

---

lvs 是 `Linux Virtual Server` 的简称，也就是 linux虚拟服务器, 是一个由章文嵩博士发起的自由软件项目，它的官方站点是 `www.linuxvirtualserver.org` 。现在 lvs 已经是 linux 标准内核的一部分，在 linux2.4 内核以前，使用 lvs 时必须要重新编译内核以支持LVS功能模块，但是从 linux2.4 内核以后，已经完全内置了 lvs 的各个功能模块，无需给内核打任何补丁，可以直接使用 lvs 提供的各种功能。

## lvs 组成及相关术语
**lvs 组成** 
`lvs` 由2部分程序组成，包括 ipvs 和 ipvsadm；
 * ipvs(ip virtual server)：一段代码工作在内核空间，叫 ipvs，是真正生效实现调度的代码；
 * ipvsadm：另外一段是工作在用户空间，叫 ipvsadm，负责为ipvs内核框架编写规则，定义谁是集群服务，而谁是后端真实的服务器 (Real Server)；

**lvs相关术语**
 > * DS：Director Server。指的是前端负载均衡器节点。
 > * RS：Real Server。后端真实的工作服务器。
 > * VIP：向外部直接面向用户请求，作为用户请求的目标的IP地址。
 > * DIP：Director Server IP，主要用于和内部主机通讯的IP地址。
 > * RIP：Real Server IP，后端服务器的IP地址。
 > * CIP：Client IP，访问客户端的IP地址。

## lvs 工作模式
**NAT**
NAT 及网络地址转换，当用户请求到达调度器时，调度器将请求报文的目标地址（即虚拟IP地址）改写成选定的Real Server地址，同时报文的目标端口也改成选定的Real Server的相应端口，最后将报文请求发送到选定的Real Server。在服务器端得到数据后，Real Server返回数据给用户时，需要再次经过负载调度器将报文的源地址和源端口改成虚拟IP地址和相应端口，然后把数据发送给用户，完成整个负载调度过程。
可以看出，在NAT方式下，用户请求和响应报文都必须经过Director Server地址重写，当用户请求越来越多时，调度器的处理能力将成为瓶颈。

(lvs nat)[images/lvs/lvs-nat.jpg]

特性：  
1. RS的应该使用私有地址；  
2. RS的网关必须指向DIP；  
3. RIP和DIP必须在同一网段内；
4. 请求和响应的报文都得经过Director，在高负载场景中，Director很可能成为性能瓶颈；
5. 支持端口映射；  
6. RS可以使用任意支持集群服务的OS；
