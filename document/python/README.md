# Python 安装

## 1.安装基础环境
```shell
$ yum -y groupinstall "Development tools"
$ yum -y install zlib-devel bzip2-devel openssl-devel ncurses-devel sqlite-devel readline-devel tk-devel gdbm-devel db4-devel libpcap-devel xz-devel
```
下载Python安装包
```shell
$ cd /usr/local/src
$ wget http://mirrors.sohu.com/python/3.6.9/Python-3.6.9.tgz
```

## 2.开始安装
```shell 
$ cd /usr/local/src/
$ tar xf Python-3.6.9.tgz
$ cd Python-3.6.9
$ ./configure --prefix=/usr/local/python3 --enable-shared --enable-loadable-sqlite-extensions --with-zlib --enable-optimizations
$ make && make install
$ make distclean
```
添加到环境
```shell
$ vim /etc/profile
export JAVA_HOME=/usr/local/jdk18
export PYTHON_HOME=/usr/local/python3
export CLASSPATH=.:$JAVA_HOME/jre/lib/rt.jar:$JAVA_HOME/lib/dt.jar:$JAVA_HOME/lib/tools.jar
export PATH="$PYTHON_HOME/bin:$JAVA_HOME/bin:/usr/local/php/bin:/usr/local/nginx/sbin:$PATH"

$ source /etc/profile
```
添加相关库配置
```shell
$ cat /etc/ld.so.conf.d/python3.conf
# 添加python3编译的lib路径
/usr/local/python3/lib

$ ldconfig
```

## 3.配置pip源
```shell
$ mkdir -p  /root/.pip/
$ cat >  /root/.pip/pip.conf   <<EOF
[global]
trusted-host=mirrors.aliyun.com
index-url=http://mirrors.aliyun.com/pypi/simple/
EOF
```
验证
```shell
$ python3 -V
Python 3.6.9
```