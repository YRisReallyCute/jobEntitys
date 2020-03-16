from scrapy import cmdline

cmdline.execute("scrapy crawl getData -a id=1006 -a refreshURL=www.baidu.com".split())