# -*- coding: utf-8 -*-
"""
@Time : 18-3-15 下午5:28
@Author : courage
@Site : 
@File : config.py
@Software: PyCharm
"""
import configparser


class Conf(object):

    def __init__(self, conf_path_list):
        self.config = configparser.ConfigParser()
        self.do(conf_path_list)

    def do(self, conf_path_list):
        for temp_path in conf_path_list:
            self.config.read(temp_path)

    def get(self, section, key):
        return self.config.get(section, key)
