# -*- coding: utf-8 -*-
import scrapy
import json
import pymysql
import requests

from zgyyxxcxpt.items import ZgyyxxcxptItem


class GetdataSpider(scrapy.Spider):
    name = 'getData'
    allowed_domains = ['www.baidu.com']
    # start_urls = ['http://39.105.161.146:9999/api/disease/queryDiseaseList?diseaseType=1&pageNo=1&pageSize=1000']#2：中医，1：西医
    start_urls = ['http://39.105.161.146:9999/api/disease/queryDiseaseList?pageNo=1&pageSize=10000']

    title2num = {}
    english2chinese = {}
    l1_cache = {}

    def __init__(self,type):
        super(GetdataSpider,self).__init__()
        self.type=int(type)

        # 0：西医疾病    1：中医疾病
        # 2：西医症状    3：中医症状
        # 4：错误
        # TODO:暂无中医疾病，平台找不到
        type2url={
            0:'http://39.105.161.146:9999/api/disease/queryDiseaseList?pageNo=1&pageSize=10000',
            1:'http://39.105.161.146:9999/api/disease/queryDiseaseList?diseaseType=2&pageNo=1&pageSize=10000',
            2:'http://39.105.161.146:9999/api/symptom/list?symptomType=16&pageSize=10000&type=symptom',
            3:'http://39.105.161.146:9999/api/symptom/list?symptomType=15&pageSize=10000&type=symptom'
        }
        type2base={
            0: 'http://39.105.161.146:9999/api/disease/',
            1: 'http://39.105.161.146:9999/api/disease/',
            2: 'http://39.105.161.146:9999/api/symptom/',
            3: 'http://39.105.161.146:9999/api/symptom/'
        }

        self.start_urls=type2url[self.type]
        self.start_url=type2url[self.type]
        self.base_site=type2base[self.type]

        # 读取配置信息
        # connection = pymysql.connect(user='cupid', password='mysql@chinark', db='yy_data', port=3306, charset='utf8')
        connection = pymysql.connect(user='root', password='root', db='yy_data1', port=3306, charset='utf8')
        # 读取配置文件，一个是title信息，一个是将英文内容转化为中文
        sql1 = "select * from data_conf_symptom_zy_baidubaike_title"
        sql2 = "select * from data_conf_english_to_chinese"

        cursor = connection.cursor()
        # 读取从title到num的转换，配置文件
        cursor.execute(sql1)
        results = cursor.fetchall()
        for row in results:
            self.title2num[row[1]] = row[2]

        # 读取从英文列名到中文列名的转换
        cursor.execute(sql2)
        results = cursor.fetchall()
        for row in results:
            self.english2chinese[row[1]] = row[2]
        self.start_urls = ('http://www.dayi.org.cn/',)
        connection.close()


    def parse(self, response):
        """
        对网页元素进行具体定位，//表示跳级定位
        :param response: URL爬取到的内容
        :return:
        """
        # body=response.body.decode("utf-8")
        keyword={
            'pageNo':1,
            'pageSize':10000
        }
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36'}  # 创建头部信息

        body=requests.get('http://39.105.161.146:9999/api/disease/queryDiseaseList',keyword,headers)
        js = json.loads(requests.get(self.star_url))
        id_list = js['list']
        for each_id in id_list:
            str_id = str(each_id['id'])
            url = self.base_site + str_id
            # url=base_site+str(1006070)headers
            yield scrapy.Request(url, callback=self.getInfo)

    def getInfo(self,response):
        item=ZgyyxxcxptItem()
        item['url'] = response.request.url
        item['type']=self.type
        js = json.loads(response.body.decode("utf-8"))

        if (item['type'] == "symptomZydb" or item['type'] == "symptomXydb"):
            list = js['symptom']
        else:
            list = js['disease']
        item['mc'] += list['chineseName']

        yield item