#!/bin/bash
## name XiaoYi
## email: yang972711021@gmail.com
## 解决Centos 6出现libc.so.6: version 'GLIBC_2.14' not found问题


strings /lib64/libc.so.6 |grep GLIBC_


yum install -y  curl openssh-server openssh-clients postfix cronie git nmap unzip wget lsof xz gcc make vim  curl gcc-c++ libtool

cd /opt 
wget http://ftp.gnu.org/gnu/glibc/glibc-2.24.tar.gz

tar zxvf glibc-2.24.tar.gz 
cd glibc-2.24
mkdir build && cd build

cp /etc/ld.so.conf /opt/glibc-2.24/etc/
../configure --prefix=/opt/glibc-2.24
make -j4
make install

export LD_LIBRARY_PATH=/opt/glibc-2.24/lib:$LD_LIBRARY_PATH
