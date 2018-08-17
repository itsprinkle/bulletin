# -*- coding: utf-8 -*-
"""
@Time : 18-3-16 下午3:56
@Author : courage
@Site :
@File : notice_parser.py
@Software: PyCharm
"""


from worker.parser.base_parser import BaseParser
from utils.request_helper import RequestHeler
import re
import paramiko
import os
import logging
from utils.ADSL import ADSL
import json
from loggerr.logger import Logger
from MySQLdb import *
log = logging.getLogger("crawler_log")



class Parser(BaseParser):

    ParseCount = 45

    def __init__(self):
        pass

    def detail_parse(self,task):
        pass


    def list_parse(self,task):
        try:
            # 定期切换ip,每处理100个就切换一次ip
            Parser.ParseCount += Parser.ParseCount
            if Parser.ParseCount % 50 == 0:
                ADSL.exe(pd=True)

            headers = {
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Connection": "keep-alive",
                "Host": "rmfygg.court.gov.cn",
                "Upgrade-Insecure-Requests": "1",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36"

            }

            postData = {
                '_noticelist_WAR_rmfynoticeListportlet_content': '',
                # postdata里面的searchContent参数可以提供搜索参数，加入日期信息可以抓取历史数据
                '_noticelist_WAR_rmfynoticeListportlet_searchContent': '2018-5-22',
                '_noticelist_WAR_rmfynoticeListportlet_IEVersion': 'ie',
                '_noticelist_WAR_rmfynoticeListportlet_flag': 'init',
                '_noticelist_WAR_rmfynoticeListportlet_noticeType': '',
                '_noticelist_WAR_rmfynoticeListportlet_aoData': '[{"name":"sEcho","value":1},{"name":"iColumns","value":6},{"name":"sColumns","value":",,,,,"},{"name":"iDisplayStart","value":0},{"name":"iDisplayLength","value":10}]'
            }
            url = task.get("data").get("url")
            li = postData['_noticelist_WAR_rmfynoticeListportlet_aoData']
            js = json.loads(li)

            # url = task.get("data").get("url")
            rsp = RequestHeler.post(url, headers=headers, data=postData)
            resultstr = rsp.text
            jsonstr = json.loads(resultstr)
            pagecount = jsonstr["iTotalRecords"]
            print(pagecount)
            # li = postData['_noticelist_WAR_rmfynoticeListportlet_aoData']
            # js = json.loads(li)
            # postData['_noticelist_WAR_rmfynoticeListportlet_aoData'] = str(js)
            # li = postData['_noticelist_WAR_rmfynoticeListportlet_aoData']
            # js = json.loads(li)
            count = int(pagecount / 10 + 1)
            i = 1
            while i < count:
                for a in js:
                    if a["name"] == "sEcho":
                        a["value"] = i
                    if a["name"] == "iDisplayStart":
                        a["value"] = i * 10 - 10
                        # print(a)
                postData['_noticelist_WAR_rmfynoticeListportlet_aoData'] = str(js)
                rsp = RequestHeler.post(url, headers=headers, data=postData)
                # time.sleep(1)
                i += 1
                if rsp is None or rsp.status_code != 200:
                    ADSL.exe(pd=True)
                sel = rsp.text
                sel = json.loads(sel)
                li_sel = sel["data"]
                result = {}
                result["project_name"] = task.get("project_name")
                result["nodeToken"] = task.get("nodeToken")
                infos = []
                for li in li_sel:
                    info = {}
                    noticeType = li['noticeType']
                    court = li['court']
                    tosendPeople = li['tosendPeople']
                    time = li['publishDate']
                    id = li["uuid"]


                    noticeCode = li['noticeCode']
                    pdf_url = 'https://rmfygg.court.gov.cn/court-service/service/downloadpdf'
                    pdf_content = RequestHeler.post(pdf_url,data=noticeCode,headers=headers).content
                    content_url = "https://rmfygg.court.gov.cn/web/rmfyportal/noticedetail?p_p_id=noticedetail_WAR_rmfynoticeDetailportlet&p_p_lifecycle=2&p_p_state=normal&p_p_mode=view&p_p_resource_id=noticeDetail&p_p_cacheability=cacheLevelPage&p_p_col_id=column-1&p_p_col_count=1&_noticedetail_WAR_rmfynoticeDetailportlet_uuid="+id
                    content_resp = RequestHeler.get(content_url, headers=headers)
                    content = content_resp.text
                    time_path = re.sub("-", "/", str(time))
                    pdf = 'bulletin/' + time_path + '/' + id + '.pdf'
                    info = {}
                    info["type"] = noticeType
                    info["person"] = court
                    info["party"] = tosendPeople
                    info["time"] = time
                    info["url"] = pdf_url
                    info["pdf"] = pdf
                    info["id"] = id
                    info["content"] = content
                    infos.append(info)

                    # 下载pdf到本地
                    local_path = os.path.split(os.path.realpath(__file__))[0] + '/temp/' + id + '.pdf'
                    with open(local_path, "wb") as f:
                        f.write(pdf_content)
                    log.info({"machine_name": "proudark009", "key": info["time"] + '-' + info["id"], "state": 3})
                    try:
                        conn = connect(host='180.76.172.153', port=3306, db='courtdoc', user='crawler',
                                       passwd='ark#2017',
                                       charset='utf8')
                        cur = conn.cursor()
                        sql = "INSERT IGNORE INTO bul_content_primary(id,type,person,party,time,pdf,url) VALUES(%s,%s,%s,%s,%s,%s,%s)"
                        cur.execute(sql, (id, noticeType, court, tosendPeople, time, pdf, url))
                        conn.commit()
                    except Exception as e:
                        log.error(e, "插入数据库错误")
                    finally:
                        cur.close()
                        conn.close()
                    try:
                        conn1 = connect(host='180.76.172.153', port=3306, db='courtdoc', user='crawler',
                                       passwd='ark#2017',
                                       charset='utf8')
                        cur1 = conn1.cursor()
                        sql = "INSERT IGNORE INTO bul_content_attachment(id,content) VALUES(%s,%s)"
                        cur1.execute(sql, (id, content))
                        conn1.commit()
                    except Exception as e:
                        log.error(e, "插入数据库错误")
                    finally:
                        cur1.close()
                        conn1.close()
                server_path = '/ps_new/upload/images/dc/bulletin/' + time_path + '/'
                local_path = os.path.split(os.path.realpath(__file__))[0] + '/temp/'
                sftp_upload_file(server_path, local_path, infos)
                result["infos"] = infos
                continue

        except Exception as e:
            log.info({"machine_name": "proudark009", "key": info["time"] + '-'+ info["id"], "state": 1})
            print(e)
            return None


def sftp_upload_file(server_path, local_path,infos):
    host = "180.76.164.253"
    port = 22
    timeout = 30
    user = "upload"
    password = "PS@Letmein123"
    try:
        t = paramiko.Transport((host, port))
        t.connect(username=user, password=password)
        sftp = paramiko.SFTPClient.from_transport(t)
        # 检查服务器文件目录是否存在
        try:
            sftp.stat(server_path)
        except Exception as e:
            # 服务器文件不存在通过paramiko ssh 命令创建
            cmd = "mkdir -p " + server_path
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(host, username=user, password=password, allow_agent=False, look_for_keys=False)
            ssh.exec_command(cmd)
            ssh.close()
        for temp in infos:
            sftp.put(local_path + temp.get("id") + '.pdf', server_path + temp.get("id") + '.pdf')
        t.close()
    except Exception as e:
        logging.exception(e)
        print(e,"log:上传错误...")
    finally:
        # 判断文件是否存在
        for temp in infos:
            path = local_path + temp.get("id") + '.pdf'
            if os.path.exists(path):
                os.remove(path)



if __name__ == '__main__':
    Logger().setup_log
    parse = Parser()
    task = {
        "data":{
            "url":"https://rmfygg.court.gov.cn/web/rmfyportal/noticeinfo?p_p_id=noticelist_WAR_rmfynoticeListportlet&p_p_lifecycle=2&p_p_state=normal&p_p_mode=view&p_p_resource_id=initNoticeList&p_p_cacheability=cacheLevelPage&p_p_col_id=column-1&p_p_col_count=1"
        },
        "project_name":"",
        "nodeToken":1
    }
    result = parse.do(task)
