# -*- coding: utf-8 -*-
"""
@Time : 18-3-14 下午4:18
@Author : courage
@Site : 
@File : WorkerSchedule.py
@Software: PyCharm
"""
import sys
import os
import getopt
import threading
from utils.redis_db_helper import Redis
from utils.rabbitmq_helper import RabbitMq
import time
import importlib
from config.config import Conf
import json
import logging
from loggerr.logger import Logger
log = logging.getLogger("crawler_log")


class Scheduler(threading.Thread):
    def __init__(self, config, pn):
        threading.Thread.__init__(self)
        self.__redis = Redis(config)
        self.__rabbitmq = RabbitMq(config)
        # 动态导入对应的项目的parse
        parse = importlib.import_module('worker.parser.' + pn + '.' + pn + '_parser')
        self.__parse = parse.Parser()

    def run(self):
        while True:
            try:
                task = self.__redis.get_nowait()
                task = {
                    "data": {
                        "url": "https://rmfygg.court.gov.cn/web/rmfyportal/noticeinfo?p_p_id=noticelist_WAR_rmfynoticeListportlet&p_p_lifecycle=2&p_p_state=normal&p_p_mode=view&p_p_resource_id=initNoticeList&p_p_cacheability=cacheLevelPage&p_p_col_id=column-1&p_p_col_count=1"
                    },
                    "project_name": "",
                    "nodeToken": 1
                }
                if task is None:
                    time.sleep(5)
                    continue
                result = self.__parse.do(task)
                # print("-------",result)
                if result is None:
                    continue
                # print("++++++++",json.dumps(result))
                self.__rabbitmq.publish(json.dumps(result))
            except Exception as e:
                logging.exception(e)



if __name__ == "__main__":
    Logger().setup_log
    opts, args = getopt.getopt(sys.argv[1:], "n:")
    pn = None
    for op, value in opts:
        if op == "-n":
            pn = value
    # if pn is None:
    #     raise Exception("invalid project name,you must give params like '-n ent'")

    pn = 'bulletin'

    # 初始化配置文件
    conf_list = []
    # 加载标准配置文件
    basePath = os.path.split(os.path.realpath(__file__))[0] + '/worker.conf'
    #加载对应项目的配置文件
    projectPath = os.path.split(os.path.realpath(__file__))[0] + '/parse/' + pn + '/' + pn +'.conf'

    conf_list.append(basePath)
    conf_list.append(projectPath)

    config = Conf(conf_list)
    thread_count = config.get("base", "thread_count")

    # 启动线程调用解析
    for i in range(int(thread_count)):
        Scheduler(config, pn).start()

# 传递数据结构
# task{
# 	data(字典，任务条件)
# 	project_name(str, 标识项目名)
# 	nodeToken(int, 标识列表页，详情页)
# }
#
# result{
# 	infos（list,解析的结果）
# 	project_name(str, 标识项目名)
# 	nodeToken(int, 标识列表页，详情页)
# }