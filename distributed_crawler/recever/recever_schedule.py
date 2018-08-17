# -*- coding: utf-8 -*-
"""
@Time : 18-3-16 上午11:50
@Author : courage
@Site : 
@File : recever_schdeule.py
@Software: PyCharm
"""
from config.config import Conf
from utils.rabbitmq_helper import RabbitMq
import json
import importlib
import os
import sys
import getopt


class Scheduler(object):
    handlers = {}

    def __init__(self):
        base_dispatcher_config_path = os.path.split(os.path.realpath(__file__))[0] + "/recever.conf"
        self.config = Conf([base_dispatcher_config_path])
        self.__rabbitmq = RabbitMq(self.config)

    def load(self, project_name):
        if project_name is None:
            return None
        # 1加载配置文件
        project_config_path = os.path.split(os.path.realpath(__file__))[0] + '/handler/' + project_name + '/' + project_name + '.conf'
        self.config.do([project_config_path])
        # 2动态加载处理类
        handler = importlib.import_module('recever.handler.' + project_name + '.' + project_name + '_handler')
        project_handler = handler.Handler(self.config)
        # 3handlers添加处理实例
        self.handlers[str(project_name)] = project_handler
        # 4返回处理实例
        return project_handler

    def handler(self, ch, method, properties, body):
        result = json.loads(body)
        project_name = result.get("project_name")
        t_hander = self.handlers.get(project_name)
        if t_hander is None:
            t_hander = self.load(project_name)
        if t_hander is not None:
            t_hander.handle(result)

    # 调用rabbitmq的回调函数方法启动接收信息
    def start(self):
        self.__rabbitmq.get(self.handler)


if __name__ == '__main__':
    opts, args = getopt.getopt(sys.argv[1:], "n:")
    project_name = None
    for op, value in opts:
        if op == "-n":
            project_name = value

    Scheduler().start()


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