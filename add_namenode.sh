#!/usr/bin/env bash
function isContinue(){
    echo $1
    read -p "是否继续?[y|n]"
    while [[ $REPLY != "y" && $REPLY != "n" ]]
    do
        read -p "$@ 输入有误，是否继续：[y|n]"
    done
    if [ $REPLY != "y" -a $REPLY != "Y" ];then
       echo "----------------------------------------"
       echo "程序退出！"
       echo "----------------------------------------"
       exit 1
    else
       return 0
    fi
}
#设置参数
bak_stufix=$(date -d "today" +%Y%m%d%H%m%S)
clusterId="CID-3f36397d-b160-4414-b7e4-f37b72e96d53"
namenode1="172.22.167.71"
namenode2="172.22.167.72"
HADOOP_HOME="/software/servers/hadoop-2.2.0"
dnRpcport="50020"
#前置检查
if [ ! -f $HADOOP_HOME/etc/hadoop/slaves ];then
    echo "slaves文件不存在"
    exit 1
fi

echo "将要添加以下两个namenode，请确认："
echo $namenode1" "$namenode2
isContinue

#通过ssh format第一个增加的namenode
echo "-----------------------------"
echo "[1/4]正在format:$namenode1 ..."
echo "-----------------------------"

ssh $namenode1 "
if [ -d /data0/nn ];then
    echo \"正在将/data0/nn移至/data0/nn.bak_$bak_stufix,请稍等...\"
    mv /data0/nn /data0/nn.bak_$bak_stufix
fi

${HADOOP_HOME}/bin/hdfs namenode -format -clusterId $clusterId
${HADOOP_HOME}/sbin/hadoop-daemon.sh start namenode
" 
if [ $? != 0 ];then
    isContinue "format $namenode1发生错误，是否继续？"
fi

#通过ssh format第二个namenode
echo "-----------------------------"
echo "[2/4]正在format:$namenode2 ..."
echo "-----------------------------"

ssh $namenode2 "
if [ -d /data0/nn ];then
    echo \"正在将/data0/nn移至/data0/nn.bak_$bak_stufix,请稍等...\"
    mv /data0/nn /data0/nn.bak_$bak_stufix
fi
${HADOOP_HOME}/bin/hdfs namenode -bootstrapStandby
${HADOOP_HOME}/sbin/hadoop-daemon.sh start namenode
" 
if [ $? != 0 ];then
    isContinue "format $namenode2发生错误，是否继续？"
fi

echo "---------------------------------"
echo "[3/4]正在刷新datanode的namenode..."
echo "---------------------------------"
#并发刷新datanode
#-------------------并发刷新datandoe,并且控制并发数
THEAD_NUM=100
#定义描述符为9的管道
mkfifo tmpcp
exec 9<>tmpcp

for ((i=0;i<$THEAD_NUM;i++))
do
    echo -ne "\n" 1>&9
done

for i in  $(cat $HADOOP_HOME/etc/hadoop/slaves);do
    read -u 9
    {
        ssh $i "$HADOOP_HOME/bin/hdfs dfsadmin -refreshNamenodes $i:$dnRpcport"
        if [ $? -ne 0 ];then
            echo "${i}刷新namenode出现问题"
            echo $i >>errornode
        else 
            echo $i >>successnode
        fi
        echo -ne "\n" 1>&9
    }&
done

wait
/bin/rm tmpcp

echo "--------------------------------"
echo "[4/4]正在启动两个namenode的zkfc..."
echo "--------------------------------"
ssh $namenode1 "$HADOOP_HOME/sbin/hadoop-daemon.sh start zkfc"
ssh $namenode2 "$HADOOP_HOME/sbin/hadoop-daemon.sh start zkfc"
