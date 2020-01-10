# -*- coding: utf-8 -*-
import scrapy
import pymysql
import re
import json
from scrapy import Request
from zgyyxxcxpt.items import ZgyyxxcxptItem


class GetdataSpider(scrapy.Spider):
    name = 'getData'

    title2num={}
    english2chinese={}
    # department对应关系
    l1_cache = {}

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

        # 读取配置文件，一个是title信息，一个是将英文内容转化为中文
        sql3 = "select * from data_conf_symptom_zy_baidubaike_title"
        sql4="select * from data_conf_english_to_chinese"

        cursor = connection.cursor()
        # 取出待爬取的一行task
        cursor.execute(sql)
        result = cursor.fetchone()
        self.url=result[0]

        cursor.execute(sql1)
        result = cursor.fetchone()
        self.type=result[0]

        # 将该行task的status设置为正在爬取
        cursor.execute(sql2)
        connection.commit()

        # 读取从title到num的转换，配置文件
        cursor.execute(sql3)
        results = cursor.fetchall()
        for row in results:
            self.title2num[row[1]] = row[2]

        # 读取从英文列名到中文列名的转换
        cursor.execute(sql4)
        results=cursor.fetchall()
        for row in results:
            self.english2chinese[row[1]]=row[2]
        self.start_urls = ('http://www.dayi.org.cn/',)
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
        item = ZgyyxxcxptItem()
        item['url'] = response.request.url
        itemDic = {}

        # 使用匹配到的title2col中的下标i，item取值对应为itemArry[int(colnum[i])]
        itemArry = ['mc', 'mcjs', 'bm', 'ywmc', 'fk', 'dfrq', 'fbbw', 'xybm', 'bybj', 'lcbx', 'jbzd', 'bzsz',
                    'fj', 'zjlf', 'yfbj', 'yslf', 'tnlf', 'wfwz', 'hl', 'yh', 'qt', 'wxya']
        # 初始化为''
        for i in range(len(itemArry)):
            item[itemArry[i]] = ''

        item['id']=self.id
        type_list=["symptomZydb","symptomXydb","diseaseZydb","diseaseXydb"]
        item['type']=type_list[self.type-2]

        departmentId = {3: '内科', 4: '皮肤性病科', 8: '外科', 1: '妇产科', 2: '儿科', 10: '五官科', 11: '耳鼻喉科', 9: '肿瘤科', 15: '精神心理科',
                        73: '生殖医学科', 77: '急诊科'}

        js = json.loads(response.body.decode("utf-8"))
        list = {}
        level = ''
        if(item['type']=="symptomZydb" or item['type']=="symptomXydb"):
            list = js['symptom']
        else:
            list=js['disease']

        item['mc'] += list['chineseName']
        for each_key in list.keys():
            level_text = ''
            if list[each_key] == None or list[each_key] == "":
                continue
            if each_key in self.english2chinese.keys():
                level = self.english2chinese[each_key]
                col_name = self.find_level(level)
                if col_name != -1:
                    str_tmp = ""
                    if each_key == 'infectivity':
                        if list[each_key] == 0:
                            level_text = '无传染性'
                        else:
                            level_text = '有传染性'
                    elif each_key == 'otherTherapies':
                        list_para = list[each_key].replace('</p>', '').replace('<br />', '').replace('\r', '').replace(
                            '\n', '').replace('\t', '').replace('\xa0', '').split('<p>')
                        para_tmp = ''
                        para_level = ''
                        para_text = ''
                        for each_para in list_para:
                            if each_para == '':
                                continue
                            else:
                                if each_para[0] > '0' and each_para[0] < '9':
                                    if para_level == '':
                                        para_level += each_para
                                        para_text += "<h1>" + para_level + "</h1><br />"
                                    else:
                                        if re.search(r'.*针.*', para_level):
                                            item['zjlf'] += para_text
                                        elif re.search(r'.*中.*药.*', para_level) or re.search(r'.*方.*', para_level):
                                            item['fj'] += para_text
                                        elif re.search(r'.*食.*疗.*', para_level) or re.search(r'.*汤品.*', para_level):
                                            item['yslf'] += para_text
                                        elif re.search(r'.*推拿.*', para_level):
                                            item['tnlf'] += para_text
                                        else:
                                            para_tmp += para_text.replace('h1', 'h2')
                                        para_level = each_para
                                        para_text = "<h1>" + para_level + "</h1><br />"
                                else:
                                    para_text += each_para + '<br />'
                        if para_level != '':
                            if re.search(r'.*针.*', para_level):
                                item['zjlf'] += para_text
                            elif re.search(r'.*中.*药.*', para_level) or re.search(r'.*方.*', para_level):
                                item['fj'] += para_text
                            elif re.search(r'.*食.*疗.*', para_level) or re.search(r'.*汤品.*', para_level):
                                item['yslf'] += para_text
                            elif re.search(r'.*推拿.*', para_level):
                                item['tnlf'] += para_text
                            else:
                                para_tmp += para_text.replace('h1', 'h2')
                        if para_tmp != '':
                            level_text += para_tmp
                    else:
                        level_text = list[each_key].replace('\ue81f', '').replace('\xa0', '')
                        # level_text=list[each_key].replace('<p>','').replace('</p>','<br />').replace('\n','').replace('\t','').replace('\r','').replace('\xa0','').replace('<br />','')
                    if level_text != '':
                        str_tmp += "<h1>" + level + "</h1><br />" + level_text
                        item[col_name] += str_tmp + "<br />"
        # if len(js['departmentNameList'])!=0:
        #     item['fk']+="<h1>就诊科室</h1><br />"+js['departmentNameList'][0]
        if len(js['dislocationNameList']) != 0:
            item['fbbw'] += "<h1>发病部位</h1><br />" + js['dislocationNameList'][0]
        print(self.l1_cache)
        yield item


    def find_level(self, level):
        """
        从标题到数据库中列名的对应关系
        :param level: 网页上爬取到的标题
        :return: 该标题对应的数据库列名
        """
        if self.title2num.get(level) != None:
            return self.title2num[level]
        if re.search(r'.*发病.*', level):
            return 'fbbw'
        if re.search(r'.*西医病名.*', level):
            return 'xybm'
        if re.search(r'.*常见病.*', level):
            return 'jbzd'
        return -1
