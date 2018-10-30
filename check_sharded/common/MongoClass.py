# encoding=utf-8


# @Time    : 2018/9/28 下午4:40
# @Author  : 张锐志
# @TODO    : Enforce Communism

# 系统库
import os
import sys
import time
import traceback
import subprocess

# 第三方库
import pymongo
import prettytable
import logbook
from pprint import pprint
from logbook.more import ColorizedStderrHandler
from logbook import Logger, TimedRotatingFileHandler, set_datetime_format
# 自定义库

# 禁止from xx import *
__all__ = []

# 打印与日志模块
set_datetime_format('local')
p = Logger('MongoClass')
p.handlers.append(ColorizedStderrHandler(level='INFO',bubble=True))

# TODO: 包装removeShard命令

from collections import namedtuple

SERVER_TYPE = namedtuple('ServerType',
                         ['Unknown', 'Mongos', 'RSPrimary', 'RSSecondary',
                          'RSArbiter', 'RSOther', 'RSGhost',
                          'Standalone'])(*range(8))


# 表格美化相关
def table_print(origin_table, head, sort_column=None, reverse_direction=True):
    """
    靠左对齐,根据排序列排序,然后打印
    """
    origin_table.align = 'l'
    # 对传入的排序项进行排序
    if sort_column:
        origin_table.sortby = sort_column
        # 逆向排序
        if reverse_direction:
            origin_table.reversesort = True
    p.info('Sorted by {}'.format(sort_column) + '\n' + '#' * 40 + '{}'.format(
        head) + '#' * 44 + '\n' + origin_table.get_string())



class Mongo:

    def __init__(self, host, port, username=None, password=None, authSource=None,
                 connectTimeoutMS=2000, socketTimeoutMS=2000, serverSelectionTimeoutMS=2000):
        """初始化连接"""
        p.debug('class init begins')
        port = int(port)
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.authSource = authSource
        self.rs_isMaster_dict = None
        # 先空连接连进来
        try:
            self.client = pymongo.MongoClient(host, port, connectTimeoutMS=connectTimeoutMS,
                                              socketTimeoutMS=socketTimeoutMS,
                                              serverSelectionTimeoutMS=serverSelectionTimeoutMS)
        except Exception:
            self.client.close()
            p.error('Init connect failed')
            traceback.print_exc()
            raise Exception

    def auth(self):
        """鉴权"""
        if self.authSource is None:
            p.debug('Haven`t got authSource,use admin for default')
            authSource = 'admin'
        # TODO:下面有问题，在其他库验证了admin库的权限，或许还能做的更灵活点
        try:
            # p.debug('{}:{}'.format(self.username,self.password))
            result = self.client.admin.authenticate(self.username, self.password, source=authSource)
            # p.debug(result)
            p.debug('User: {}. Auth sucess :>'.format(self.username))
            p.debug('class init ok')
        except Exception:
            self.client.close()
            traceback.print_exc()
            raise

    def findMany(self, database='admin', collection='sb', json_where={}):
        """
        根据指定的库,表名去查询复合条件的若干条记录，返回字典列表
        :conn 建立好的连接
        :database 需要查询的数据库
        :collection 需要查询的表
        :json_where mongo查询的where条件{json格式}
        """
        document_list = []
        try:
            for document in self.client[database][collection].find(json_where):  # cursor
                document_list.append(document)
            return document_list
        except Exception as e:
            traceback.print_exc()
            print(e)

    def get_ismaster_info(self):
        """get rs.isMaster() result to a dict"""
        self.rs_isMaster_dict = self.admin_comand('isMaster')

    # 从官方的pymongo里面抄来的
    def server_type(self):
        """Determine the server type from an ismaster response."""
        if not self.rs_isMaster_dict.get('ok'):
            return SERVER_TYPE.Unknown
        if self.rs_isMaster_dict.get('isreplicaset'):
            return SERVER_TYPE.RSGhost
        elif self.rs_isMaster_dict.get('setName'):
            if self.rs_isMaster_dict.get('hidden'):
                return SERVER_TYPE.RSOther
            elif self.rs_isMaster_dict.get('ismaster'):
                return SERVER_TYPE.RSPrimary
            elif self.rs_isMaster_dict.get('secondary'):
                return SERVER_TYPE.RSSecondary
            elif self.rs_isMaster_dict.get('arbiterOnly'):
                return SERVER_TYPE.RSArbiter
            else:
                return SERVER_TYPE.RSOther
        elif self.rs_isMaster_dict.get('msg') == 'isdbgrid':
            return SERVER_TYPE.Mongos
        else:
            return SERVER_TYPE.Standalone

    


    


    def close(self):
        self.client.close()
