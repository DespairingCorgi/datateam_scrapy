import re
import scrapy
from news.items import NewsItem
import urllib


class KoreatimesSpider(scrapy.Spider):
    name = 'koreatimes'
    allowed_domains = ['www.koreatimes.co.kr']
  
    custom_settings = {
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'DOWNLOAD_DELAY': 2.0,
        'BOT_NAME': 'news_reader',#
        'LOG_LEVEL': 'DEBUG',
        'LOG_FILE' : 'koreatimes.log', #
        'ROBOTSTXT_OBEY' : False,  # robots.txt 설정 무시...
        'FEED_EXPORT_ENCODING' : 'utf-8',
        
        'RETRY_ENABLED' : True,
        'RETRY_TIMES': 2,
        
        }
    
    # startDate, endDate가 있으나 모두 date 값 하나만 받는 걸로.
    
    
    def url_creator(self, select = 0, page_num = 1):    
       
        basic_0 = 'https://www.koreatimes.co.kr/www2/common/search.asp?'
        basic_1 = 'https://www.koreatimes.co.kr/www2/common/pages/ajax_search.asp?'
          
        data = {
            'kwd': '',
            'pageNum' : page_num,
            'pageSize' : '10',
            'category' : 'TOTAL',
            'sort' : '',
            'startDate' : self.date,
            'endDate' : self.date,
            'date' : 'select',
            'srchFd' : '',
            'range' : '',
            'author' : 'all',
            'authorData' : '',
        }
        data_component = urllib.parse.urlencode(data)
        added_component = 'mysrchFd=%2FDate'
        
        if select == 0:
            return basic_0 + data_component + added_component
        elif select == 1:
            return basic_1 + data_component + added_component
        else:
            return None
    
    
    def start_requests(self):
        
        yield scrapy.Request(url = self.url_creator(select = 0), callback = self.all_news_checker)     

    
    def all_news_checker(self, response):
        
        articles_text = response.xpath('//font[@style="font-size:11pt"]/font/text()').extract()[0]
        
        articles_num = int(re.search('[\d]+', articles_text)[0])
        
        page_num = articles_num // 10
        left_page = page_num % 10
        
        if left_page == 0:
            for index in range(1, page_num + 1):
                yield scrapy.Request(url = self.url_creator(select = 1, page_num = index), callback = self.news_url_extractor)
        
        else:
            for index in range(1, page_num):
                yield scrapy.Request(url = self.url_creator(select = 1, page_num = index), callback = self.news_url_extractor)
    
    
    def news_url_extractor(self, response):
        
        for address in response.xpath('//div[@class="list_article_headline HD"]/a/@href').extract():
            yield scrapy.Request(url = address, callback = self.article_extractor)
    
    
    def article_extractor(self, response):
        item = NewsItem()
        
        title_temp = response.xpath('//div[@class="view_headline LoraMedium"]/text()').extract()[0]
        item['title'] = title_temp.replace('\n', ' ')

        item['date'] = self.date[:4] + '-' + self.date[4:6] + '-' + self.date[6:]
        #date_box = response.xpath('//div[@class="view_date"]/text()').extract()
        #item['date'] = date_box[0].split(':')[1].strip()[:-3]

        content_temp = ' '.join(response.xpath('//div[@id="startts"]/span/span/text()').extract())
        item['contents'] = content_temp.replace('\n', ' ')
      