# -*- coding: utf-8 -*-
"""
@Time : 18-3-15 下午4:15
@Author : courage
@Site : 
@File : ent_parse.py
@Software: PyCharm
"""

from worker.parser.base_parser import BaseParser


class Parser(BaseParser):

    # be used to parse List
    # return result
    def list_parse(self, task):
        pass

    # be used to parse detail
    # return result
    def detail_parse(self, task):
        pass
