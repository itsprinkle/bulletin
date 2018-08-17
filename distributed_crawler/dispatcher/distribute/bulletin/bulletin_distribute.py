# -*- coding: utf-8 -*-
"""
@Time : 18-3-20 下午3:48
@Author : courage
@Site : 
@File : bulletin_distribute.py
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
import logging



log = logging.getLogger("crawler_log")

class Distribute(BaseDistribute):

    def __init__(self, config):
        super(BaseDistribute,self).__init__()
        self.__redis = Redis(config)
        self.headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36"
            }


    def dispatch(self):
        # try:
        #     self.get_cur_day(str_time= None , count=-1)
        # except Exception as e:
        #     print(e,"发送请求失败")
        #     self.get_cur_day(str_time= None , count=-1)
        self.get_cur_day()     # 补
        # 抓取实时公告
        # self.get_cur_day(str_time=None, count=-1)
        # redis_sise = self.__redis.qsize()
        # if redis_sise < 500:
            # 补抓过去公告
            # self.get_past_data(str_time1=None,count=-180)


    def get_cur_day1(self):
        url = 'http://rmfygg.court.gov.cn/web/rmfyportal/noticeinfo?p_p_id=noticelist_WAR_rmfynoticeListportlet&p_p_lifecycle=2&p_p_state=normal&p_p_mode=view&p_p_resource_id=initNoticeList&p_p_cacheability=cacheLevelPage&p_p_col_id=column-1&p_p_col_count=1'
        task = {}
        task['data'] = {'url': url}
        task['project_name'] = 'bulletin'
        task['nodeToken'] = 1
        self.__redis.put(json.dumps(task))

    # 获取当天公告的url,并保存到redis
    def get_cur_day(self,str_time = None,count=-1):
        if str_time == None:
            str_time = (datetime.datetime.now() + datetime.timedelta(days=(count))).strftime("%Y-%m-%d")
            print(str_time)
        #http://rmfygg.court.gov.cn/psca/lgnot/bulletin/2018-05-21_0_2.html
        url = 'http://rmfygg.court.gov.cn/psca/lgnot/bulletin/' + str_time + '_0_0.html'
        rsp = requests.get(url)
        sel = etree.HTML(rsp.text)
        print('rsp.text:',rsp.text)
        try:
            last_url = sel.xpath('//a[text()="末页"]/@href')[0]
            print('last_url:',last_url)
            last_page_num = int(re.search('_(\d+)\.html',last_url).group(1))
            for i in range(last_page_num+1):
                turl = 'http://rmfygg.court.gov.cn/psca/lgnot/bulletin/' + str_time + '_0_' + str(i) + '.html'
                task = {}
                task['data'] = {'url': turl}
                task['project_name'] = 'bulletin'
                task['nodeToken'] = 1
                self.__redis.put(json.dumps(task))
        except Exception as e:
            print(e,"last_url error")
            first_url = sel.xpath('//a[text()=“首页”]/@href')[0]
            while True:
                first_url += 1
                turl = 'http://rmfygg.court.gov.cn/psca/lgnot/bulletin/' + str_time + '_0_' + str(first_url) + '.html'
                task = {}
                task['data'] = {'url': turl}
                task['project_name'] = 'bulletin'
                task['nodeToken'] = 1
                self.__redis.put(json.dumps(task))
                if first_url is None :
                    return





    def get_def_url(self):
        task = {}
        task['data'] = {'url': 'http://rmfygg.court.gov.cn/bulletin/court/0.html'}
        task['project_name'] = 'bulletin'
        task['nodeToken'] = 1
        self.__redis.put(json.dumps(task))

#  -42