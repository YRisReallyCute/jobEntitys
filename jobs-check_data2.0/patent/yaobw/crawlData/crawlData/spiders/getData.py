# -*- coding: utf-8 -*-
import scrapy


class GetdataSpider(scrapy.Spider):
    name = 'getData'
    allowed_domains = ['www.com']
    start_urls = ['http://www.com/']

    def parse(self, response):
        pass
