#encoding=utf-8
import logging
import os
import re
import commands


def getlog(loggername,loggerfile):
    logger = logging.getLogger(loggername)
    logger.setLevel(logging.DEBUG)
    # 创建一个handler，用于写入日志文件
    fh = logging.FileHandler(loggerfile)
    fh.setLevel(logging.DEBUG)
    # 再创建一个handler，用于输出到控制台
    ch = logging.StreamHandler()
    ch.setLevel(logging.WARNING)
    # 定义handler的输出格式
    formatter = logging.Formatter('%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    # 给logger添加handler
    logger.addHandler(fh)
    logger.addHandler(ch)
    # 记录一条日志
    return logger



#日志配置
def runshcommand(cmd):
    log=getlog('tool','tool.log')
    status,result=commands.getstatusoutput(cmd)
    if status !=0 :
        log.error("there is someting wrong:"+result)
        return None
    else:
        return result.split('\n')

