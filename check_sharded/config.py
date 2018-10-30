#!/bin/python3
# encoding=utf-8


# @Time    : 2018/9/28 下午10:49
# @Author  : 张锐志
# @TODO    : Enforce Communism

# 系统库

# 第三方库

# 自定义库

# 禁止from xx import *
__all__ = []

# Mongos的连接信息
class ConnString(object):
    ip = "5.20.13.14"
    port = 5201
    auth_enabled=True  # 是否开启了验证
    user = 'me'
    password = 'fate'

