# -*- coding: utf-8 -*-
import scrapy
import pymysql
import re

from scrapy import Request

from baidubaike.items import BaidubaikeItem


class GetdataSpider(scrapy.Spider):
    name = 'getData'
    # allowed_domains = ['baidu.com']
    base_site='https://baike.baidu.com/item/'
    # 特殊一级标题，这些标题下的二级标题可能会被存在其他列下
    special_l1 = ['辨证施治', '辨证论治', '辨证要点', '预防保健', '预防', '其他疗法', '其他治疗']

    # 需要存储两个位置的标题，这些标题需要存在多个列下
    multi_pos_l1 = {'预防调护': ['yfbj', 'hl']}

    title2num={}
    # 未给出的标题cache
    l1_cache = []
    text_cache = []
    l2_cache = []
    l2_text_cache = []

    l1_name = {}
    l2_name = {}

    def __init__(self,id=0,*args,**kwargs):
        super(GetdataSpider,self).__init__(*args,**kwargs)
        self.id=int(id)
        connection=pymysql.connect(user='root',password='root',db='yy_data1',port=3306,charset='utf8')
        sql="select * from data_job_word_search_task where id= %s" %self.id
        sql2="update data_job_word_search_task set status = 1 where id=%s" %self.id
        sql3="select * from data_conf_symptom_zy_baidubaike_title"
        cursor=connection.cursor()
        # 取出待爬取的一行task
        cursor.execute(sql)
        self.result=cursor.fetchone()

        #将该行task的status设置为正在爬取
        cursor.execute(sql2)
        connection.commit()

        #读取从title到num的转换，配置文件
        cursor.execute(sql3)
        results=cursor.fetchall()
        for row in results:
            self.title2num[row[1]] = row[2]
        self.start_urls = ['https://baike.baidu.com']
        connection.close()


    def parse(self, response):
        url='https://baike.baidu.com/item/%s'%self.result[1]
        yield Request(url,callback=self.getInfo)


    def getInfo(self,response):
        item = BaidubaikeItem()
        item['id']=self.id

        # 将每一个item初始化为''
        itemArry = ['mc', 'mcjs', 'bm', 'ywmc', 'fk', 'dfrq', 'fbbw', 'xybm', 'bybj', 'lcbx', 'jbzd', 'bzsz',
                    'fj', 'zjlf', 'yfbj', 'yslf', 'tnlf', 'wfwz', 'hl', 'yh', 'qt', 'url', 'auth']
        for i in range(len(itemArry)):
            item[itemArry[i]] = ''

            # URL的值
            item['url'] = response.request.url

            # 名词
            item['mc'] = response.xpath('//dd[@class="lemmaWgt-lemmaTitle-title"]/h1/text()').extract()[0]

        # 权威认证
        authority = response.xpath('//*[@class="page-background"]').extract()
        if (len(authority) > 0):
            item['auth'] = 1
        else:
            item['auth'] = 0

        # 名词解释
        mcjs_text = ''
        mcjs_para = response.xpath('//div[@class="lemma-summary"]/div[@class="para"]/text()').extract()
        for each_t1 in mcjs_para:
            mcjs_text = mcjs_text + each_t1 + '<br/>'
        item['mcjs'] = mcjs_text

        # ------------------------------------基本信息部分----------------------------------------

        # 所有能爬取到的一级标题及其对应内容
        level1 = []
        level1_text = []

        base_div_arry = response.xpath('.//div')
        for each_base_div in base_div_arry:
            # 根据class属性判断是否是基本信息部分
            kk = each_base_div.css('::attr(class)').extract()
            while type(kk) is list and len(kk) > 0:
                kk = kk[0]
            if len(kk) == 0: continue

            if re.search(r'.*[b B]ase.*[i I]nfo.*', kk):
                for each_dl in each_base_div.xpath('.//dl'):
                    dt = each_dl.xpath('./dt/text()').extract()
                    dd = each_dl.xpath('./dd/text()').extract()
                    for j in range(len(dt)):
                        level1.append(self.replace_special(dt[j]))
                        level1_text.append(self.replace_special(dd[j]))

        for i in range(len(level1)):
            tmp_ind = self.find_level(level1[i])
            if tmp_ind != -1:
                tmp_l = '<h1>' + level1[i] + '</h1>' + '<br/>'
                item[tmp_ind] += tmp_l + level1_text[i]
            else:
                if (level1[i] not in self.l1_name.keys()):
                    self.l1_name[level1[i]] = item['mc']
                self.l1_cache.append(item['mc'] + '\t' + level1[i])
                self.text_cache.append(level1_text[i])

        # -------------------------------------正文部分-------------------------------------------

        tmp_l1 = ''  # 存放一级标题
        tmp_l1_text = ''  # 存放一级标题及其下内容
        tmp_l3 = ''  # 存放二级标题
        tmp_l3_text = ''  # 存放二级标题及其下内容
        tmp_l3_num = 0  # 存放当前二级标题下是否有内容
        tmp_col = ''  # 存放二级标题内容应该放到哪列下面，列名

        tmp_l1 = response.xpath('//div[@class="para-title level-2"]/h2/text()').extract_first()
        if (tmp_l1 == None):
            tmp_l1 = ""
        else:
            tmp_l1 = self.replace_special(tmp_l1)
        tmp_l1_text = tmp_l1_text + '<h1>' + tmp_l1 + '</h1>' + '<br/>'
        level1.append(tmp_l1)

        divArry = response.xpath('//div[@class="para-title level-2"]/following-sibling::div')  # 选出同级的所有div

        # 逐个div进行提取
        for each_div in divArry:
            css = each_div.css('::attr(class)').extract()[0]

            # -------------------------------- 一级标题 -----------------------------------------
            if css == 'para-title level-2':
                # 如果有还未写入的l3，将其写入
                if tmp_l3_num != 0:
                    item[tmp_col] += '<h1>' + tmp_l1 + '</h1>' + '<br/>' + tmp_l3_text
                else:
                    tmp_l1_text += tmp_l3_text
                tmp_l3 = ''  # 更新l2
                tmp_l3_text = ''
                tmp_col = ''
                tmp_l3_num = 0

                # 更新tmp_l1的值，并将tmp_l1_text写进对应的item中
                if self.multi_pos_l1.get(tmp_l1) != None:  # 是否需要写入多个列中
                    col_arry = self.multi_pos_l1[tmp_l1]
                    for each_col in col_arry:
                        item[each_col] += tmp_l1_text
                else:
                    number = self.find_level(tmp_l1)
                    if (number == ""):
                        continue
                    if number == -1:
                        # 没找到，写进cache里
                        if (tmp_l1 not in self.l1_name.keys()):
                            self.l1_name[tmp_l1] = item['mc']
                        self.l1_cache.append(item['mc'] + '\t' + tmp_l1)
                        self.text_cache.append(tmp_l1_text)
                    else:
                        # 找到了，写进对应的item里
                        item[number] += tmp_l1_text
                # 重置tmp值
                tmp_l1 = self.replace_special(each_div.xpath('./h2/text()').extract()[0])
                tmp_l1_text = ''
                tmp_l1_text += '<h1>' + tmp_l1 + '</h1>' + '<br/>'

            # -------------------------------- 二级标题 -----------------------------------------
            if css == 'para-title level-3':
                # 先将缓存的特殊二级标题内容写入，特殊标题写入特殊列
                if tmp_l3_num != 0:
                    item[tmp_col] += '<h1>' + tmp_l1 + '</h1>' + '<br/>' + tmp_l3_text
                else:  # 非特殊标题写入tmp_l1_text
                    tmp_l1_text += tmp_l3_text
                # 清空缓存
                tmp_col = ''
                tmp_l3_num = 0

                level2 = each_div.xpath('./h3/text()').extract()[0]
                level2 = self.replace_l2(level2)
                tmp_l3 = level2
                # 写进cache里
                if (level2 not in self.l2_name.keys()):
                    self.l2_name[level2] = item['mc']
                tmp_l3_text = '<h2>' + tmp_l3 + '</h2>' + '<br/>'
                if self.is_special(tmp_l1, tmp_l3) != '':
                    tmp_l3_num = 1
                    tmp_col = self.is_special(tmp_l1, tmp_l3)

            # -------------------------------- 正文内容 -----------------------------------------

            if css == 'para':
                tmp_str = ''
                para_text = each_div.xpath('.//text()').extract()
                b_text = each_div.xpath('./b/text()').extract()
                # 判断此时的一级标题是否是特殊标题
                tmp_l1 = self.replace_special(tmp_l1)
                tmp_l3 = self.replace_special(tmp_l3)

                if len(para_text) < 2 and len(para_text) > 0:
                    if len(b_text) > 0:  # 二级标题
                        if tmp_l3_num != 0:
                            item[tmp_col] += '<h1>' + tmp_l1 + '</h1>' + '<br/>' + tmp_l3_text
                        else:  # 非特殊标题写入tmp_l1_text
                            tmp_l1_text += tmp_l3_text
                        # 清空缓存
                        tmp_col = ''
                        tmp_l3_num = 0
                        # 更新tmp_l3的值
                        tmp_l3 = b_text[0]
                        # 写进cache里
                        if (tmp_l3 not in self.l2_name.keys()):
                            self.l2_name[tmp_l3] = item['mc']
                        tmp_l3_text = '<h2>' + tmp_l3 + '</h2>' + '<br/>'
                        if self.is_special(tmp_l1, tmp_l3) != '':
                            tmp_l3_num = 1
                            tmp_col = self.is_special(tmp_l1, tmp_l3)
                    else:  # 一段话
                        if tmp_l3 != '':
                            tmp_l3_text += para_text[0]
                        else:
                            tmp_l1_text += para_text[0]
                else:  # 很多段话
                    for each_para_text in para_text:
                        tmp_str += self.replace_special(each_para_text)
                    if tmp_l3 != '':
                        tmp_l3_text += tmp_str
                    else:
                        tmp_l1_text += tmp_str

        # 如果有还未写入的l3，将其写入
        if tmp_l3_num != 0:
            item[tmp_col] += '<h1>' + tmp_l1 + '</h1>' + '<br/>' + tmp_l3_text
        else:
            tmp_l1_text += tmp_l3_text

        # 是否需要写入多个列中
        if self.multi_pos_l1.get(tmp_l1) != None:
            col_arry = self.multi_pos_l1[tmp_l1]
            for each_col in col_arry:
                item[each_col] += tmp_l1_text
        else:
            number = self.find_level(tmp_l1)
            if number != "":
                if number == -1:
                    # 没找到，写进cache里
                    self.l1_cache.append(item['mc'] + '\t' + tmp_l1)
                else:
                    # 找到了，写进对应的item里
                    item[number] += tmp_l1_text

        for each_key in self.l1_name.keys():
            print(each_key + '\t' + self.l1_name[each_key])

        print("/r/n----------二级标题------------/r/n")

        for each_key in self.l2_name.keys():
            print(each_key + '\t' + self.l2_name[each_key])

        yield item

    # ----------------------------函数find_level--------------------------------
    # 根据字典的key值（一级标题）返回对应的列名
    def find_level(self, level):
        if self.title2num.get(level) != None:
            return self.title2num[level]
        if re.search(r'.*发病.*', level):
            return 'fbbw'
        if re.search(r'.*西医病名.*', level):
            return 'xybm'
        if re.search(r'.*常见病.*', level):
            return 'jbzd'
        return -1

    # ----------------------------函数is_special--------------------------------
    # 判断是不是特殊的二级标题，如果是特殊的二级标题，返回应当放到的列名
    def is_special(self, level1, level2):
        itemName = ''
        if re.search(r".*辨证施治.*", level1):
            # 根据二级标题分类
            if re.search(r".*辨证要点.*", level2):
                itemName = 'jbzd'
            elif re.search(r".*基本方药.*", level2):
                itemName = 'fj'
            elif re.search(r".*针灸.*", level2):
                itemName = 'zjlf'
            else:
                itemName = ''

        elif re.search('辨证论治', level1):
            if re.search(r".*辨证要点.*", level2):
                itemName = 'jbzd'

        elif re.search('其他疗法', level1) or re.search('其他治疗', level1):
            if re.search(r".*针灸.*", level2):
                itemName = 'zjlf'
            elif re.search(r".*饮食.*", level2):
                itemName = 'yslf'
            elif re.search(r".*外治.*", level2) or re.search(r".*外敷.*", level2):
                itemName = 'wfwz'
            elif re.search(r".*推拿.*", level2):
                itemName = 'tnlf'

        elif re.search('辨证要点', level1):
            if re.search(r".*治疗原则.*", level2):  # 10
                itemName = 'bzsz'

        elif re.search('预防保健', level1):
            if re.search(r".*中草药.*", level2):  # 10
                itemName = 'fj'

        elif re.search('预防', level1):
            if re.search(r".*中.*药.*", level2):
                itemName = 'fj'
            elif re.search(r".*食疗.*", level2):
                itemName = 'yslf'
            elif re.search(r".*汤品.*", level2):
                itemName = 'yslf'

        else:
            itemName = ''

        return itemName

    # ----------------------------函数replace_special--------------------------------

    def replace_special(self, str):
        nstr = str.strip().replace('\t', '').replace('\xa0', '').replace('\u3000', '').replace('辩', '辨').replace(
            '：', '').replace(' ', '')
        return nstr

    # ----------------------------函数replace_special--------------------------------
    # 去除二级标题的标号，不保留其顺序
    def replace_l2(self, str):
        # 如果有其他形式可以再添加
        nstr = self.replace_special(str)
        nstr = nstr.replace('一、', '').replace('二、', '').replace('三、', '').replace('四、', '').replace('五、', '')
        return nstr
