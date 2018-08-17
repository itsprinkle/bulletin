# -*- coding: utf-8 -*-
"""
@Time : 18-3-16 上午11:44
@Author : courage
@Site : 
@File : ent_handler.py
@Software: PyCharm
"""
from recever.handler.base_handler import BaseHandler


class Handler(BaseHandler):
    # be uesd to init handler
    def __init__(self, config):
        super(Handler, self).__init__(config)
        pass

    # be used to handle result
    def handle(self, result):
        pass