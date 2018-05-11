# -*- coding: utf-8 -*-
from __future__ import print_function
# from __future__ import unicode_literals
import sys
import time
import getopt
import re
import yaml
import json
import pymongo
from pprint import pprint
from Logger import Logger
from bson.json_util import loads,dumps
log = Logger('all.log',level='debug')
p = log.logger
from functions import Mongo
# config = dumps(config)
# print(config)
# 连接本机Mongo
# class Mongo:
#
#     def __init__(self,  host, port,username=None, password=None, authSource=None):
#         p.debug('class init begins')
#         self.host = host
#         self.port = port
#         self.username = username
#         self.password = password
#         p.debug(self.password)
#         if username is None and password is None:
#             p.debug('username is None and password is None')
#             self.client = pymongo.MongoClient(host, port, authMechanism='SCRAM-SHA-1')
#         elif authSource is None:
#             p.debug('authSource is None')
#             self.client = pymongo.MongoClient(host, port, username=username, password=password, authSource=admin,
#                                               authMechanism='SCRAM-SHA-1')
#         else:
#             self.client = pymongo.MongoClient(host, port, username=username, password=password, authSource=authSource,
#                                               authMechanism='SCRAM-SHA-1')
#         p.debug('class init ok')
#     # 放最后操作
#     def init_rs(self,TrueIP,replsetname,priority):
#         self.client.admin.command('replSetInitiate',"{_id:'{}',members:[{host:'{}:{}',priority:{}}]}".format(replsetname,TrueIP,port,priority))


#
# host = '127.0.0.1'
port = 30000
# username = 'root'
# password = 'sa123456'
#
# instance = Mongo(host,port,username,password,authSource='admin')

p.debug('now opreate inside mongo')
instance = Mongo('127.0.0.1', port)
# instance.init_rs(ip,replsetname,priority)
# create_root_user(port,user_name='root',password='sa123456')
# instance.add_repset_member()

