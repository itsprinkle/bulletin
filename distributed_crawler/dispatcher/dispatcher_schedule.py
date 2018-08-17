# -*- coding: utf-8 -*-
"""
@Time : 18-3-20 下午3:52
@Author : courage
@Site : 
@File : dispatcher_schedule.py
@Software: PyCharm
"""
import os
import sys
import getopt
from config.config import Conf
import importlib
import configparser
from loggerr.logger import Logger


class Scheduler(object):
    distributes = {}

    def __init__(self,project_name):
        base_dispatcher_config_path = os.path.split(os.path.realpath(__file__))[0] + "/dispatcher.conf"
        self.config = Conf([base_dispatcher_config_path])
        self.__distribute = self.load(project_name)

    def load(self, project_name):
        if project_name is None:
            return None
        # 1加载配置文件
        project_config_path = os.path.split(os.path.realpath(__file__))[0] + '/distribute/' + project_name + '/' + project_name + '.conf'
        self.config.do([project_config_path])
        # 2动态加载处理类
        distribute = importlib.import_module('dispatcher.distribute.' + project_name + '.' + project_name + '_distribute')
        project_distribute = distribute.Distribute(self.config)
        # 4返回处理实例
        return project_distribute

    # 调用rabbitmq的回调函数方法启动接收信息
    def start(self):
        self.__distribute.dispatch()


if __name__ == '__main__':
    Logger().setup_log
    opts, args = getopt.getopt(sys.argv[1:], "p:")
    project_name = None
    for op, value in opts:
        if op == "-p":
            project_name = value
    project_name = 'bulletin'
    Scheduler(project_name).start()


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