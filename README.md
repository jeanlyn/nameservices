#简介
该脚本的主要作用是用于比较方便为已经运行的集群添加nameservicer

#功能
-   增加nameservice
-   删除nameservice
-   查看配置文件里配置的nameserver
-   查看配置文件里已经配置的namenode
-   根据输入查找hdfs-site.xml配置里面相应的内容

#主要功能的操作步骤
##增加nameservice
1.  根据输入的参数进行检查，防止原有的集群已经配置
2.  根据输入的参数对本地的相应的配置进行修改
3.  将修改好的文件传送到datanode以及需要修改的namenode的hadoop的目录下
4.  在新加入的两个namenode根据`dfs.namenode.name.dir`创建目录
5.  运行`hdfs -format -clusterId $CLUSTERID`格式化其中一个namenode
,对另外一个namenode运行`hdfs namenode -bootstrapStandby`去拷贝已经
以及启动namenode。**注意:**启动namenode之后还不能启动zkfc服务
6.  运行`hdfs dfsadmin -refreshNamenodes $i:$DATANODE_RPC_PORT`.**DATANODE_RPC_PORT**为集群上每一个datanode的host

##删除nameservice
1.  检查输入的ns是否存在
2.  修改配置
3.  分发修改的配置到集群上的每个datanode以及删除的两个namenode上
4.  停止相应的进程
5.  运行`hdfs dfsadmin -refreshNamenodes $i:$DATANODE_RPC_PORT`.**DATANODE_RPC_PORT**为集群上每一个datanode的host

#使用

##前提

该脚本主要是为了已经运行的集群进行添加nameservice的,所以有些东西是需要依赖或者以现有的集群作为标准进行配置

###运行的集群需要有的服务进程包括:
1.  zookeeper因为新加的nameservice都是使用ha的所以需要使用到zookeeper去支持zkfc服务
2.  qjournalnode,作为ha的`shark.edit.dir`
3.  已经存在的datanode

##注意事项
**在运行脚本之前需要进行如下的一些工作**
###检查**conf/conf.ini**
1.**hadoop_home**为集群的hadoop根目录
2.**cluster_id**为现有集群的id,可以在namenode的**dfs.namenode.name.dir/current/VERSION**下查看

    cat VERSION
        namespaceID=318050901
        **clusterID=ns1**
        cTime=0
        storageType=NAME_NODE
        blockpoolID=BP-569750865-172.22.178.63-1410918673402
        layoutVersion=-47

3.**datanodefile**配置本地的路径,存放的是集群的datanode的host信息
4.**namenode下的hdfsxml**配置,这个作为修改配置的主要信息,在运行程序之前需要必须将集群的hdfs-site.xml拷贝到相应的配置目录
5.其他配置的话如果集群是采用默认就不需要修改了

###运行环境
1.  **python2.7+**
2.  可以对集群的节点进行无密码登录即打通ssh

##运行
1.增加nameservice

    ./nameservice.py addns -ns `nsname` -nn1 `namenode1host` -nn2 `namenode2host`

2.删除nameservice

    ./nameservice.py rmns -ns `nsname`

3.查看配置文件里配置的nameserver

    ./nameservice.py lsns

4.查看配置文件里已经配置的namenode

    ./nameservice.py lsnn

5.查找hdfs-site.xml配置

    ./nameservice.py lscf `name`

