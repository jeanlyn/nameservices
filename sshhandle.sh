#!/usr/bin/env bash
#usage:
#   bash sshhandle.sh hadoophome scpfile host1 host2
#   主要用于远程传输文件：第一个参数是远程的目录地址 第二个参数是传输的文件 之后的参数是host的列表

if [ $# -lt 3 ]; then
    echo "too few argument"
    echo "需要输入如下的参数："
    echo "1.hadoophome的目录"
    echo "2.复制的文件"
    echo "3.datanode的host信息"
    exit 1
fi
REMOTE_DIR=$1
echo "the remote DIR is $REMOTE_DIR"
shift
COPYFILE=$1
shift
for i in $@;do
    scp -r $COPYFILE $i:$REMOTE_DIR
done
