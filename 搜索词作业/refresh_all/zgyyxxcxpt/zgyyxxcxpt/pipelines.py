# -*- coding: utf-8 -*-
import pymysql
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


class ZgyyxxcxptPipeline(object):
    dbName = {
        0: 'data_disease_xy_zgyyxxcxpt',
        1: 'data_disease_zy_zgyyxxcxpt',
        2: 'data_symptom_xy_zgyyxxcxpt',
        3: 'data_symptom_zy_zgyyxxcxpt'
    }

    def __init__(self):
        # 建立数据库连接
        # self.connection = pymysql.connect(user='cupid', password='mysql@chinark', db='yy_data', port=3306, charset='utf8')
        self.connection = pymysql.connect(user='root', password='root', db='yy_data1', host='127.0.0.1',port=3306,charset='utf8')

        # 创建操作游标
        self.cursor = self.connection.cursor()

    def process_item(self, item, spider):
        sourcedb=self.dbName[item['type']]
        self.cursor.execute("""update"""+sourcedb+"""set origin_url=%s where info_mc=%s""",(item['url'],item['mc']))

    def __del__(self):
        self.cursor.close()
        self.connection.close()
