# -*- coding: utf-8 -*-
from __future__ import print_function
# from __future__ import unicode_literals
import sys
import time
import getopt
import re
import os
import yaml
import commands as subprocess
import pymongo
from functions import bin_prefix,make_dir,generate_keyfile,mod_conf,p,pre_check,write_keyfile
from functions import  start_instant,check_alive,regist_instance_to_replset,Mongo,create_root_user
# TODO:复制集开放的IP问题
prefix = ''
def read_args():
    #c configServer
    #s mongos
    #ar regist instance to repSet
    #as add shard
    global prefix
    opts,args = getopt.getopt(sys.argv[1:],'i:r:c:s:ar:as:')
    for opt,value in opts:
        # i instance
        if opt == '-i':
            print('opt:', opt)
            ip = re.split(':|#|/', value)[0]
            port = re.split(':|#|/', value)[1]
            disk = re.split(':|#|/', value)[2]
            buffer = re.split(':|#|/', value)[3]
            prefix = 'mongod'
            return ip,port,disk,buffer,prefix
        elif opt == '-r':
            # r repset
            # 192.168.1.151:30000#3/20#primary#repsetname#priority
            ip = re.split(':|#|/', value)[0]
            port = re.split(':|#|/', value)[1]
            disk = re.split(':|#|/', value)[2]
            buffer = re.split(':|#|/', value)[3]
            role = re.split(':|#|/', value)[4]
            replsetname = re.split(':|#|/', value)[5]
            priority = re.split(':|#|/', value)[6]
            prefix = 'shard'
            return ip,port,disk,buffer,role,replsetname,priority,prefix
        elif opt == '-ar':
            # 注册节点到复制集中
            # 192.168.1.151:30000#192.168.1.152#50#arbiterOnly-->|true|false注意大小写
            primaryIP = re.split(':|#|/', value)[0]
            port = re.split(':|#|/', value)[1]
            otherIP = re.split(':|#|/', value)[2]
            priority = re.split(':|#|/', value)[3]
            arbiterOnly = re.split(':|#|/', value)[4]
            prefix = 'add repset'
            return primaryIP,port,otherIP,priority, arbiterOnly, prefix
        elif opt == '-c':
            #192.168.1.151:30000#3/20#primary#90#repsetname
            ip = re.split(':|#|/', value)[0]
            port = re.split(':|#|/', value)[1]
            disk = re.split(':|#|/', value)[2]
            buffer = re.split(':|#|/', value)[3]
            role = re.split(':|#|/', value)[4]
            replsetname = re.split(':|#|/', value)[5]
            prefix = 'configSvr'
            return ip, port, disk, buffer, role, replsetname, prefix
        elif opt == '-s':
            # 192.168.1.151:30000/ConfigSvrIP1/ConfigSvrIP2/ConfigSvrIP3/ConfigSvrPort
            ip = re.split(':|#|/', value)[0]
            port = re.split(':|#|/', value)[1]
            disk = 1
            ConfigSvrIP1 = re.split(':|#|/', value)[2]
            ConfigSvrIP2 = re.split(':|#|/', value)[3]
            ConfigSvrIP3 = re.split(':|#|/', value)[4]
            ConfigSvrPort = re.split(':|#|/', value)[5]
            prefix = 'mongos'

keystring ='''8raIkk38J1t8M3Ae+LqX0jLTnDmy5ypkDcdvdDo01wHYNNyz9w2ceZZ9sVk4EhvC\
              9TItdE5R4aMg0ISQv+G3PK9Xm+eWX25tptjoPNcXR/h085XR2MAfmhgyXwoPeapI\
              yuphWPC1zjteaYVbSwq8edPMm1As9mdPVrClBfNvRXldjW/luC4++Bks+QRiA9kZ\
              dG14IKHEos2ewFz14jq1yehx8lK3PIFUCXwKzjcDjB27VrObLYhAbBlOJIhOQ551\
              HcwG0js6m48o+Mt+j5FRb7JJ0tdUdNybdozMYmSl2AdVTd9WZxBTbZT0r7FhdaAj\
              QUlqZKowuVv6Q3X7TyNFu49n9eW7ZhQT7zgga1IFVkgilwU4YNRmAzGwyb9fnigt\
              8elkoAKAAX5daJomNIlZUQfI2tSlEHQMz7wQNXgM8+xNNp8kHG1DtmygRdy6t4Fp\
              a6DE8gCJ348vR9Ekv9Octd/NOiqHNe7tr+y00pOzNBmjtr62kqaZr8mk/2kaHseX\
              Up7ZqrizV/plWZxVEx/+fA=='''
mongo_version = 36
read_args()
try:
    if prefix == 'shard':
        ip, port, disk, buffer, role, replsetname, priority, prefix = read_args()
        p.debug(prefix)
        p.info('get opts finished')
        # whether port and path been used
        # pre_check(port,disk,mongo_version,prefix)
        # p.info('pre check finished')
        # make base path,data path,log_path and return,different shard role use different prefix
        # base_path, data_path, log_file = make_dir(disk, mongo_version, port,prefix)
        # write down the keystring in basepath
        # write_keyfile(base_path,keystring)
        # generate conf file using a single instant conf. according to different prefix add some shard/repSet option
        # conf_file = mod_conf(disk, mongo_version, port, replsetName=replsetname,role=role,prefix=prefix)
        # start instant with -f option
        # bin_prefix = bin_prefix(36)
        # start_instant(bin_prefix, conf_file)
        # check alive by netstat -ntulp|grep mongod > find(port)
        check_alive(port)
        if role == 'primary':
            print('127.0.0.1',port)
            p.debug('now opreate inside mongo')
            instance = Mongo('127.0.0.1', port)
            p.debug('now go to  init_rs')
            instance.init_rs(ip,replsetname,priority)
            create_root_user(port,user_name='root',password='sa123456')
    if prefix == 'add repset':
        try:
            primaryIP, port, otherIP, priority, arbiterOnly, prefix = read_args()
            regist_instance_to_replset(primaryIP,port,otherIP,priority,arbiterOnly,root_user='root',root_password='sa123456')
        except Exception:
            p.error('regist_instance_to_replset failed')
    else:
        p.info('It has been add to TODO list')
except Exception:
    p.error('error,stopped')


