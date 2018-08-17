# -*- coding: utf-8 -*-
"""
@Time : 18-3-20 上午10:21
@Author : courage
@Site : 
@File : bulletin_handler.py
@Software: PyCharm
"""


# class BaseHandler(object):
#
#     # be uesd to init handler
#     def __init__(self,config):
#         pass
#
#     # be used to handle result
#     def handle(self):
#         pass
from recever.handler.base_handler import BaseHandler
from utils.mysql_db_helper import MysqlCn
import time





class Handler(BaseHandler):

    def __init__(self, config):
        super(Handler, self).__init__(config)
        self.__config = config

    def handle(self,result):
        infos = result.get('infos')
        self.insert(infos)

    def insert(self,msgs):
        try:
            mysqlCn = MysqlCn(self.__config)
            sql = 'INSERT IGNORE INTO bul_content_primary(id,type,person,party,time,pdf,url,create_time) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)'
            sql1 = 'INSERT IGNORE INTO bul_content_attachment(id,content) VALUES(%s,%s)'
            for ttemp in msgs:
                tid = int(ttemp.get('id'))
                ttype = str(ttemp.get('type'))
                person = str(ttemp.get('person'))
                party = str(ttemp.get('party'))
                ttime = str(ttemp.get('time'))
                pdf = str(ttemp.get('pdf'))
                turl = str(ttemp.get('url'))
                content = str(ttemp.get('content'))
                create_time = time.strftime("%Y-%m-%d %H:%M:%S")
                row_id = mysqlCn.insertOne(sql, (tid,ttype,person,party,ttime,pdf,turl,create_time))
                content_row_id = mysqlCn.insertOne(sql1, (tid,content))
            mysqlCn.dispose()
        except Exception as e:
            print(e,"入库失败")


if __name__ == '__main__':
    print(time.strftime("%Y-%m-%d %H:%M:%S"))


