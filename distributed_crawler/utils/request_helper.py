# -*- coding: utf-8 -*-
"""
@Time : 18-3-14 下午3:52
@Author : courage
@Site : 
@File : RequestHelper.py
@Software: PyCharm
"""
import requests
import logging


class RequestHeler(object):

    @staticmethod
    def get(url,params=None,retry=4,**kwargs):
        response = None
        for i in range(retry):
            try:
                response = requests.get(url,params=params,**kwargs)
                break
            except TimeoutError as e:
                print("request get time out :",url)
                continue
            except Exception as e:
                logging.error(e)
                # logging.exception(e)
                # traceback.print_exc()
                continue
        return response

    @staticmethod
    def post(url,data=None,json=None,retry=4,**kwargs):
        response = None
        for i in range(retry):
            try:
                response = requests.post(url,data=data,json=json,**kwargs)
                break
            except TimeoutError as e:
                print("request post time out :", url)
                continue
            except Exception as e:
                logging.error(e)
                continue
        return response
