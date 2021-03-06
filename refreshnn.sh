#!/usr/bin/env bash
#至少需要輸入兩個參數，第一个参数为hadoop的目录，剩余的参数为datanode的host
if [ $# -lt 3 ]; then
    echo "刷新datanode的nameservice信息至少需要输入三个以上的参数"
    echo "1.hadoophome"
    echo "2.datanode的rpcport"
    echo "3....datanode列表"
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
