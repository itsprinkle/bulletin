# -*- coding: utf-8 -*-
"""
@Time : 18-3-26 下午4:13
@Author : courage
@Site : 
@File : mysql_handler.py
@Software: PyCharm
"""

import logging
from utils.mysql_db_helper import MysqlCn
from config.config import Conf
import os
import json
import re


class MysqlHandler(logging.Handler):
    def __init__(self,level=logging.NOTSET):
        """Setting up msyql handler, initializing mysql database connection via ."""
        base_dispatcher_config_path = os.path.split(os.path.realpath(__file__))[0] + "/config.conf"
        self.__config = Conf([base_dispatcher_config_path])
        logging.Handler.__init__(self, level)
        pass

    def emit(self, record):
        """Inserting new logging record to msyql database."""
        try:
            msg = re.sub('\'', '\"', record.getMessage())
            msg = json.loads(msg)
            print(msg)
        except Exception as e:
            msg = None
        if isinstance(msg,dict) and msg.get("machine_name") is not None:
            try:
                self._mysqlCn = MysqlCn(self.__config)
                sql = "INSERT INTO bulletin_log(machine,`key`,state) " \
                      "VALUES(%s,%s,%s)"
                machine = msg.get("machine_name")
                key = msg.get("key")
                state = msg.get("state")
                self._mysqlCn.insertOne(sql, (machine, key, state))
                self._mysqlCn.dispose()
            except Exception as e:
                print(e)