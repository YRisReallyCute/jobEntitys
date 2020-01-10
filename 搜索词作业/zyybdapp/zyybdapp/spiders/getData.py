# -*- coding: utf-8 -*-
import re

import pymysql
import scrapy
from scrapy import Request
from zyybdapp.items import ZyybdappItem


class GetdataSpider(scrapy.Spider):
    name = 'getData'

    start_urls = ['http://zhongyao2.fenxiangjingling.com']
    # 基础路由
    base_site = 'http://zhongyao2.fenxiangjingling.com'

    title2col={}
    title2name={}

    def __init__(self,id=0):
        super(GetdataSpider,self).__init__()
        self.id=id
        connection = pymysql.connect(user='cupid', password='mysql@chinark', db='yy_data', port=3306, charset='utf8')
        # connection = pymysql.connect(user='root', password='root', db='yy_data1', port=3306, charset='utf8')
        # 根据id取出待执行任务的信息
        sql = "select origin_url from data_job_word_search_task where id= %s" % self.id
        sql1 = "select job_id from data_job_word_search_task where id= %s" % self.id

        # 将当前状态设置为 待执行
        sql2 = "update data_job_word_search_task set status = 1 where id=%s" % id

        # 读取配置信息
        sql3 = "select title,col,name from data_conf_patent_zyybd_title2col"

        cursor = connection.cursor()
        # 取出待爬取的一行task
        cursor.execute(sql)
        result = cursor.fetchone()
        self.url = result[0]    #本次待爬取的链接

        cursor.execute(sql1)
        result = cursor.fetchone()
        self.type = result[0]   #本次任务类型

        # 将该行task的status设置为正在爬取
        cursor.execute(sql2)
        connection.commit()

        # 读取配置信息
        cursor.execute(sql3)
        result = cursor.fetchall()
        for row in result:
            self.title2col[row[0]]=row[1]
            self.title2name[row[0]]=row[2]
        connection.close()


    def parse(self, response):
        url=self.url
        yield Request(url,callback=self.getInfo)


    def getInfo(self,response):
        """
        具体提取信息
        :param response:
        :return:
        """
        item = ZyybdappItem()
        item['url']=response.request.url
        item['origin_body'] = response.body.decode('utf-8')
        item['id']=self.id
        item['type']=self.type

        #初始化
        itemArry=['ym','bm','cf','zffx','gnzz','zbff','jxgg','yfyl','zlbz','syjj','zysx','xdyj','lcyy','fg','qtzj','zc','lj','blfy','yldl','ywxhzy','fl','zxbz','qt']
        for each in itemArry:
            item[each]=''

        #text_list获取页面全部文本信息，text为拼接为一段文本
        text_list = response.xpath('//body//text()').extract()
        text=''

        for each_t in text_list:
            text += each_t

        # 去掉text中的特殊字符
        text = text.replace('\r', '').replace(' ', '').replace('\n', '').replace('\t', '')

        origin_split = text.split('【')
        title_result = []
        content_result = []
        # 从药名开始，到最后的 查看更多 前结束
        for i in range(1, origin_split.__len__() - 1):
            title_result.append(origin_split[i].split('】')[0])
            content_result.append(origin_split[i].split('】')[1])

        content_result[content_result.__len__() - 1] = content_result[content_result.__len__() - 1].split('打开')[0]

        #将得到的标题和内容逐一写入
        if title_result.__len__() > 1:
            print(title_result)
            for i in range(title_result.__len__()):
                each_res = title_result[i]
                if each_res in self.title2col.keys():
                    item[self.title2col[each_res]] += "<span class = \"title_1\">" + self.title2name[each_res] + "</span>" + content_result[i]
                else:
                    item['qt']+="<span class = \"title_1\">" + self.title2name[each_res] + "</span>" + content_result[i]

        #药名字段只保留中文内容，不要拼音
        pat=re.compile(r'[\u4e00-\u9fa5]+')
        result=pat.findall(item['ym'])
        str_ym=''
        for each in result:
            str_ym+=each
        item['ym']=str_ym[2:]

        yield item













