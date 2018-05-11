# -*- coding: utf-8 -*-
from __future__ import print_function
# from __future__ import unicode_literals
import time
import os
import yaml
import commands as subprocess
import pymongo
import json
from Logger import Logger
#TODO: yaml回写配置的时候，写入了缩写的形式，虽可以正常使用，但是看起来麻烦，其他功能都OK后，再处理这个
# 打印与日志
log = Logger('all.log',level='debug')
p = log.logger


# 检查端口是否已被占用，若已经被占用，抛出异常
def pre_check(port,disk,mongo_version,prefix):
    p.info('now in pre chec')
    cmd = 'netstat -ntulp|grep mongod|grep {}'.format(port)
    status, output = subprocess.getstatusoutput(cmd)
    if status == 0:
        p.error('the port U choose is used,please check again')
        raise Exception
    base_path = '/data{}/{}_{}_port_{}'.format(disk,prefix, mongo_version, port)
    if os.path.exists(base_path):
        p.error('path already exists,please check again')
        raise Exception

# 询问安装单实例的版本：默认/home/dba/dba-tool/tool/mongodb-3.6/bin/mongod
def get_version(mongo_version):
    try:
        input_value = input('please choose you mongod version,type 2 for 3.2,other for 3.6')
        if input_value == 2:
            p.info('U have choose 3.2 version,\nlocate in /home/dba/dba-tool/tool/mongodb-3.2/bin/mongod')
            mongo_version = 32
        elif input_value == 1:
            p.info('U have choose 3.6 version,\nlocate in /home/dba/dba-tool/tool/mongodb-3.6/bin/mongod')
            mongo_version = 36
    except Exception:
        p.info('U don`t type in ,We suppose it well be 3.6')
        mongo_version = 36
    return mongo_version


# 根据返回的版本，给出目录前缀
def bin_prefix(mongo_version):
    if mongo_version == 32:
        bin_prefix = '/home/dba/dba-tool/tool/mongodb-3.2/bin/'
    if mongo_version == 36:
        bin_prefix = '/home/dba/dba-tool/tool/mongodb-3.6/bin/'
    return bin_prefix



# 创建文件夹
def make_dir(disk, mongo_version, port,prefix):
    p.debug('now in make dir')
    base_path = '/data{}/{}_{}_port_{}/'.format(disk, prefix, mongo_version, port) 
    data_path = '{}/data/'.format(base_path)
    log_path = '{}/log/'.format(base_path)
    log_file = '{}/log/{}_{}_port_{}.log'.format(base_path, prefix, mongo_version, port)
    p.debug(repr(base_path))
    try:
        os.makedirs(data_path)
        os.makedirs(log_path)
        return base_path, data_path, log_file
    except Exception:
        p.error(os.listdir(base_path))
        p.error('Create data dir failed,please check')
        raise Exception

# 生成密钥
def generate_keyfile(base_path):
    os.chdir(base_path)
    cmd = 'openssl rand -base64 400 >mongodb-keyfile'
    try:
        status, output = subprocess.getstatusoutput(cmd)
        if status != 0:
            raise Exception
    except Exception:
        p.error('generate key file failed')
        raise Exception

# 创建密钥
def write_keyfile(base_path,keystring):
    cmd ='''echo "{}" >{}/mongo_keyfile'''.format(keystring,base_path)
    try:
        status, output = subprocess.getstatusoutput(cmd)
        if status == 0:
            os.chmod('''{}/mongo_keyfile'''.format(base_path),0o400)
        if status != 0:
            raise Exception
    except Exception:
        p.error('recite keystring failed')
        raise Exception


# 配置文件生成
def mod_conf(disk, mongo_version, port, replsetName=None,role=None,prefix=None):
    try:
        p.debug('now in mod conf')
        base_path = '/data{}/{}_{}_port_{}'.format(disk,prefix, mongo_version, port)
        data_path = '{}/data'.format(base_path)
        log_file = '{}/log/{}_{}_port_{}.log'.format(base_path, prefix, mongo_version, port)
        pid_file = '{}/{}_{}_port_{}.pid'.format(base_path, prefix, mongo_version, port)
        keyfile_name = '{}/mongo_keyfile'.format(base_path)
        p.debug(log_file)
        # 读取原本的单实例配置文件，并修改相关变量，在数据的根目录下写入新的配置文件，mongod_version_port.conf
        with open('conf/mongod_20001.conf', 'rt') as mongo_conf_file:
            tmp = mongo_conf_file.read()
        mongo_conf = yaml.load(tmp)
        if not role:
            role = 'mongod'
        new_conf = '{}/{}_{}_port_{}.conf'.format(base_path,prefix, mongo_version, port)
        p.debug(new_conf)
        with open(new_conf, 'wt') as mongo_conf_file:
            p.debug('now in write conf')
            mongo_conf['net']['port'] = port
            p.debug(pid_file)
            mongo_conf['processManagement']['pidFilePath'] = pid_file
            mongo_conf['systemLog']['path'] = log_file
            mongo_conf['storage']['dbPath'] = data_path
            mongo_conf['storage']['wiredTiger']['engineConfig']['cacheSizeGB'] = 1
            # YAML回写的时候会把off自动改写成false，这里需要手工指定
            mongo_conf['operationProfiling']['mode'] = 'off'
            p.debug(mongo_conf)
            # 如果replsetName存在（判断：不为None）
            p.debug(replsetName)
            if replsetName is not None:
                mongo_conf['replication'] = {'replSetName':replsetName}
                mongo_conf['security'] = {'keyFile':keyfile_name}
            p.debug(replsetName)
            yaml.dump(mongo_conf, mongo_conf_file)
        return new_conf
    except Exception:
        p.error('config file mod failed')
        raise Exception


# 启动实例
def start_instant(bin_prefix, conf):
    cmd = '{}/mongod -f {}'.format(bin_prefix, conf)
    status, output = subprocess.getstatusoutput(cmd)
    if status != 0:
        p.error('start instance failed')
        p.error(output)
        raise Exception


# 检查实例启动情况
def check_alive(port):
    cmd = 'netstat -ntulp|grep mongod'
    status, output = subprocess.getstatusoutput(cmd)
    try:
        if status == 0:
            if output.find('{}'.format(port)) != -1:
                p.info('Instance start ok,{} is serving'.format(port))
            else:
                p.error('can`t find port')
                raise Exception
        else:
            raise Exception
    except Exception:
        p('Specified port is not online')
        raise Exception

# 添加repset 节点
def regist_instance_to_replset(primaryIP, port, secondaryIP, priority, arbiterOnly, root_user, root_password, bin_prefix):
    # 若其为仲裁节点，将其priority重置为0
    if arbiterOnly == 'true':
        priority = 0
    mongo_cmd = 'rs.add({host:{},priority:{},{})'.format(secondaryIP,priority,arbiterOnly)
    cmd = '''{}/mongo --host={}:{} admin -u{} -p{} --eval "{}" '''.format(bin_prefix,primaryIP,port,root_user,root_password,mongo_cmd)
    status,output = subprocess.getstatusoutput(cmd)
    if status != 0:
        p.error('regist instance to replset failed')
        raise Exception

# ！！未完成，repset 初始化,只能在操作机上使用,下发给所有的实例，若权重大的IP为本机IP，就执行初始化， 若不是，不执行
def intitate_repset(IP1,priority1,IP2,priority2,IP3,priority3):
    dict = {"IP1": "priority1", "IP2": "priority2", "IP3": "priority3"}
    dict = {"{}".format(IP1): "{}", "{}": "{}", "{}": "{}"}

# 为实例创建一个admin库鉴权的root角色用户，用户名为root,密码为sa123456
def create_root_user(port, user_name, password):
    client = pymongo.MongoClient('127.0.0.1',port)
    db = client.admin
    db.command("createUser", "{}".format(user_name), pwd="{}".format(str(password)), roles=["root"])


# 连接本机Mongo
class Mongo:

    def __init__(self,  host, port,username=None, password=None, authSource=None):
        p.debug('class init begins')
        port = int(port)
        self.host = host
        self.port = port
        p.debug(type(port))
        self.username = username
        self.password = password
        p.debug(self.password)
        if username is None and password is None:
            p.debug(host)
            p.debug('username is None and password is None')
            self.client = pymongo.MongoClient(host, port, authMechanism='SCRAM-SHA-1')
        elif authSource is None:
            p.debug('authSource is None')
            self.client = pymongo.MongoClient(host, port, username=username, password=password, authSource=admin,
                                              authMechanism='SCRAM-SHA-1')
        else:
            self.client = pymongo.MongoClient(host, port, username=username, password=password, authSource=authSource,
                                              authMechanism='SCRAM-SHA-1')
        p.debug('class init ok')
    # 放最后操作,拼接有问题，暂时不用
    def init_rs(self,TrueIP,replsetname,priority):
        p.debug('start init rs')
        p.debug({'_id':'{}'.format(replsetname),'members':[{'host':'{}:{}'.format(TrueIP,port),'priority':'{}'.format(priority)}]})
        self.client.admin.command('replSetInitiate',"{_id:'{}',members:[{host:'{}:{}',priority:{}}]}".format(replsetname,TrueIP,port,priority))

def init_rs(host,port,ip,replsetname,priority):
    mongo_cmd = 'rs.initiate({host:{},priority:{},{})'.format(secondaryIP,priority,arbiterOnly)
    cmd = '''{}/mongo --host={}:{} admin -u{} -p{} --eval "{}" '''.format(bin_prefix,primaryIP,port,root_user,root_password,mongo_cmd)


if __name__ == '__main__':
    p.debug('test print')