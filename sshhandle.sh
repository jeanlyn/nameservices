#!/usr/bin/env bash
#usage:
#   bash sshhandle.sh hadoophome scpfile host1 host2
#   主要用于远程传输文件：第一个参数是远程的目录地址 第二个参数是传输的文件 之后的参数是host的列表

if [ $# -lt 2 ]; then
    echo "too few argument"
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
