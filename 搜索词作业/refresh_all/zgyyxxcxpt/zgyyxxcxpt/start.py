from scrapy import cmdline

cmdline.execute(("scrapy crawl getData -a type=0").split())