# -*- coding: utf-8 -*-
from __future__ import print_function
# from __future__ import unicode_literals
import sys
import time
import getopt
import re
import yaml
with open('mongod_20001.conf','rt') as mongo_conf_file:
    tmp = mongo_conf_file.read()
    print(tmp)
mongo_conf = yaml.load(tmp)
with open('mongod_20001.conf','wt') as mongo_conf_file:
    mongo_conf['net']['port'] = 20001
    mongo_conf['processManagement']['pidFilePath'] = '/home/dba/sysbench-data/mongo/20001/20001.pid'
    mongo_conf['systemLog']['path'] = '/home/dba/sysbench-data/mongo/20001/log/20001.log'
    mongo_conf['storage']['dbPath'] = '/home/dba/sysbench-data/mongo/20001/data'
    mongo_conf['storage']['wiredTiger']['engineConfig']['cacheSizeGB'] = 1
    # yaml回写的时候会把off自动改写成false，这里需要手工指定
    mongo_conf['operationProfiling']['mode'] = 'off'
    yaml.dump(mongo_conf,mongo_conf_file)