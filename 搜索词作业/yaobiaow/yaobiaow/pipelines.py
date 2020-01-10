# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import datetime

import pymysql


class YaobiaowPipeline(object):
    noRefresh = 11
    doneRefresh = 12
    doneInsert = 21

    refreshStatus = 20

    # 从任务类型转换到待插入数据库
    dbName = {
        6: 'data_patent_yaobw',
        8: 'data_herbal_yaobw',
    }

    def __init__(self):
        # 建立数据库连接
        self.connection = pymysql.connect(user='cupid', password='mysql@chinark', db='yy_data', port=3306,charset='utf8')
        # self.connection = pymysql.connect(user='root', password='root', db='yy_data1', host='127.0.0.1',port=3306,charset='utf8')

        # 创建操作游标
        self.cursor = self.connection.cursor()

    def process_item(self, item, spider):
        # 判断来自哪个数据库
        sourcedb = self.dbName[item['type']]

        # 判断是否有更新
        # sql="select * from data_symptom_zy_baidubaike where info_mc=%s"%(item['mc'])
        self.cursor.execute("""select 
                        id,info_ym,info_cf,info_fl,info_zffx,info_gnzz,info_zbff,info_jxgg,info_yfyl,info_zlbz,info_zysx,info_xdyj,info_lcyy,info_blfy,info_qtzj,info_fg,info_zc,info_lj,info_qt
                        from """ + sourcedb + """ where info_ym=%s ORDER BY id desc""", (item['ym']))
        insertOrNot = 0
        result = self.cursor.fetchone()
        old_id=result[0]

        # 获取插入id
        self.cursor.execute("""select max(id) from """ + sourcedb)
        max_id = self.cursor.fetchone()[0]
        max_id = max_id + 1

        if (result):
            issame, refresh_content = self.isSame(result, item)
            if (issame):
                insertOrNot = self.noRefresh
                item['log'] = "没有更新"
            else:
                insertOrNot = self.doneRefresh
                item['log'] = "有更新，更新内容如下: \r\n" + "旧id: " +str(old_id)+"\r\n新id："+str(max_id) + "\r\n" + refresh_content+"\r\n"+"链接："+item['url']

        else:
            insertOrNot = self.doneInsert
            item['log'] = "新插入id: " + str(max_id)

        if (insertOrNot != self.noRefresh):
            # 获取当前时间
            dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.cursor.execute(
                """insert into yy_data.""" + sourcedb + """(id,info_ym,info_cf,info_fl,info_zffx,info_gnzz,info_zbff,info_jxgg,info_yfyl,info_zlbz,info_zysx,info_xdyj,info_lcyy,info_blfy,info_qtzj,info_fg,info_zc,info_lj
                        ,origin_url,create_time,update_time,origin_body,status,info_qt)
                        value(%s,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s, %s, %s, %s,%s,%s)""",
                (
            # self.cursor.execute(
            #     """insert into yy_data1.""" + sourcedb + """(id,info_ym,info_cf,info_fl,info_zffx,info_gnzz,info_zbff,info_jxgg,info_yfyl,info_zlbz,info_zysx,info_xdyj,info_lcyy,info_blfy,info_qtzj,info_fg,info_zc,info_lj
            #             ,origin_url,create_time,update_time,origin_body,status,info_qt)
            #             value(%s,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s, %s, %s, %s,%s,%s)""",
            #     (
                    max_id,
                    item['ym'],
                    item['cf'],
                    item['fl'],
                    item['zffx'],
                    item['gnzz'],
                    item['zbff'],
                    item['jxgg'],
                    item['yfyl'],
                    item['zlbz'],
                    item['zysx'],
                    item['xdyj'],
                    item['lcyy'],
                    item['blfy'],
                    item['qtzj'],
                    item['fg'],
                    item['zc'],
                    item['lj'],
                    item['url'],
                    dt,
                    dt,
                    item['origin_body'],
                    self.refreshStatus,
                    item['qt']
                )
            )
            # self.count=self.count+1
            self.connection.commit()
            # sql2 = "update data_job_word_search_task set status = 11 where id=%s" % insertOrNot
            self.cursor.execute("""update data_job_word_search_task set status = %s,task_log=%s  where id=%s""",
                                (insertOrNot, item['log'], item['id']))
            self.connection.commit()
        else:
            # 没有更新记录
            self.cursor.execute("""update data_job_word_search_task set status = %s,task_log=%s where id=%s""",
                                (self.noRefresh, item['log'], item['id']))
            self.connection.commit()
        return item

    def __del__(self):
        self.cursor.close()
        self.connection.close()

    def isSame(self, result, item):
        print("lll")
        itemArry = ['ym','cf','fl','zffx','gnzz','zbff','jxgg','yfyl','zlbz','zysx','xdyj','lcyy','blfy','qtzj','fg','zc','lj','qt']
        issame = 1
        refresh_content = ""
        for i in range(itemArry.__len__()):
            if (result[i+1] != item[itemArry[i]]):
                if (issame == 1):
                    issame = 0
                refresh_content += "\r\n" + "info_" + itemArry[i] + ":\r\n\t更新前: " + result[i+1] + "\n\t更新后: " + item[
                    itemArry[i]] + "\r\n"

        return issame, refresh_content

