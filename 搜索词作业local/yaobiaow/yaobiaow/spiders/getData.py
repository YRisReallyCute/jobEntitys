# -*- coding: utf-8 -*-
import pymysql
import scrapy
from scrapy import Request

from yaobiaow.items import YaobiaowItem


class GetdataSpider(scrapy.Spider):
    name = 'getData'
    title2col={}
    title2name={}

    start_urls = ['http://www.yaobw.cn/yaobw/book.do?flag=show&bookId=1&cid=1&cid2=3']

    def __init__(self,id=0):
        super(GetdataSpider,self).__init__()
        self.id=id
        # connection = pymysql.connect(user='cupid', password='mysql@chinark', db='yy_data', port=3306, charset='utf8')
        connection = pymysql.connect(user='root', password='root', db='yy_data1', port=3306, charset='utf8')
        # 根据id取出待执行任务的信息
        sql = "select origin_url from data_job_word_search_task where id= %s" % self.id
        sql1 = "select job_id from data_job_word_search_task where id= %s" % self.id

        # 将当前状态设置为 待执行
        sql2 = "update data_job_word_search_task set status = 1 where id=%s" % id

        # 读取配置信息
        sql3 = "select title,col,name from data_conf_patent_yaobw_title2col"

        cursor = connection.cursor()
        # 取出待爬取的一行task
        cursor.execute(sql)
        result = cursor.fetchone()
        self.url = result[0]  # 本次待爬取的链接

        cursor.execute(sql1)
        result = cursor.fetchone()
        self.type = result[0]  # 本次任务类型

        # 将该行task的status设置为正在爬取
        cursor.execute(sql2)
        connection.commit()

        # 读取配置信息
        cursor.execute(sql3)
        result = cursor.fetchall()
        for row in result:
            self.title2col[row[0]] = row[1]
            self.title2name[row[0]] = row[2]
        connection.close()


    def parse(self, response):
        url = self.url
        yield Request(url, callback=self.getInfo)

    def getInfo(self,response):
        """
        具体提取信息
        :param response:
        :return:
        """
        item = YaobiaowItem()
        item['url']=response.request.url
        item['id']=self.id
        item['type']=self.type
        item['origin_body'] = response.body.decode('utf-8')

        itemArry=['ym','cf','fl','zffx','gnzz','zbff','jxgg','yfyl','zlbz','zysx','xdyj','lcyy','blfy','qtzj','fg','zc','lj','qt']
        for each in itemArry:
            item[each]=''

        item['ym'] = response.xpath('/html/body/div[1]/div[3]/div[2]/div[3]/pre/center[1]/b/text()').extract()[0]

        # 主体转化为文本之后，使用正则表达式切割后存储到对应的item中
        contain = response.xpath('//*[@id="content_text"]/text()')
        contain_text = ''
        for text in contain:
            contain_text += text.extract().strip()

        list = contain_text.split('【')

        # 查看是否在所需要的标签列表中，如果在的话，将信息提取出来
        for i in range(1, list.__len__()):
            l = list[i].split('】')[0]
            c = list[i].split('】')[1]
            if l in self.title2col.keys():
                item[self.title2col[l]] = "<span class = 'title1'>" + self.title2name[l] + "</span>" + c
            else:
                item['qt']+="<span class = 'title1'>" + l + "</span>" + c

        yield item







