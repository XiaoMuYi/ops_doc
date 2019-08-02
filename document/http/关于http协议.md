# 关于http协议

## 1.认识http协议

`HTTP`就是超文本传输协议，也就是`HyperText Transfer Protocol`。是一个在计算机世界里专门在两点之间传输文字、图片、音频、视频等超文本数据的约定和规范。而且需要知道`HHTP`不是互联网、不是编程语言、不是HTML，也不是一个孤立的协议。

`HTTP`协议的请求报文和响应报文的结构基本相同，由以下3部分组成：
* 起始行（start line），描述请求和响应的基本信息；
* 头部字段集合（header），使用`key-value`形式更详细地说明报文；
* 消息正文（entity），实际传输的数据，它不一定是纯文本，可以是图片、视频等二进制数据；

起始行和头部字段经常又被称为 **“请求头”** 或 **“响应头”**。消息正文又被称为 **“实体”**。但与`header`对应，很多时候就直接称为`body`。在`HTTP`协议报文中，`header`是必须的，`body`可以没有。并且在`header`之后必须包含一个空行，也就是`CRLF`。

### 1.1 请求行
起始行也就是请求行，主要是简述客户端想要如何操作服务器端的资源。由以下三部分构成：

* 请求方法，比如GET/PUT/POST等，表示对资源的操作；
* 请求目标，通常是一个`URI`，标记请求方法要操作的资源；
* 版本号，表示报文使用的`HTTP`协议版本号；

这三部分通常是空格（SP）分割，使用`CRLF`换行表示结束。

### 1.2 状态行
响应报文里的起始行，注意这里它不叫“响应行”，而是 **状态行（status line）**，意思是服务器响应的状态。它主要由以下三部分构成：

* 版本号，表示报文使用的`HTTP`协议版本号；
* 状态码，比如200是成功，500是服务器错误；
* 原因，作为状态码补充，更详细的文字说明，帮助人理解原因；

这三部分通常也是空格（SP）分割，使用`CRLF`换行表示结束。

### 1.3 头部字段
请求行和状态行在加上头部字段集合就构成了`HTTP`报文里完整的请求头或相应头。

## 2.关于HTTP状态码

1xx：提示信息，表示目前是协议处理的中间状态，还需要后续操作；
2xx：成功，报文已经收到并正确处理；
* 200 是最常见的成功状态码，如果非HEAD请求，通常在响应头后都会有 body 数据；
* 204 No Content，与 200基本相同，区别就是响应头没有 body 数据；
* 206 Partial Content，是HTTP 分块下载或断点续传的基础，但在 body 里的数据不是全部资源而是部分资源。

3xx：重定向，资源位置发生变动，需要客户端重新发送请求；

* 301 Moved Permanently 俗称永久重定向，含义是此次请求资源已经不存在，需要改用新的URI再次访问；
* 302 Found，临时重定向。请求的资源还在，但暂时需要用另一个URI 访问；
* 304 Not Modified，用于 If-Modified-Since 等条件请求，表示资源未修改，用于缓存控制。

4xx：客户端错误，请求报文有误，服务器无法处理；

* 400 Bad Request 表示请求报文错误；
* 403 Forbidden 表示服务器禁止访问资源；
* 404 Not Found 资源在服务器中未找到；
* 405 Method Not Allowed，不允许使用某些方法操作资源；
* 406 Not Acceptable 资源无法满足客户端请求条件，例如请求中文但只有英文；
* 408 Request Timeout 请求超时，服务器等待时间过长；
* 409 Conflict 多个请求发送了冲突，可以理解为多线程并发时的竟态；
* 413 Request Entity Too Large 请求报文里的 body 太大；
* 414 Request-URI Too Long 请求行里的URI太大；
* 429 Too many Requests 客户端发送了太多的请求，通常是由于服务器的限连策略；
* 413 Request Header Fields Too Large 请求头某个字段或总体太大；

5xx：服务器错误，服务器在处理请求时内部发生错误。

* 500 Internal Server Error 与 400类似，不知道为啥；
* 501 Not Implemented 表示客户端请求的功能还不支持；
* 502 Bad Gateway 网关或代理错误，一般表示后端服务器发生错误；
* 503 Service Unavailable 表示服务器很忙，暂时无法响应服务；

**案例分析** 
一般情况下`4xx`是服务端业务状态码，需要业务开发人员解决。`5xx`是比较常见的，比如500、502在LNMP架构中，500 就是因为业务代码写的不合理，导致`NGINX`的`upstream`接受错误，抛出了异常。

502 就是`php-fpm`挂了。

504 说明有慢查询`php-fpm`可能还在运行，由于`nginx`本身的超时设置已经主动断开。

## 3.关于HTTPS

### 什么叫安全通信？

既然`http`不够安全，那么如何才算安全呢？通常认为，如果通信过程具备四个特性：传输机密性、数据完整性、身份认证、不可否认，就可以认为是安全的。

### 什么是HTTPS？

`https`，默认端口为 443。`https`把`http`下层的传输协议由`TCP/IP`换成`SSL/TLS`，由`HTTP over TCP/IP`变成`HTTP over SSL/TLS`，让`HTTP`运行在安全的`SSL/TLS`协议上，收发报文不在使用`Socket API`，而是调用专门的安全接口。  

`SSL`即安全套接层（Secure Socket Layer），在`OSI`模型中处于第五层（会话层）。`SSL`发展的 v3 时已经是一个非常好的安全通信协议，于是互联网工程组`IETF`在1999年把它改名为`TLS`（传输层安全，Transport Layer Security），正式标准化，版本号从 1.0 重新算起，所以 `TLS1.0`实际上是`SSLv3.1`。  

目前应用最广泛的是`TLS`是 1.2，而之前的协议（TLS1.1/1.0 SSLv3/v2）各大浏览器将在2020年左右不在支持。`TLS`由记录协议、握手协议、警告协议、变更密码规范协议、扩展协议等多种协议组合而成，综合使用对称加密、非对称加密、身份认证等许多密码学技术。浏览器和服务器在使用`TLS`建立连接时需要选择一种恰当的加密算法来实现安全通信，这些算法的组合被称为“密码套件”。  

`TLS 1.2`，客户端和服务器都支持非常多的加密套件。比如"ECDHE-RSA-AES256-GCM-SHA384"，它的基本的形式是“密钥交换算法 + 签名算法 + 对称加密算法 + 摘要算法”。  

大概意思就是，握手时使用`ECDHE`算法进行秘钥交换，使用`RSA`签名和身份认证，握手后的通信使用`AES`对称算法，秘钥长度为 256位，分组模式是`GCM`，摘要算法`SHA384`用户消息认证和产生随机数。  


### OpenSSL

`OpenSSL`是从另一个开源库`SSLeay`发展而来。目前主要有`1.0.2`、`1.1.0`和`1.1.1`三个主要分支，前两个将不再维护。它还有一些代码分支，比如`Google`的`BoringSSL`、`OpenBSD`的`LibreSSL`，这些分支在原有基础上删除一些老旧代码，并新增一些特性。  

`OpenSSL`里的密码套件定义与`TLS`略有不同，`TLS`里的形式是"TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384"，加了前缀`TLS`，并用`WITH`分开了握手和通信的算法。

## 4.优化HTTPS

目前流行的`AES`、`ChaCha20`性能都很好，还有硬件优化，报文传输的性能损耗基本可以忽略不计。关于`https`优化建议从如下几点入手：

 * 硬件优化，由于`https`是计算密集型，此时可以选择更快的`CPU`，最好支持`AES`优化。也可以选择`SSL`加速卡，加解密时直接调用它的`API`，阿里的`Tengine`就是基于Intel QAT加速卡。因为`SSL`加速卡存在一些缺点，因此也可以选择`SSL`加速服务器。

 * 软件优化，比如`Linux`内核可以选择4.x以上，选择`Nginx 1.16`以上版本，将`OpenSSL`由 1.0.1 升级到 1.1.0/1.1.1。

 * 协议优化，尽量采用 `TLS 1.3`，它简化了握手过程并且更加安全。`Nginx`进行如下配置：
```shell
# 选择最优的密码套件和椭圆曲线；
ssl_ciphers TLS13-AES-256-GCM-SHA384:TLS13-CHACHA20-POLY1305-SHA256:EECDH+CHACHA20;
ssl_ecdh_curve X25519:P-256;
```

 * 证书优化，服务器的证书最好选择椭圆曲线（ECDSA）证书而不是`RSA`证书，它既能够节约带宽也能减少客户端的运算量。

 * 会话复用，分为2种，第一种基于`session ID`，最早也是最广的会话复用技术，缺点就是服务器必须保存每个客户端的会话数据，当客户端达到千万级别是存储就会成为瓶颈。第二种基于`session Ticket`，类似`http`的`cookie`，存储的责任由服务器转移到了客户端，服务器加密会话信息，用`New Session Ticket`消息发给客户端让其保存。

 * 预共享密钥（Pre-shared key），在TLS 1.3中已经将`session ID`和`session Ticket`移除，只能使用`PSK`实现会话复用。

关于`Nginx`证书配置参考：
```shell
listen                     443 ssl;
ssl_certificate            xxx_rsa.crt;
ssl_certificate_key        xxx_rsa.key;

# 将http都跳转至https；
return 301 https://$host$request_uri;             # 永久重定向
rewrite ^  https://$host$request_uri permanent;   # 永久重定向

# 强制指定tls协议为1.2
ssl_protocols              TLSv1.2 TLSv1.3;

# 打开session_ticket会话复用；
ssl_session_timeout        5m;
ssl_session_tickets        on;
ssl_session_ticket_key     ticket.key

# 建议以服务器的套件优先配置，这里只是举例说明；
ssl_prefer_server_ciphers   on;
ssl_ciphers   ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-CHACHA20-POLY1305:ECDHE+AES128:!MD5:!SHA1;
```
