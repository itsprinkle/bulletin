# -*- coding: utf-8 -*-
"""
@Time : 18-3-14 上午11:16
@Author : courage
@Site : 
@File : RabbitmqHelper.py
@Software: PyCharm
"""

import pika
import logging


class RabbitMq(object):
    # 连接对象
    __conn = None

    def __init__(self,config):
        self.__config = config
        self.__rk = config.get("rabbitmq", "routing_key")

    @staticmethod
    def __get_channel(config):
        if RabbitMq.__conn is None or RabbitMq.__conn.is_closed:
            credentials = pika.PlainCredentials(config.get("rabbitmq", "UNAME"), config.get("rabbitmq", "PWD"))
            RabbitMq.__conn = pika.BlockingConnection(pika.ConnectionParameters(config.get("rabbitmq", "HOST"), config.get("rabbitmq", "PORT"), '/', credentials,heartbeat=60))
        channel = RabbitMq.__conn.channel()
        # 声明queue
        channel.queue_declare(config.get("rabbitmq", "queue"))
        return channel

    def publish(self, msg):
        try:
            self.__channel = RabbitMq.__get_channel(self.__config)
            self.__channel.basic_publish(exchange='',routing_key=self.__rk,body=msg)
        except Exception as e:
            logging.exception(e)
            #异常进行第二次消息重发
            self.__channel = RabbitMq.__get_channel(self.__config)
            self.__channel.basic_publish(exchange='', routing_key=self.__rk, body=msg)

    def get(self,callback):
        while True:
            try:
                self.__channel = RabbitMq.__get_channel(self.__config)
                self.__channel.basic_consume(callback, queue=self.__config.get("rabbitmq","queue"), no_ack=True)
                self.__channel.start_consuming()
            except Exception as e:
                logging.exception(e)
