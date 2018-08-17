# -*- coding: utf-8 -*-
"""
@Time : 18-3-30 上午9:45
@Author : yang
@Site : 
@File : wenshu_handler.py
@Software: PyCharm
"""


from recever.handler.base_handler import BaseHandler
from utils.mysql_db_helper import MysqlCn


class Handler(BaseHandler):

    def __init__(self, config):
        super(Handler, self).__init__(config)
        self.__config = config

    def handle(self,result):
        infos = result.get('infos')
        self.insert(infos)

    def insert(self,msgs):
        mysqlCn = MysqlCn(self.__config)
        sql = 'INSERT ignore INTO ws_content_primary(id,date,caseName,caseNo,dataSources,trialProcedure,reason,docID,releaseDate,time,appellor,caseReason,keyWord,caseType,legalBase) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);'
        sql1 = 'INSERT ignore INTO ws_content_attachment(id,content) VALUES(%s,%s);'
        for ttemp in msgs:
            row_id = mysqlCn.insertOne(sql, (ttemp.get('id'),ttemp.get('date'),ttemp.get('caseName'),ttemp.get('caseNo'),ttemp.get('dataSources'),ttemp.get('trialProcedure'),ttemp.get('reason'),ttemp.get('doclD'),ttemp.get('releaseDate'),ttemp.get('time'),ttemp.get('appellor'),ttemp.get('caseReason'),ttemp.get('keyWord'),ttemp.get('caseType'),ttemp.get('legalBase')))
            content_row_id = mysqlCn.insertOne(sql, (ttemp['id'], ttemp['content']))
        mysqlCn.dispose()