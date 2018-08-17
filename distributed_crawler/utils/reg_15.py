# -*- coding: utf-8 -*-
"""
@Time : 18-3-14 上午9:55
@Author : courage
@Site : 
@File : reg_15.py
@Software: PyCharm
"""
from utils.mysql_db_helper import MysqlCn
import configparser
import logging
import requests
import urllib
from utils.ADSL import ADSL
import time

class Rgno15(object):

    def __init__(self):
        """
        [mysql]
        DBHOST = 180.76.172.153
        DBPORT = 3306
        DBUSER = crawler
        DBPWD = ark#2017
        DBNAME = courtdoc
        DBCHAR = utf8
        """
        config = configparser.ConfigParser()
        config.add_section('mysql')
        config.add_section('project')
        config.set('mysql', 'DBHOST', '180.76.172.153')
        config.set('mysql', 'DBPORT', '3306')
        config.set('mysql', 'DBUSER', 'crawler')
        config.set('mysql', 'DBPWD', 'ark#2017')
        config.set('mysql', 'DBNAME', 'ent')
        config.set('mysql', 'DBCHAR', 'utf8')

        config.set('project','project_name','Rgno15')

        self.config = config

    def mod10(self,value):
        if value == 10:
            return value
        else:
            return value % 10

    def check(self,str):
        if "N" in str:
            return '%sX' % (str[:14])
        value = 10
        for t in str:
            value = (self.mod10(value + (ord(t) - ord('0'))) * 2) % 11
        num = 11 - value
        if num >= 10:
            num = num - 10
        return '%s%d' % (str[:14], num)

    def get_not_crawler_from_keyword(self):
        mysqlCn = MysqlCn(self.config)
        sql = "SELECT count(id) as `count` FROM keyword_info WHERE `status`>1 AND priority = 1 AND province_id IS NOT NULL;"
        result = mysqlCn.getAll(sql)
        mysqlCn.dispose()
        if result:
            return result[0].get('count')
        else:
            return False

    def inset_keyword(self,keywods):
        mysqlCn = MysqlCn(self.config)
        sql = "INSERT INTO keyword_info(keyword,province_id,priority) VALUES(%s,%s,%s);"
        for i in range(len(keywods)):
            keyword = keywods[i].get('keyword')
            province_id = keywods[i].get('province_id')
            priority = 0
            result = mysqlCn.insertOne(sql, (keyword, province_id, priority))
        mysqlCn.dispose()
        return None

    def inset_keyword_confirmed(self,keywods):
        mysqlCn = MysqlCn(self.config)
        sql = "INSERT IGNORE INTO keyword_info_confirmed(keyword,province_id,`name`,priority) VALUES(%s,%s,%s,%s);"
        for i in range(len(keywods)):
            keyword = keywods[i].get('keyword')
            province_id = keywods[i].get('province_id')
            name = keywods[i].get('name')
            priority = 0
            result = mysqlCn.insertOne(sql, (keyword, province_id,name, priority))
        mysqlCn.dispose()
        return None

    def is_rengo_exit(self,regno):
        mysqlCn = MysqlCn(self.config)
        tmd5 = self.md5(regno)
        sql = "SELECT COUNT(`id`) AS counts FROM business_info WHERE md5 = %s;"
        result = mysqlCn.getAll(sql, (tmd5,))
        mysqlCn.dispose()
        if result[0].get('counts') == 0:
            return False
        else:
            return True

    def get_sectino_num(self):
        mysqlCn = MysqlCn(self.config)
        sql = "SELECT section_num,province_id,max_num,current_num  FROM regno_statistic WHERE status = 0 AND section_num IS NOT NULL LIMIT 1;"
        result = mysqlCn.getAll(sql)
        mysqlCn.dispose()
        if len(result)>0:
            return result[0]
        else:
            return False

    def update_sectino_num(self,section_num,current_num,status=0):
        mysqlCn = MysqlCn(self.config)
        sql = "UPDATE regno_statistic SET `status` = %s,`current_num`= %s WHERE section_num = %s;"
        result = mysqlCn.update(sql, (status,current_num,section_num))
        mysqlCn.dispose()
        return result

    def md5(self,strs):
        import hashlib
        m = hashlib.md5()
        m.update(str(strs).encode("utf8"))
        return m.hexdigest()

    def handler(self):
        # 1 检测keyword 表带抓取记录量
        # 2 其实就是算法生成随机选择号段生成
        # 3 注册号生成算法，以及遍历号查询，回填当前遍历号
        keyword_count = self.get_not_crawler_from_keyword()
        print('keyword_count:',keyword_count)
        if keyword_count and keyword_count < 1000:
            struct_section_num = self.get_sectino_num()
            print('struct_section_num:',struct_section_num)
            if not struct_section_num:
                return None
            section_num = struct_section_num.get('section_num')
            province_id = struct_section_num.get('province_id')
            max_num = int(struct_section_num.get('max_num'))
            current_num = int(struct_section_num.get('current_num'))
            print('current_num:',current_num)
            keywords = []
            i = 1
            while True:
                sequence_num = current_num + i
                i = i + 1
                if len(keywords) == 10000:
                    self.update_sectino_num(section_num,sequence_num)
                    break
                if sequence_num >= max_num:
                    self.update_sectino_num(section_num,sequence_num,status=1)
                    break
                regno = self.check(section_num + str(sequence_num).zfill(5))
                if not self.is_rengo_exit(regno):
                    keyword = {}
                    keyword['keyword'] = regno
                    keyword['province_id'] = province_id
                    keywords.append(keyword)
                    print('regno not exit:', regno)
                else:
                    print('regno     exit:',regno)
            self.inset_keyword(keywords)

    def getmsg(self,param):
        json_object = None

        url = 'https://www.creditchina.gov.cn/api/credit_info_search?keyword=' + param + '&templateId=&page=1&pageSize=10'

        headers = {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Connection": "keep-alive",
            "Cookie": "Hm_lvt_0076fef7e919d8d7b24383dc8f1c852a=1522398473; Hm_lpvt_0076fef7e919d8d7b24383dc8f1c852a=1522398482",
            "Host": "www.creditchina.gov.cn",
            "Referer": "https://www.creditchina.gov.cn/xinyongxinxi/index.html?index=0&keyword=" + urllib.parse.quote(
                param),
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest"
        }
        exception_count = 0
        while True:
            try:
                rsp = requests.get(url, headers=headers)
                if rsp is None or rsp.status_code != 200:
                    raise Exception('request error')
                json_object = rsp.json()
                json_object = json_object['data']['results']
                break
            except Exception as e:
                logging.exception(e)
                if exception_count < 3:
                    time.sleep(5)
                    exception_count =exception_count + 1
                    continue
                else:
                    print('exception_adsl')
                    exception_count = 0
                    ADSL.exe(pd=True)
                    continue
        if json_object is not None and len(json_object) > 0:
            return json_object[0]
        else:
            return None

    def handler_get_exit_regno(self):
        struct_section_num = self.get_sectino_num()
        section_num = struct_section_num.get('section_num')
        province_id = struct_section_num.get('province_id')
        max_num = int(struct_section_num.get('max_num'))
        current_num = int(struct_section_num.get('current_num'))

        keywords = []
        i = 1
        while True:
            sequence_num = current_num + i
            i = i + 1
            if len(keywords) == 100:
                self.inset_keyword_confirmed(keywords)
                self.update_sectino_num(section_num, sequence_num)
                keywords.clear()
            if sequence_num >= max_num:
                self.inset_keyword_confirmed(keywords)
                self.update_sectino_num(section_num, sequence_num, status=1)
                break
            regno = self.check(section_num + str(sequence_num).zfill(5))
            if not self.is_rengo_exit(regno):
                zgzx = self.getmsg(regno)
                if zgzx is not None:
                    keyword = {}
                    keyword['keyword'] = regno
                    keyword['name'] = zgzx.get('name')
                    keyword['province_id'] = province_id
                    keywords.append(keyword)
                    print('regno     exit in            server:', regno)
                else:
                    print('regno not exit in loacal and server:', regno)
            else:
                print('regno     exit in loacal:', regno)

if __name__ == '__main__':
    regno15 = Rgno15()
    while True:
        regno15.handler_get_exit_regno()