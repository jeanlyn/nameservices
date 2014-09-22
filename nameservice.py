#!/usr/bin/env python
#encoding=UTF-8

from tool.hconf import *
from tool.tool import *
import ConfigParser 

log = getlog('addnameservice','addnameservice.log')
import argparse

class Process(object):
    """use for the return value"""
    SUCCESS = 1
    FAIL    = 2
        

class nameservice:
    #检查列表，用于检查原来的配置完整不完整，现在还没有用到
    checklist = ['dfs.ha.fencing.methods','']
    def __init__(self,conf_file='conf/conf.ini'):
        self.cf = ConfigParser.ConfigParser()
        self.cf.read(conf_file)
        self.namenodefile = self.cf.get("namenode","hdfsxml")
        self.nnconf = HadoopConf(self.namenodefile) #将配置文件转化成字典格式如下: {'name':{'value':value,'description':desc}}
        log.info('getting namenodefile' + self.namenodefile)
        dt = self.nnconf.get()
        self.nss = {}
        #获取ns名称,以及对应的namenode名称,构造
        if dt.get('dfs.nameservices',None) is not None:
            for x in dt['dfs.nameservices']['value'].split(','):
                self.nss[x] = dt.get('dfs.ha.namenodes'+'.'+x,None)['value'].split('') if dt.get('dfs.ha.namenodes'+'.'+x,None) is not None else []
        
    #增加nameserviece之前进行检查
    def addprecheck(self,nameservice,namenode1,namenode2):
        if [] in self.nss.values():
            log.info("nameservice 里面有空值，请检查配置！")
            return Process.FAIL
        if namenode1 in self.nss.values() or namenode2 in self.nss.values():
            log.info("namenode 已经存在！")
            return Process.FAIL
        if self.nss.get(nameservice,None) is not None:
            log.info("nameservice已经存在！")
            return Process.FAIL
        dt = self.nnconf.get()
        if dt.get('dfs.namenode.shared.edits.dir',None) is None:
            log.info("原来的配额没有配置dfs.namenode.shared.edits.dir!")
        elif dt['dfs.namenode.shared.edits.dir']['value'].split(':')[0] != 'qjournal':
            log.info("目前ha只支持使用QJM，请为原来的ha模式使用QJM的配置")
        return Process.SUCCESS
    
    #增加nameservice
    def addnameservice(self,nameservice,namenode1,namenode2,nnrpcport='50070',nnhttpport='8020'):        
        if self.addprecheck(nameservice,namenode1,namenode2) == Process.SUCCESS:
            #在conf文件夹下创建新nn的文件夹
            newnsdir = "conf/"+nameservice
            log.info("正在创建"+newnsdir)
            runshcommand('mkdir -p '+newnsdir)
            hdfsconf = self.nnconf.get()
            #增加nameservicers
            hdfsconf['dfs.nameservices'] = {'value':','.join(self.nss.keys()+[nameservice])}
            #增加namenode
            hdfsconf['dfs.ha.namenodes.'+nameservice] = {'value':','.join([namenode1,namenode2])}
            #设置rpc地址以及http地址
            for x in [namenode1,namenode2]:
                hdfsconf['.'.join(['dfs.namenode.rpc-address',nameservice,x])]={'value':x+nnrpcport}
                hdfsconf['.'.join(['dfs.namenode.http-address',nameservice,x])]={'value':x+nnhttpport}
            #设置share.edit.dir:一般形式为qjournal://host1:8485,host2:8485/nameservice
            hdfsconf['dfs.namenode.shared.edits.dir']={'value':'/'.join(hdfsconf['dfs.namenode.shared.edits.dir']['value'].split('/')[:-1]+[nameservice])}
            newhdfsxml = newnsdir + '/hdfs-site.xml'
            newhdfsconf = HadoopConf(newhdfsxml)
            #将字典写回文件
            self.nnconf.setdt(hdfsconf)
            newhdfsxml.setdt(hdfsconf)

    
                  

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-ns",action='store',dest='ns',help='[必须输入]nameserver名称,在集群里需要唯一')
    parser.add_argument("-nn1",action='store',dest='nn1',help='[必须输入]输入新的namenode的名称')
    parser.add_argument("-nn2",action='store',dest='nn2',help='[必须输入]目前只是支持ha的配置所以需要输入两个nn')
    parser.add_argument("-nnhttpport",action='store',dest='nnhttpport',default='50070',help='namenode的http的端口，默认50070')
    parser.add_argument("-nnrpcport",action='store',dest='nnrpcport',default='8020',help='namenode的rpc端口，默认的8020')
    results = parser.parse_args()
    if results.ns and results.nn1 and results.nn2:
        print results.ns,results.nn1,results.nn2
    else:
        print "输入有误，使用-h查看输入"
    
    



