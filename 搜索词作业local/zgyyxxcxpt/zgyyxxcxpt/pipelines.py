# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql
import datetime

class ZgyyxxcxptPipeline(object):
    noRefresh = 12
    doneRefresh = 11
    doneInsert = 21

    refreshStatus = 20

    dbName={
    'diseaseXydb':'data_disease_xy_zgyyxxcxpt',
    'diseaseZydb':'data_disease_zy_zgyyxxcxpt',
    'symptomXydb':'data_symptom_xy_zgyyxxcxpt',
    'symptomZydb':'data_symptom_zy_zgyyxxcxpt'
    }

    def __init__(self):
        # 建立数据库连接
        # self.connection = pymysql.connect(user='cupid', password='mysql@chinark', db='yy_data', port=3306, charset='utf8')

        self.connection = pymysql.connect(user='root', password='root', db='yy_data1', host='127.0.0.1',
                                          port=3306,charset='utf8')

        # 创建操作游标
        self.cursor = self.connection.cursor()


    def process_item(self, item, spider):
        # 判断来自哪个数据库
        sourcedb=self.dbName[item['type']]

        # 判断是否有更新
        # sql="select * from data_symptom_zy_baidubaike where info_mc=%s"%(item['mc'])
        self.cursor.execute("""select * from """+ sourcedb + """ where info_mc=%s""", (item['mc']))
        insertOrNot = 0
        result = self.cursor.fetchone()
        if (result):
            if (self.isSame(result, item)):
                insertOrNot = self.noRefresh
            else:
                insertOrNot = self.doneRefresh
        else:
            insertOrNot = self.doneInsert

        if (insertOrNot != self.noRefresh):
            self.cursor.execute("""select max(id) from """+sourcedb)
            max_id=self.cursor.fetchone()[0]
            max_id=max_id+1
            # 获取当前时间
            dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.cursor.execute(
                """insert into yy_data1.""" + sourcedb + """(id,info_mc,info_mcjs,info_bm,info_ywmc,info_fk,info_dfrq,info_fbbw,info_xybm,info_bybj,info_lcbx,info_jbzd,info_bzsz,info_fj,info_zjlf,info_yfbj,info_yslf,info_tnlf,info_wfwz,info_hl,info_yh,info_qt,origin_url,create_time,update_time,status)
                            value(%s,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s, %s, %s, %s, %s, %s, %s,%s)""",
                (
            # self.cursor.execute(
            #     """insert into yy_data1."""+sourcedb+"""(id,info_mc,info_mcjs,info_bm,info_ywmc,info_fk,info_dfrq,info_fbbw,info_xybm,info_bybj,info_lcbx,info_jbzd,info_bzsz,info_fj,info_zjlf,info_yfbj,info_yslf,info_tnlf,info_wfwz,info_hl,info_yh,info_qt,origin_url,create_time,update_time,status)
            #     value(%s,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s, %s, %s, %s, %s, %s, %s,%s)""",
            #     (
                    max_id,
                    item['mc'],
                    item['mcjs'],
                    item['bm'],
                    item['ywmc'],
                    item['fk'],
                    item['dfrq'],
                    item['fbbw'],
                    item['xybm'],
                    item['bybj'],
                    item['lcbx'],
                    item['jbzd'],
                    item['bzsz'],
                    item['fj'],
                    item['zjlf'],
                    item['yfbj'],
                    item['yslf'],
                    item['tnlf'],
                    item['wfwz'],
                    item['hl'],
                    item['yh'],
                    item['qt'],
                    item['url'],
                    dt,
                    dt,
                    self.refreshStatus
                )
            )
            # self.count=self.count+1
            self.connection.commit()
            # sql2 = "update data_job_word_search_task set status = 11 where id=%s" % insertOrNot
            self.cursor.execute("""update data_job_word_search_task set status = %s where id=%s""",
                                (insertOrNot, item['id']))
            self.connection.commit()
        return item

    def __del__(self):
        self.cursor.close()
        self.connection.close()

    def isSame(self, result, item):
        print("lll")
        itemArry = ['mc', 'mcjs', 'bm', 'ywmc', 'fk', 'dfrq', 'fbbw', 'xybm', 'bybj', 'lcbx', 'jbzd', 'bzsz',
                    'fj', 'zjlf', 'yfbj', 'yslf', 'tnlf', 'wfwz', 'hl', 'yh', 'qt']
        issame = 1
        for i in range(itemArry.__len__()):
            if (result[i + 1] != item[itemArry[i]]):
                issame = 0
                break

        return issame
