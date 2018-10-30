#!/usr/bin/python3
# encoding=utf-8


# @Time    : 2018/9/28 下午5:05
# @Author  : 张锐志
# @TODO    : Enforce Communism

# 系统库

# 第三方库
import prettytable
import logbook
import pymongo
from pymongo.database import Database
from pprint import pprint
from logbook.more import ColorizedStderrHandler
from logbook import Logger, TimedRotatingFileHandler, set_datetime_format
# 自定义库
from config import ConnString
from common.MongoClass import Mongo

# 禁止from xx import *
__all__ = []

# 打印与日志模块
set_datetime_format('local')
p = Logger('checkUnsharded')
p.handlers.append(ColorizedStderrHandler(level='INFO', bubble=True))


def get_unpartion_db(mongos_instance):
    """
    返回未开启分区的库
    :param mongos_instance:连接实例
    :return:库名列表
    """
    unpartioned_db_list = mongos_instance.findMany(database='config', collection="databases",
                                                   json_where={"partitioned": {"$ne": True}})
    return unpartioned_db_list


def get_sharded_collection(mongos_instance):
    """
    获取已经分片后的集合
    :param mongos_instance: 连接
    :return: db.collection样式的字符列表
    """
    sharded_table_list = mongos_instance.findMany(database='config', collection="collections",
                                                  json_where={"dropped": {"$ne": True}})
    return sharded_table_list


def get_database_list(mongos_instance, verbose=False):
    """
    获取实例中所有的db名称
    :param mongos_instance: mongos连接
    :param verbose:返回详细字典列表或者简单的字符串列表
    :return:
    """
    if verbose:
        return mongos_instance.client.list_databases()
    else:
        return mongos_instance.client.list_database_names()


def get_collection_list(mongos_instance, database="overdrive", verbose=False):
    """
    返回给定的连接的库中的所有表
    :param mongos_instance:
    :param database:
    :param verbose: 启用后，返回字典信息列表
    :return: 字符串列表
    """
    if verbose:
        return mongos_instance.client[database].list_collections()
    else:
        return mongos_instance.client[database].list_collection_names()


if __name__ == '__main__':

    Cluster = Mongo(host=ConnString.ip, port=ConnString.port,
                    username=ConnString.user, password=ConnString.password)

    if ConnString.auth_enabled:
        Cluster.auth()

    p.warning("###### Need to be enableSharding ######")
    for db in get_unpartion_db(Cluster):
        p.warning(db)

    p.warning("###### Need to be shardCollection ######")
    for i in get_database_list(Cluster):
        if i in ["config", "admin", "test"]:
            continue
        for table in get_collection_list(Cluster, database=i):
            full_table_name = i + '.' + table
            if full_table_name not in \
                    [sharded_table['_id'] for sharded_table in get_sharded_collection(Cluster)]:
                p.warning(full_table_name)

    Cluster.close()
