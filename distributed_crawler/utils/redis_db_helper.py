# -*- coding: utf-8 -*-
"""
@Time : 18-3-14 上午11:03
@Author : courage
@Site : 
@File : RedisDBHelper.py
@Software: PyCharm
"""

import redis


class Redis(object):
    # 连接池对象
    __pool = None

    def __init__(self,config):
        # 数据库构造函数，从连接池
        namespace = config.get("redis","qnamespace")
        name = config.get("redis","qname")
        self.__conn = Redis.__get_conn(config)
        self.key = '%s:%s' %(namespace, name)

    @staticmethod
    def __get_conn(config):
        """
        @summary: 静态方法，从连接池中取出连接
        @return redis  连接对象
        """
        if Redis.__pool is None:
            Redis.__pool = redis.ConnectionPool(host=config.get("redis", "RDHOST"),port=config.get("redis","RDPORT"),password = config.get("redis","RDPWD"))
        return redis.Redis(connection_pool=Redis.__pool)

    def qsize(self):
        return self.__conn.llen(self.key)  # 返回队列里面list内元素的数量

    def put(self, item):
        print(self.key,item)
        self.__conn.rpush(self.key, item)  # 添加新元素到队列最右方

    def get_wait(self, timeout=None):
        # 返回队列第一个元素，如果为空则等待至有元素被加入队列（超时时间阈值为timeout，如果为None则一直等待）
        item = self.__conn.blpop(self.key, timeout=timeout)
        # if item:
        #     item = item[1]  # 返回值为一个tuple
        return item

    def get_nowait(self):
        # 直接返回队列第一个元素，如果队列为空返回的是None
        item = self.__conn.lpop(self.key)
        return item