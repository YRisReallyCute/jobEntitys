# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class SymptomItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    mc = scrapy.Field()
    mcjs = scrapy.Field()
    bm = scrapy.Field()
    ywmc = scrapy.Field()
    fk = scrapy.Field()
    dfrq = scrapy.Field()
    fbbw = scrapy.Field()
    xybm = scrapy.Field()
    bybj = scrapy.Field()
    lcbx = scrapy.Field()
    jbzd = scrapy.Field()
    bzsz = scrapy.Field()
    fj = scrapy.Field()
    zjlf = scrapy.Field()
    yfbj = scrapy.Field()
    yslf = scrapy.Field()
    tnlf = scrapy.Field()
    wfwz = scrapy.Field()
    hl = scrapy.Field()
    yh = scrapy.Field()
    qt = scrapy.Field()
    url = scrapy.Field()
    auth = scrapy.Field()

    id = scrapy.Field()
    log = scrapy.Field()
    type=scrapy.Field()
    responseStatus = scrapy.Field()

class PatentItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    ym = scrapy.Field()
    mcjs=scrapy.Field()
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
    auth = scrapy.Field()

    id = scrapy.Field()
    log = scrapy.Field()
    type=scrapy.Field()
