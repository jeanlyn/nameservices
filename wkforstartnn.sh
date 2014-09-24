#!/usr/bin/env bash
#输入的参数：
#1.hadoop_home
#2.dfs.nn.dir目录
#3.namenode1
#4.namenode2

if [ $# -ne 5 ];then
    echo "必须输入下面的四个参数："
    echo "1.hadoophome"
    echo "2.dfs.nn.dir目录"
    echo "3.clusterid"
    echo "4.namenode1"
    echo "5.namenode2"
    exit 1
fi

HADOOP_HOME=$1
NAMENODE_DIR=$2
CLUSTERID=$3
NAMENODE1=$4
NAMENODE2=$5

HDOOP_DAEMON=$HADOOP_HOME/sbin/hadoop-daemon.sh
HDFS_COMMAND=$HADOOP_HOME/bin/hdfs

SUFFIX="`date +'%Y%m%d%H%M'`"
#1.备份NAMENODE DIR
ssh $NAMENODE1 "if [ -d $NAMENODE_DIR ];then mv -r ${NAMENODE_DIR} ${NAMENODE_DIR}_${SUFFIX}; fi"

ssh $NAMENODE2 "if [ -d $NAMENODE_DIR ];then mv -r ${NAMENODE_DIR} ${NAMENODE_DIR}_${SUFFIX}; fi"

#2.创建 NAMENODE_DIR
ssh $NAMENODE1 "mkdir -p $NAMENODE_DIR"

ssh $NAMENODE2 "mkdir -p $NAMENODE_DIR"

#3.format zkfc and jn and namenode
ssh $NAMENODE1 "$HDFS_COMMAND zkfc -formatZK"
ssh $NAMENODE1 "$HDFS_COMMAND namenode -format -clusterId $CLUSTERID"
ssh $NAMENODE2 "$HDFS_COMMAND namenode -bootstrapStandby"

#4.启动namenode以及zkfc
ssh $NAMENODE1 "$HDOOP_DAEMON start namenode"
ssh $NAMENODE2 "$HDOOP_DAEMON start namenode"

