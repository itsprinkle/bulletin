# -*- coding: utf-8 -*-
"""
@Time : 18-3-14 下午3:38
@Author : courage
@Site : 
@File : BaseParser.py
@Software: PyCharm
"""

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

class BaseParser(object):

    def __init__(self):
        pass

    # be used to parse msg
    # return result{
    #       infos（list,解析的结果）,
    #       project_name(int, 标识项目名),
    #       nodeToken(int, 标识列表页，详情页)
    # }
    def do(self,task):
        print(task)
        nodeToken = task.get("nodeToken")
        if nodeToken == 1:
            return self.list_parse(task)
        elif nodeToken == 2:
            return self.detail_parse(task)

    # be used to parse List
    # return result
    def list_parse(self, task):
        pass

    # be used to parse detail
    # return result
    def detail_parse(self, task):
        pass
