#!/usr/bin/env python
#encoding=UTF-8

from tool.hconf import *
from tool.tool import *
import ConfigParser 

log = getlog('addnameservice','addnameservice.log')
import argparse

class nameservice:
    def __init__(self,conf_file='conf/conf.ini'):
        self.cf = ConfigParser.ConfigParser()
        self.cf.read(conf_file)
        self.namenodefile = self.cf.get("namenode","hdfsxml")
        self.nnconf= HadoopConf(self.namenodefile) #将配置文件转化成字典格式如下: {'name':{'value':value,'description':desc}}
        log.info('getting namenodefile' + self.namenodefile)
        dt = self.nnconf.get()
        self.nss = {}
        #获取ns名称,以及对应的namenode名称
        if dt.get('dfs.nameservices',None) is not None:
            for x in dt['dfs.nameservices']['value'].split(','):
                self.nss[x] = dt.get('dfs.ha.namenodes'+'.'+x,None)['value'].split('') if dt.get('dfs.ha.namenodes'+'.'+x,None) is not None else []
        

    def addnameservice(nameservice,namenode1,namenode2):
        pass


                  

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-ns",action='store',dest='ns',help='[必须输入]nameserver名称,在集群里需要唯一')
    parser.add_argument("-nn1",action='store',dest='nn1',help='[必须输入]输入新的namenode的名称')
    parser.add_argument("-nn2",action='store',dest='nn2',help='[必须输入]目前只是支持ha的配置所以需要输入两个nn')
    parser.add_argument("-nnhttpport",action='store',dest='nnhttpport',default='50070',help='namenode的http的端口，默认50070')
    parser.add_argument("-nnrpcport",action='store',dest='nnrpcport',help='namenode的rpc端口，默认的8020')
    results = parser.parse_args()
    if results.ns and results.nn1 and results.nn2:
        print results.ns,results.nn1,results.nn2
    else:
        print "输入有误，使用-h查看输入"
    
    namenode = HaConf()



