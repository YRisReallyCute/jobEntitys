# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ZyybdappItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    ym = scrapy.Field()
    bm = scrapy.Field()
    cf = scrapy.Field()
    zffx = scrapy.Field()
    gnzz = scrapy.Field()
    zbff = scrapy.Field()
    jxgg = scrapy.Field()
    yfyl = scrapy.Field()
    zlbz = scrapy.Field()
    syjj = scrapy.Field()
    zysx = scrapy.Field()
    xdyj = scrapy.Field()
    lcyy = scrapy.Field()
    fg = scrapy.Field()
    qtzj = scrapy.Field()
    zc = scrapy.Field()
    lj = scrapy.Field()
    blfy = scrapy.Field()
    yldl = scrapy.Field()
    ywxhzy = scrapy.Field()
    fl = scrapy.Field()
    zxbz = scrapy.Field()
    qt = scrapy.Field()
    url = scrapy.Field()
    create_time = scrapy.Field()
    origin_body = scrapy.Field()

    id=scrapy.Field()   #保存本次执行的任务id
    type=scrapy.Field() #保存任务类型
    log=scrapy.Field()  #保存任务日志
