#!/usr/bin/env bash
if [ $# -lt 3 ];then
    echo "必须输入三个以上的参数,第一个参数为hadoop的目录，剩余的参数为要停止进程的地址"
    exit 1
fi
HADOOP_HOME=$1
shift
START_STOP=$1
shift
HADOOP_DAEMON=$HADOOP_HOME/sbin/hadoop-daemon.sh

for i in $@;do
    #停止zkfc进程
    ssh $i "$HADOOP_DAEMON $START_STOP zkfc" 
done
wait