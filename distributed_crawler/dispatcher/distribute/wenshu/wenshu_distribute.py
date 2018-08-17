# -*- coding: utf-8 -*-
"""
@Time : 18-3-26 上午11:40
@Author : yang
@Site : 
@File : wenshu_distribute.py
@Software: PyCharm
"""

import json
from dispatcher.distribute.base_distribute import BaseDistribute
from utils.redis_db_helper import Redis
from lxml import etree
import requests
import datetime
import re
import time

class Distribute(BaseDistribute):

    def __init__(self, config):
        super(BaseDistribute,self).__init__()
        self.__redis = Redis(config)
        self.start = '2017-01-01'
    def dispatch(self):
        self.get_cur_day()

    def get_cur_day(self,str_time = None):
        datestart = datetime.datetime.strptime(self.start, '%Y-%m-%d')
        for i in range(30):
            datestart += datetime.timedelta(days=1)
            turl = datestart.strftime('%Y-%m-%d')
            task = {}
            task['data'] = {'url': turl}
            task['project_name'] = 'wenshu'
            task['nodeToken'] = 1
            self.__redis.put(json.dumps(task))
            time.sleep(1)

    def get_latest_180(self):
        for i in range(180):
            str_time = (datetime.datetime.now()+datetime.timedelta(days=(-i))).strftime("%Y-%m-%d")
            self.get_cur_day(str_time)

    def get_def_url(self):
        task = {}
        task['data'] = {'url': '2017-01-01'}
        task['project_name'] = 'wenshu'
        task['nodeToken'] = 1
        self.__redis.put(json.dumps(task))