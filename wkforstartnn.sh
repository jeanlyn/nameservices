#!/usr/bin/env bash
#输入的参数：
#1.hadoop_home
#2.dfs.nn.dir目录
#3.namenode1
#4.namenode2

if [ $# -ne 4 ];then
    echo "必须输入下面的四个参数："
    echo "1.hadoophome"
    echo "2.dfs.nn.dir目录"
    echo "3.namenode1"
    echo "4.namenode2"
    exit 1
fi

HADOOP_HOME=$1
NAMENODE_DIR=$2
NAMENODE1=$3
NAMENODE2=$4

#1.备份NAMENODE DIR
ssh $NAMENODE1 "if [ -d $NAMENODE_DIR ];then mv ${NAMENODE_DIR} ${NAMENODE_DIR}.BAK fi"

ssh $NAMENODE1 "if [ -d $NAMENODE_DIR ];then mv ${NAMENODE_DIR} ${NAMENODE_DIR}.BAK fi"

#2.创建 NAMENODE_DIR
ssh $NAMENODE1 "mkdir -p $NAMENODE_DIR"

ssh $NAMENODE2 "mkdir -p $NAMENODE_DIR"