#!/usr/bin/env bash
#至少需要輸入兩個參數，第一个参数为hadoop的目录，剩余的参数为datanode的host
if [ $# -lt 2 ]; then
    echo "至少需要输入三个以上的参数"
    exit 1
fi

HADOOP_HOME=$1
HADOOP_COMMAND=$HADOOP_HOME/bin/hdfs
shift

DATANODE_RPC_PORT=$1
shift

for i in $@;do
    $HADOOP_COMMAND dfsadmin -refreshNamenodes $i:$DATANODE_RPC_PORT &
done
wait