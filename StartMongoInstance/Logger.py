import logging
from logging import handlers

class Logger(object):
    level_relations = {
        'debug':logging.DEBUG,
        'info':logging.INFO,
        'warning':logging.WARNING,
        'error':logging.ERROR,
        'crit':logging.CRITICAL
    }#log level map

    def __init__(self,filename,level='info',when='D',backCount=3,fmt='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s'):
        self.logger = logging.getLogger(filename)
        format_str = logging.Formatter(fmt)#log file formate
        self.logger.setLevel(self.level_relations.get(level))# set log level
        sh = logging.StreamHandler()
        sh.setFormatter(format_str)
        th = handlers.TimedRotatingFileHandler(filename=filename,when='D',backupCount=backCount,encoding='utf-8')
        #TimedRotatingFileHandler
        th.setFormatter(format_str)
        self.logger.addHandler(sh)
        self.logger.addHandler(th)
