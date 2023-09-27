import requests
import scrapy
from news.items import NewsItem

from scrapy import Selector



class SedailySpider(scrapy.Spider):
    name = 'sedaily'
    allowed_domains = ['www.sedaily.com']
  
    custom_settings = {
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'DOWNLOAD_DELAY': 0.5,
        'BOT_NAME': 'news_reader',#
        'LOG_LEVEL': 'DEBUG',
        'LOG_FILE' : 'sedaily.log', #
        'ROBOTSTXT_OBEY' : False,  # robots.txt 설정 무시...
        'FEED_EXPORT_ENCODING' : 'utf-8',
        
        'RETRY_ENABLED' : True,
        'RETRY_TIMES': 2,
        
        }
    
    # https://www.sedaily.com/robots.txt 서울경제.. 너란 녀석 정말 친절하게 다 안내해주는구나.
    # https://www.sedaily.com/daily-news/YYYYMMDD # 해당 날짜의 모든 기사에 대한 링크가 준비되어 있음.
    # News봇 걸러야함...
        
    def start_requests(self):
        # https://docs.scrapy.org/en/latest/topics/spiders.html
        # ex > scrapy crawl sedaily -a date=20230101
        # YYYYMMDD format         
        # 문서에 의하면...start_requests 내에서 self.(변수명)으로 써두면 그 변수명에 해당하는 값 받을 수 있고 확인 완료.
        
        basic = 'https://www.sedaily.com/daily-news/'
        yield scrapy.Request(url = f"{basic}{self.date}", callback = self.news_url_extractor)
                
    def news_url_extractor(self, response):
        sel = Selector(text = response.text)
        for news_url in sel.xpath('//loc/text()').extract():
            yield scrapy.Request(url = news_url, callback = self.article_extractor)
            
    def article_extractor(self, response):
        
        check_category = response.xpath('//div[@class="article_head"]/div/a/text()')[2].extract()
        if check_category in ['News봇', '포토', '해외증시']:
            return None
        
        item = NewsItem()
        item['title'] = response.xpath('//h1[@class="art_tit"]/text()').extract()[0]
        
        item['date'] = self.date[:4] + '-' + self.date[4:6] + '-' + self.date[6:]
        #info_tag = response.xpath('//div[@class="article_info"]/span')
        #item['date'] = info_tag[0].xpath('./text()').extract()[0].replace('.','-').split(' ')[0]
        
        try:
            article_temp = [article_chunk.strip() for article_chunk in response.xpath('//div[@class="article_view"]/text()').extract() if article_chunk.strip() != '']
        except:
            article_temp = []
            
        item['contents'] = ' '.join(article_temp)
        
        