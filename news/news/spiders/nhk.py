import requests
import scrapy
from news.items import NewsItem



class NHKSpider(scrapy.Spider):
    name = 'nhk'
    allowed_domains = ['www3.nhk.or.jp']
  
    custom_settings = {
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'DOWNLOAD_DELAY': 0.5,
        'BOT_NAME': 'news_reader',#
        'LOG_LEVEL': 'DEBUG',
        'LOG_FILE' : 'nhk.log', #
        'ROBOTSTXT_OBEY' : False,  # robots.txt 설정 무시...
        'FEED_EXPORT_ENCODING' : 'utf-8',
        
        'RETRY_ENABLED' : True,
        'RETRY_TIMES': 2,
        
        }
    
    # https://www3.nhk.or.jp/news/json16/new_010.json # new_001 ~ new_010까지. 날짜별로 보여주는 건 없나봐.
    # 0 ~ 19까지 총 20개씩. ['channel']['item'][0]['link'] 형식으로 접근.
    # 'https://www3.nhk.or.jp/news/' + link
    # ['channel']['item'][0]['link'].split('/')[1] 형식으로 날짜 확인.
    
    def start_requests(self):
        # date : YYYYMMDD 형식으로 넣어요.
        # 주의! nhk는 가장 최근 200개의 기사만 보여주므로 날짜가 오늘 날짜와 차이가 크면 결과가 안 나옴!
        # 2~3일만 넘어가도 못 잡는 경우가 있으므로 되도록이면 하루 전 정도로...
        
        news_basic = 'https://www3.nhk.or.jp/news/'
        link_box = []      
        
        for i in range(1,10+1):
            json_url = f'https://www3.nhk.or.jp/news/json16/new_{i:0>3}.json'
            json_res = requests.get(json_url).json()
            for j in range(20):
                partial_link = json_res['channel']['item'][j]['link']
                news_date = partial_link.split('/')[1]

                if self.date == news_date: ############################## 여기에서 오늘 날짜가 사용됩니다.
                    print('통과')
                    yield scrapy.Request(url = news_basic + partial_link, callback = self.article_extractor)
                    
                
    def article_extractor(self, response):
        
        item = NewsItem()
        item['title'] = response.xpath('//h1[@class="content--title"]/span/text()').extract()[0]
                            
        item['date'] = self.date[:4] + '-' + self.date[4:6] + '-' + self.date[6:]
        #date_temp = response.xpath('//p[@class="content--date"]/time/@datetime').extract()[0]
        #item['date'] = date_temp.split('T')[0]
        
        main_part = response.xpath('//div[@class="content--detail-body"]')
        
        try:
            summary = ' '.join(main_part.xpath('.//p[@class="content--summary"]/text()').extract())             
        except:
            summary = ''
        try:
            summary_more = ' '.join(main_part.xpath('./div/p[@class="content--summary-more"]/text()').extract())
        except:
            summary_more = ''
            
        body_box = []
        
        try:
            body_tag = main_part.xpath('./div/section/descendant::text()').extract()
        except:
            body_tag = []
        
        for body_text in body_tag:
            temp = body_text.strip()
            if temp == '':
                continue
            body_box.append(temp)
        
        item['contents'] = summary + summary_more + ' '.join(body_box)