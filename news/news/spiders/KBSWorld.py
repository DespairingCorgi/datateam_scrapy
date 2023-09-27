import requests
import scrapy
from news.items import NewsItem



class KBSWorldSpider(scrapy.Spider):
    name = 'kbsworld'
    allowed_domains = ['world.kbs.co.kr']
  
    custom_settings = {
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'DOWNLOAD_DELAY': 0.5,
        'BOT_NAME': 'news_reader',#
        'LOG_LEVEL': 'DEBUG',
        'LOG_FILE' : 'kbsworld.log', #
        'ROBOTSTXT_OBEY' : False,  # robots.txt 설정 무시...
        'FEED_EXPORT_ENCODING' : 'utf-8',
        
        'RETRY_ENABLED' : True,
        'RETRY_TIMES': 2,
        
        }
    
    # 변수 lang , date
    
    
    # 언어 코드 ##  a : 아랍어, c: 중국어,  e : 영어, f : 프랑스어, g : 독일어, i : 인도네시아, j : 일본어, r : 러시아어, s : 스페인어, v : 베트남어
    language_code_dict = { 'Arabic' : 'a', 'Chinese' : 'c', 'English' : 'e',
                         'French' : 'f', 'German': 'g', 'Indonesian' : 'i',
                         'Japanese' : 'j', 'Russian' : 'r', 'Spanish' : 's', 'Vietnamese' : 'v' }
    
    def start_requests(self):
        # 날짜별 기사 모음 형식  http://world.kbs.co.kr/service/news_today.htm?lang={language_code}&date=yyyy-mm-dd
        transformed_date = self.date[:4] + '-' + self.date[4:6] + '-' + self.date[6:]
        
        list_url = f'http://world.kbs.co.kr/service/news_today.htm?lang={self.lang}&date={transformed_date}'
        
        yield scrapy.Request(url = list_url, callback = self.news_url_extractor)
    
    def news_url_extractor(self, response):
        
        list_tag = response.xpath('//section[@class="comp_text_1x"]/article')
        # 기사 목록이 비어있는 경우
        if list_tag.extract() == []:
            print("Today's news doesn't exist.")
            return None
        
        basic = 'http://world.kbs.co.kr/service/'
        partial_url_list = list_tag.xpath('./h2/a/@href').extract()
        
        for partial_url in partial_url_list:    
            yield scrapy.Request(url = basic + partial_url, callback = self.article_extractor )
        
    
    def article_extractor(self, response):
        # http://world.kbs.co.kr/service/news_view.htm?lang=v&Seq_Code=57245 형식
        # 이 형식에서 lang값을 바꿔도 정확히 동일한 기사에 대응되진 않음.
        item = NewsItem()
        
        title_area_tag = response.xpath('//div[@class="title_area"]')       
        item['title'] = title_area_tag.xpath('./h1/text()').extract()[0]      
        
        #date_list = title_area_tag.xpath('./p[@class="date"]/text()').extract()
        #item['date'] = ' '.join(date_list[0].split(' ')[1:])[:-3]
        item['date'] = self.date[:4] + '-' + self.date[4:6] + '-' + self.date[6:] # 어차피 하루 단위로 수집한다고 날짜 입력하는데.. 시간도 필요없겠다! 굳이 찾을 필요가 있나!

        article_temp = response.xpath('//div[@class="contents"]//div[@class="body_txt fr-view"]/text()').extract()
        item['contents'] = ' '.join([word.strip() for word in article_temp if word.strip() != ''])
