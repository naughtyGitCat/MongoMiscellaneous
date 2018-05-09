# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
import sys
import time
import getopt
import re
import os
import yaml
import subprocess
#全局参数


#TODO: yaml回写配置的时候，写入了缩写的形式，虽可以正常使用，但是看起来麻烦，其他功能都OK后，再处理这个

# ip:port#disk/buffer#role#priority
#192.168.1.151:30000#3/20#primary#90

# 读取参数
def read_args():
    opts,args = getopt.getopt(sys.argv[1:],'i:')
    print('opts:',opts)
    for opt,value in opts:
        print('opt:', opt)
        ip = re.split(':|#|/', value)[0]
        port = re.split(':|#|/', value)[1]
        disk = re.split(':|#|/', value)[2]
        buffer = re.split(':|#|/', value)[3]
        role = re.split(':|#|/', value)[4]
        priority = re.split(':|#|/', value)[5]
    print('ip+port:', ip, ':', port, '\ndisk:', disk, '\nbuffer:', buffer,'GB', '\nrole:', role, '\npriority:', priority )
    return ip, port, disk, buffer, role, priority
read_args()

# 带日期打印
def p(a):
    now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    print(now, ' ', a)

# 询问安装单实例的版本：默认/home/dba/dba-tool/tool/mongodb-3.6/bin/mongod
def get_version(mongo_version):
    try:
        input_value = input('please choose you mongod version,type 2 for 3.2,other for 3.6')
        if input_value == 2:
            p(u'U have choose 3.2 version,\nlocate in /home/dba/dba-tool/tool/mongodb-3.2/bin/mongod')
            mongo_version = 32
        elif input_value == 1:
            p(u'U have choose 3.6 version,\nlocate in /home/dba/dba-tool/tool/mongodb-3.6/bin/mongod')
            mongo_version = 36
    except Exception:
        p('U don`t type in ,We suppose it well be 3.6')
        mongo_version = 36
    return mongo_version

# 根据返回的版本，给出目录前缀
def bin_prefix(mongo_version):
    if mongo_version == 32:
        bin_prefix='/home/dba/dba-tool/tool/mongodb-3.2/bin/'
    if mongo_version == 36:
        bin_prefix='/home/dba/dba-tool/tool/mongodb-3.6/bin/'
    return bin_prefix

# 创建文件夹
def mkdir(disk,mongo_version,port):
    base_path = '/data{}/mongodb_{}_port_{}'.format(disk, mongo_version, port)
    data_path = '{}/data'.format(base_path)
    log_file = '{}/log/mongodb_{}_port_{}.log'.format(base_path, mongo_version, port)
    try:
        os.makedirs(base_path, exist_ok=False)
        os.makedirs(data_path, exist_ok=False)
        os.makedirs(log_file, exist_ok=False)
    except Exception:
        p('创建目录失败，请检测是否已有同名目录')

# 配置文件生成
def mod_conf(disk, mongo_version, port):
    try:
        base_path = '/data{}/mongodb_{}_port_{}'.format(disk, mongo_version, port)
        data_path = '{}/data'.format(base_path)
        log_file = '{}/log/mongodb_{}_port_{}.log'.format(base_path, mongo_version, port)
        pid_file= '{}/mongodb_{}_port_{}.pid'
        # 读取原本的单实例配置文件，并修改相关变量，在数据的根目录下写入新的配置文件，mongod_version_port.conf
        with open('mongod_20001.conf', 'rt') as mongo_conf_file:
            tmp = mongo_conf_file.read()
        mongo_conf = yaml.load(tmp)
        new_conf = '{}/mongodb_{}_port_{}'.format(base_path, mongo_version, port)

        with open(new_conf, 'wt') as mongo_conf_file:
            mongo_conf['net']['port'] = port
            mongo_conf['processManagement']['pidFilePath'] = pid_file
            mongo_conf['systemLog']['path'] = log_file
            mongo_conf['storage']['dbPath'] = data_path
            mongo_conf['storage']['wiredTiger']['engineConfig']['cacheSizeGB'] = 1
            # yaml回写的时候会把off自动改写成false，这里需要手工指定
            mongo_conf['operationProfiling']['mode'] = 'off'
            yaml.dump(mongo_conf, mongo_conf_file)
        return new_conf
    except Exception:
        p('配置文件写入失败，请检查')
        raise Exception

# 启动实例
def start_instant(bin_prefix,conf):
    cmd = '{}/mongod -f '
    status, output =subprocess.getstatusoutput(cmd)
