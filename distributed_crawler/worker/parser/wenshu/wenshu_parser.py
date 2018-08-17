# -*- coding: utf-8 -*-
"""
@Time : 18-3-26 下午3:52
@Author : yang
@Site : 
@File : wenshu_parser.py
@Software: PyCharm
"""

# from worker.parser.base_parser import BaseParser
# from utils.request_helper import RequestHeler
# from lxml import etree
# import paramiko
import os
# import logging
import requests
from random import random
from subprocess import check_output
import re
import json
import datetime
import time
from MySQLdb import *
from multiprocessing.dummy import Pool as ThreadPool

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
def format_s(s):
    return {
        item.split(':', 1)[0].strip(): item.split(':', 1)[1].strip() for item in s.split('\n') if item
        }


def createGuid():
    return hex(int((1 + random()) * 0x10000))[3:]


def Guid():
    return createGuid() + createGuid() + "-" + createGuid() + "-" + createGuid() + createGuid() + "-" + createGuid() + createGuid() + createGuid()


def resul():
    # .decode('utf8')
    return check_output(['/home/python/Downloads/node-v6.1.0-linux-x64/bin/node', os.path.split(os.path.realpath(__file__))[0] + '/result2.js']).strip()


def fagui(page,wenshu):
    url = 'http://wenshu.court.gov.cn/Content/GetSummary'
    data = {'docId': page}
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'}
    proxies = {"http": "http://" + requests.get('http://180.76.189.148:8000/',timeout = 10).text}
    response = requests.post(url, data=data, headers=headers,proxies=proxies,timeout = 500)
    ss = response.text.replace('\\', '').replace('u0027', '"').replace('&amp;#xA;', '').strip()
    content = re.sub(r'([a-zA-Z\u4e00-\u9fa5]+)(?=:)', r'"\1"', ss).replace(",],", "],")
    content = json.loads(content[1:-1], strict=False)
    for i in content['RelateInfo']:
        if i["key"] == 'appellor':
            wenshu['appellor'] = i.get('value')
        elif i["key"] == 'reason':
            wenshu['caseReason'] = i.get('value')
            wenshu['keyWord'] = i.get('value')
        elif i["key"] == 'caseType':
            wenshu['caseType'] = i.get('value')
    if len(content['LegalBase']) == 0:
        wenshu['legalBase'] = ""
    else:
        wenshu['legalBase'] = str(content.get('LegalBase'))
    return wenshu


class Parser():

    def __init__(self):
        pass
    # be used to parse List
    # return result

    def list_parse(self,task):
        # result = {}
        # result["project_name"] = task.get("project_name")
        # result["nodeToken"] = task.get("nodeToken")

        # infos = []

        # session = requests.Session()
        # List
        id = 22426897
        index = 1

        for i in range(1):
            # pass
            # time_one = task.get("data").get("url")
            time_one = "2017-01-01"
            url = 'http://wenshu.court.gov.cn/List/List'
            params = """sorttype: 1
            conditions: searchWord  CPRQ
            conditions:searchWord 1 AJLX  案件类型:刑事案件
            刑事案件 案件类型:刑事案件"""
            headers = """Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8
            Accept-Encoding: gzip, deflate
            Accept-Language: zh-CN,zh;q=0.9
            Cache-Control: max-age=0
            Connection: keep-alive
            Cookie: _gscu_2116842793=21547039fulqyb16; vjkl5=453a09dff054d5f01d218bd0a9c72bf550477159; Hm_lvt_3f1a54c5a86d62407544d433f6418ef5=1521710620; Hm_lpvt_3f1a54c5a86d62407544d433f6418ef5=1521710620; _gscbrs_2116842793=1; _gscs_2116842793=217106202fpxya16|pv:1
            Host: wenshu.court.gov.cn
            Referer: http://wenshu.court.gov.cn/
            Upgrade-Insecure-Requests: 1
            User-Agent: Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.162 Safari/537.36"""
            try:
                proxies = {"http": "http://" + requests.get('http://180.76.189.148:8000/',timeout = 10).text}
                # , proxies = proxies
                response = requests.get(url=url, params=format_s(params), headers=format_s(headers),proxies=proxies,timeout = 500)
                vjkl5 = response.cookies.get('vjkl5')
                html = response.content.decode("utf-8")
                # print(html)
                # pattern = re.compile(r'function getKey.*\s*')
                pattern = re.compile(r'function getKey(?:.|\n)+(?=\<)')
                content = pattern.findall(html)
                js = content[0][:-12]
                word = "'" + vjkl5 + "'"
                js = js.replace("getCookie('vjkl5')", word)
                # print(js)
                with open("result.js", "r") as f:
                    js_old = f.read()
                with open("result2.js", "w") as f:
                    f.write(js_old)
                    f.write(js)
            except:
                print("获取vjkl5失败")
            # item_list = pattern.findall(response)
            # print(content)
            # vjkl5 =response.cookies.get('vjkl5')
            # GetCode
            # print(vjkl5)
            try:
                url = 'http://wenshu.court.gov.cn/ValiCode/GetCode'
                guid = Guid()
                data = {
                    'guid': guid
                }
                headers = """Accept: */*
            Accept-Encoding: gzip, deflate
            Accept-Language: zh-CN,zh;q=0.9
            Connection: keep-alive
            Content-Length: 40
            Content-Type: application/x-www-form-urlencoded; charset=UTF-8
            Cookie: _gscu_2116842793=21547039fulqyb16; Hm_lvt_3f1a54c5a86d62407544d433f6418ef5=1521710620; Hm_lpvt_3f1a54c5a86d62407544d433f6418ef5=1521710620; _gscbrs_2116842793=1; _gscs_2116842793=217106202fpxya16|pv:1; vjkl5={vjkl5:s}
            Host: wenshu.court.gov.cn
            Origin: http://wenshu.court.gov.cn
            Referer: http://wenshu.court.gov.cn/List/List?sorttype=1&conditions=searchWord+1++%E5%88%91%E4%BA%8B%E6%A1%88%E4%BB%B6+%E6%A1%88%E4%BB%B6%E7%B1%BB%E5%9E%8B:%E5%88%91%E4%BA%8B%E6%A1%88%E4%BB%B6
            User-Agent: Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.162 Safari/537.36
            X-Requested-With: XMLHttpRequest""".format(vjkl5=vjkl5)

                proxies = {"http": "http://" + requests.get('http://180.76.189.148:8000/',timeout = 10).text}
                number = requests.post(url=url, data=data, headers=format_s(headers),proxies=proxies,timeout = 500).text

                # ListContent
                url = 'http://wenshu.court.gov.cn/List/ListContent'
                vl5x = resul()

                data = {
                    'Param': '裁判日期:'+time_one+'    TO  '+time_one+',案件类型:刑事案件',
                    'Index': index,
                    'Page': '20',
                    'Order': '法院层级',
                    'Direction': 'asc',
                    'vl5x': vl5x,
                    'number': number,
                    'guid': guid
                }
                headers = """Accept: */*
                Accept-Encoding: gzip, deflate
                Accept-Language: zh-CN,zh;q=0.9
                Connection: keep-alive
                Content-Length: 240
                Content-Type: application/x-www-form-urlencoded; charset=UTF-8
                Cookie: _gscu_2116842793=21547039fulqyb16; Hm_lvt_3f1a54c5a86d62407544d433f6418ef5=1521710620; Hm_lpvt_3f1a54c5a86d62407544d433f6418ef5=1521710620; _gscbrs_2116842793=1; vjkl5={vjkl5:s}
                Host: wenshu.court.gov.cn
                Origin: http://wenshu.court.gov.cn
                Referer: http://wenshu.court.gov.cn/List/List?sorttype=1&conditions=searchWord+1++%E5%88%91%E4%BA%8B%E6%A1%88%E4%BB%B6+%E6%A1%88%E4%BB%B6%E7%B1%BB%E5%9E%8B:%E5%88%91%E4%BA%8B%E6%A1%88%E4%BB%B6
                User-Agent: Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.162 Safari/537.36
                X-Requested-With: XMLHttpRequest""".format(vjkl5=vjkl5)
            except:
                print("获取vl5x失败")
            try:
                proxies = {"http": "http://" + requests.get('http://180.76.189.148:8000/',timeout = 10).text}
                content = requests.post(url=url, data=data, headers=format_s(headers),proxies=proxies,timeout = 500)
                s = content.text

                ss = s.replace('\\', '')
                # print(ss)
                data_json = json.loads(ss[1:-1])
                # #[1:len(ss) - 1]
                # print(data_json)
                num = int(data_json[0]["Count"]) // 20 + 1
                print(num)
            except:
                print("获取详情失败")
            try:
                for i in data_json[1:]:
                    wenshu = {}
                    # cast_time = i.get('裁判日期')
                    # d = datetime.datetime.strptime(cast_time,'%Y-%m-%d')
                    wenshu['id'] = id
                    wenshu['date'] = i.get('裁判日期')
                    wenshu['caseName'] = i.get('案件名称')
                    wenshu['caseNo'] = i.get('案号')
                    wenshu['dataSources'] = i.get('法院名称')
                    wenshu['trialProcedure'] = i.get('审判程序')
                    wenshu['reason'] = i.get('裁判要旨段原文')
                    wenshu['doclD'] = i.get('文书ID')
                    print(wenshu['doclD'])
                    headers = """Accept: */*
                    Accept-Encoding: gzip, deflate
                    Accept-Language: zh-CN,zh;q=0.9
                    Connection: keep-alive
                    Content-Length: 240
                    Content-Type: application/x-www-form-urlencoded; charset=UTF-8
                    Cookie: _gscu_2116842793=21547039fulqyb16; Hm_lvt_3f1a54c5a86d62407544d433f6418ef5=1521710620; Hm_lpvt_3f1a54c5a86d62407544d433f6418ef5=1521710620; _gscbrs_2116842793=1; _gscs_2116842793=217106202fpxya16|pv:1; vjkl5={vjkl5:s}
                    Host: wenshu.court.gov.cn
                    Origin: http://wenshu.court.gov.cn
                    Referer: http://wenshu.court.gov.cn/List/List?sorttype=1&conditions=searchWord+1++%E5%88%91%E4%BA%8B%E6%A1%88%E4%BB%B6+%E6%A1%88%E4%BB%B6%E7%B1%BB%E5%9E%8B:%E5%88%91%E4%BA%8B%E6%A1%88%E4%BB%B6
                    User-Agent: Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.162 Safari/537.36
                    X-Requested-With: XMLHttpRequest""".format(vjkl5=vjkl5)
                    content_url = 'http://wenshu.court.gov.cn/CreateContentJS/CreateContentJS.aspx?DocID='
                    proxies = {"http": "http://" + requests.get('http://180.76.189.148:8000/',timeout = 10).text}
                    content = requests.post(url=content_url + wenshu['doclD'], data=data, headers=format_s(headers),proxies=proxies,timeout = 500)
                    con = re.compile(r'"{(?:.|\n)+(?=";)')
                    content = con.findall(content.text)
                    ss = content[0].replace('\\', '')
                    data_json = json.loads(ss[1:])
                    wenshu['content'] = data_json['Html']
                    # pub_time = data_json['PubDate']
                    # s = datetime.datetime.strptime(pub_time,'%Y-%m-%d')
                    # print(s)
                    wenshu['releaseDate'] = data_json['PubDate']
                    # wenshu['time'] = datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')
                    wenshu['time'] = datetime.datetime.today().strftime('%Y-%m-%d')
                    time.sleep(1)
                    page = wenshu['doclD']
                    fagui(page,wenshu)
                    # print(wenshu)
                    try:
                        conn = connect(host='180.76.172.153', port=3306, db='courtdoc', user='crawler',
                                       passwd='ark#2017',
                                       charset='utf8')
                        cur = conn.cursor()
                        # count = cs1.execute("insert into test(wenshuid) values('wenshuid')")
                        sql = "INSERT ignore INTO ws_content_primary(id,date,caseName,caseNo,dataSources,trialProcedure,reason,docID,releaseDate,time,appellor,caseReason,keyWord,caseType,legalBase) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);"

                        cur.execute(sql, (
                            wenshu.get('id'), wenshu.get('date'), wenshu.get('caseName'), wenshu.get('caseNo'),
                            wenshu.get('dataSources'),
                            wenshu.get('trialProcedure'), wenshu.get('reason'), wenshu.get('doclD'),
                            wenshu.get('releaseDate'), wenshu.get('time'),
                            wenshu.get('appellor'), wenshu.get('caseReason'), wenshu.get('keyWord'),
                            wenshu.get('caseType'),
                            wenshu.get('legalBase')))
                        # print count
                        conn.commit()
                        conn_one = connect(host='180.76.172.153', port=3306, db='courtdoc', user='crawler',
                                           passwd='ark#2017',
                                           charset='utf8')
                        cur_one = conn_one.cursor()
                        # count = cs1.execute("insert into test(wenshuid) values('wenshuid')")
                        sql_one = "INSERT ignore INTO ws_content_attachment(id,content) VALUES(%s,%s);"

                        cur_one.execute(sql_one, (
                            wenshu['id'], wenshu['content'])
                                        )
                        # print count
                        conn_one.commit()



                    except Exception as e:
                        print(e)
                    finally:
                        try:
                            cur.close()
                            conn.close()
                            cur_one.close()
                            conn_one.close()
                        except Exception as e:
                            print(e)

                    id += 1
            except:
                print("解析失败")


                # wenshu = json.dumps(wenshu, ensure_ascii=False)
                # infos.append(wenshu)
                # print(wenshu)

                # 这是详情的
                # content_url = 'http://wenshu.court.gov.cn/CreateContentJS/CreateContentJS.aspx?DocID=699daf62-d6a6-43b1-aefc-a8ad00345f99'

                # result["infos"] = infos

                # return result

            index += 1
    # be used to parse detail
    # return result
    def detail_parse(self,task):
        pass






if __name__ == '__main__':

    parse = Parser()
    task = {
        "data":{
            "url":"2017-01-01"
        },
        "project_name":"wenshu",
        "nodeToken":1
    }
    result = parse.list_parse(task)
    print(result)
