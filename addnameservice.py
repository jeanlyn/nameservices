#!/usr/bin/env python
#encoding=UTF-8

from tool.hconf import *
from tool.tool import *
import ConfigParser 
import sys

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
        cf = ConfigParser.ConfigParser()
        cf.read(conf_file)
        self.namenodefile = cf.get("namenode","hdfsxml")
        self.nnrpcport = cf.get('namenode','rpcport')
        self.nnhttpport = cf.get('namenode','httpport')
        self.nnconf = HadoopConf(self.namenodefile) #将配置文件转化成字典格式如下: {'name':{'value':value,'description':desc}}
        log.info('getting namenodefile: ' + self.namenodefile)
        dt = self.nnconf.get()
        self.nss = {}
        #获取ns名称,以及对应的namenode名称,构造
        if dt.get('dfs.nameservices',None) is not None:
            for x in dt['dfs.nameservices']['value'].split(','):
                self.nss[x] = dt.get('dfs.ha.namenodes'+'.'+x,None)['value'].split(',') if dt.get('dfs.ha.namenodes'+'.'+x,None) is not None else []
        
    #增加nameserviece之前进行检查
    def addprecheck(self,nameservice,namenode1,namenode2):
        if namenode1 == namenode2:
            log.warn("两个namenode名字不能一样！")
            return Process.FAIL
        if [] in self.nss.values():
            log.warn("nameservice 里面有空值，请检查配置！")
            return Process.FAIL
        if namenode1 in self.nss.values() or namenode2 in self.nss.values():
            log.warn("namenode 已经存在！")
            return Process.FAIL
        if self.nss.get(nameservice,None) is not None:
            log.warn("nameservice已经存在！")
            return Process.FAIL
        dt = self.nnconf.get()
        if dt.get('dfs.namenode.shared.edits.dir',None) is None:
            log.warn("原来的配额没有配置dfs.namenode.shared.edits.dir!")
            return Process.FAIL
        elif dt['dfs.namenode.shared.edits.dir']['value'].split(':')[0] != 'qjournal':
            log.warn("目前ha只支持使用QJM，请为原来的ha模式使用QJM的配置")
            return Process.FAIL
        if dt.get('dfs.namenode.name.dir',None) is None:
            log.warn("dfs.namenode.name.dir没有设置！")
            return Process.FAIL
        return Process.SUCCESS
    
    #增加nameservice
    def addnameservice(self,parser):     
        #初始化变量
        nnrpcport = self.nnrpcport
        nnhttpport = self.nnhttpport
        nameservice = parser.ns
        namenode1 = parser.nn1
        namenode2 = parser.nn2
        if nameservice is None or namenode1 is None or namenode2 is None:
            log.warn('输入的参数有误！使用 addns -h 查看具体使用')
            return Process.FAIL   
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
                hdfsconf['.'.join(['dfs.namenode.rpc-address',nameservice,x])]={'value':x+':'+nnrpcport}
                hdfsconf['.'.join(['dfs.namenode.http-address',nameservice,x])]={'value':x+':'+nnhttpport}
            #设置share.edit.dir:一般形式为qjournal://host1:8485,host2:8485/nameservice
            hdfsconf['dfs.namenode.shared.edits.dir']={'value':'/'.join(hdfsconf['dfs.namenode.shared.edits.dir']['value'].split('/')[:-1]+[nameservice])}
            newhdfsxml = newnsdir + '/hdfs-site.xml'
            newhdfsconf = HadoopConf(newhdfsxml)
            #将字典写回文件
            self.nnconf.setdt(hdfsconf)
            newhdfsconf.setdt(hdfsconf)

    #删除nameservicer
    def removenameservice(self,parser):
        nameservice = parser.ns
        if nameservice is None:
            log.warn('输入的参数有无，必须使用-ns输入nameservicer名称')
            return Process.FAIL        
        hdfsconf = self.nnconf.get()
        originns = hdfsconf['dfs.nameservices']['value'].split(',')
        if nameservice not in originns:
            log.warn('nameservicer并不存在，请检查名称：' + nameservice )
            return Process.FAIL
        namenodes = hdfsconf['dfs.ha.namenodes.'+nameservice]['value'].split(',')
        namenodehosts = [ hdfsconf['dfs.namenode.rpc-address.'+nameservice+'.'+x]['value'].split(':')[0] for x in namenodes ]
        #1.删除dfs.nameservices以及dfs.ha.namenode配置
        originns.remove(nameservice)
        hdfsconf['dfs.nameservices']['value'] = ','.join(originns)
        if hdfsconf.get('dfs.ha.namenodes.'+nameservice,None) is not None:
            del hdfsconf['dfs.ha.namenodes.'+nameservice]
        #2.删除http-adrees以及rpc-adress
        for x in list(set(namenodes)):
            if hdfsconf.get('dfs.namenode.rpc-address.'+nameservice+'.'+x,None) is not None:
                del hdfsconf['dfs.namenode.rpc-address.'+nameservice+'.'+x] 
            if hdfsconf.get('dfs.namenode.http-address.'+nameservice+'.'+x,None) is not None:
                del hdfsconf['dfs.namenode.http-address.'+nameservice+'.'+x]
        #3.删除文件夹
        runshcommand('/bin/rm -r conf/'+nameservice)
        self.nnconf.setdt(hdfsconf)


    #列出nameservicer
    def lsnameservice(self,parser):
        try:
            hdfsconf = self.nnconf.get()

            for i in hdfsconf['dfs.nameservices']['value'].split(','):
                print(i)
        except Exception, e:
            log.error(e)               
        return Process.SUCCESS

    #列出namenodes
    def lsnamenodes(self,parser):
        try:          
            hdfsconf = self.nnconf.get()
            for nameservice,namenodes in zip(self.nss.keys(),self.nss.values()):
                namenodehosts = [ (x,hdfsconf['dfs.namenode.rpc-address.'+nameservice+'.'+x]['value'].split(':')[0]) for x in namenodes ]
                for k,v in namenodehosts:
                    print(k+': '+v)
        except Exception, e:
            log.error(e)
        else:
            pass
        finally:
            pass
        return Process.SUCCESS


if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers(help='commands')

    lisparser = subparsers.add_parser('lsns',help='列出现在的nameservicer')

    lisnnparser = subparsers.add_parser('lsnn',help='列出所有的namenode')

    addns_parser = subparsers.add_parser('addns',help='增加nameserver')
    addns_parser.add_argument("-ns",action='store',dest='ns',help='[必须输入]nameserver名称,在集群里需要唯一')
    addns_parser.add_argument("-nn1",action='store',dest='nn1',help='[必须输入]输入新的namenode的名称')
    addns_parser.add_argument("-nn2",action='store',dest='nn2',help='[必须输入]目前只是支持ha的配置所以需要输入两个nn')
    # addns_parser.add_argument("-nnhttpport",action='store',dest='nnhttpport',default='50070',help='namenode的http的端口，默认50070')
    # addns_parser.add_argument("-nnrpcport",action='store',dest='nnrpcport',default='8020',help='namenode的rpc端口，默认的8020')

    removeparser = subparsers.add_parser('rmns',help='删除nameservicer')
    removeparser.add_argument('-ns',action='store',dest='ns',help='[必须输入]要删除的nameserver名称')

    results = parser.parse_args()
    ns = nameservice()
    runmethod = {
                 'lsns':ns.lsnameservice,
                 'addns':ns.addnameservice,
                 'lsnn':ns.lsnamenodes,
                 'rmns':ns.removenameservice
                }
    runmethod[sys.argv[1]](results)

        
    



