import datetime
import json
import random
import requests
import scrapy
import time



from nvblog.items import NvblogItem

class BlogSpider(scrapy.Spider):
    name = 'blog'
    allowed_domains = ['blog.naver.com']  
    
    custom_settings = {
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'DOWNLOAD_DELAY': 2.0,
        'BOT_NAME': 'i_need_jeongsi_toegeun',
        'LOG_LEVEL': 'DEBUG',
        'LOG_FILE' : 'blog.log',  # log 파일 위치
        'ROBOTSTXT_OBEY' : False, # 
        'FEED_EXPORT_ENCODING' : 'utf-8',
        
        'RETRY_ENABLED' : True,
        'RETRY_TIMES': 2,
        
        'ITEM_PIPELINES' : {'nvblog.pipelines.NvblogPipeline': 300},
    }
    
    
    # 형식 보고 갑시다
    # response.xpath('//span/text()') 로 긁으면
    ''' 
    ...
    '전체보기'
    '목록열기'
    <<<<< 제목 >>>>>
    \n
    \n
    \n
    <<<<< 시간 정보 >>>>>
    '본문 기타 기능'
    <<<<< 본문 주르륵 >>>>>
    
    '저작자 명시 필수'
    '동일조건 유지시 변경 허가'
    ...
    '''
    
    def start_requests(self):
        header = { 'Referer' : ''}
        
        # 블로그홈 글은 리스트 100번까지 존재.
        for page in range(1, 100+1):                       
            header['Referer'] = f'https://section.blog.naver.com/BlogHome.naver?directoryNo=0&currentPage={page}&groupId=0'
            page_url = f'https://section.blog.naver.com/ajax/DirectoryPostList.naver?pageNo={page}'
            
            time.sleep(random.uniform(2,3))
            #print(f'블로그 홈 글 리스트 {page:>3}')
            
            yield scrapy.Request(url = page_url, headers = header, callback = self.post_url_extractor)
    
    def post_url_extractor(self, response):
        post_url_json = json.loads(response.text[6:].strip())
        
        for chunk in post_url_json['result']['postList']:
            blogId = chunk['domainIdOrBlogId']
            logNo = chunk['logNo']
            post_url = f'https://blog.naver.com/PostView.naver?blogId={blogId}&logNo={logNo}&topReferer=https://section.blog.naver.com/BlogHome.naver?directAccess=false'
            
            time.sleep(random.uniform(2,3))
            print(f'블로그 글 ID : {blogId}, N : {logNo}')
            
            yield scrapy.Request(url = post_url, callback = self.post_content_extractor)
    
    def post_content_extractor(self, response):
        
        item = NvblogItem()
        
        text_box = response.xpath('//td[@class="bcc"]//div[@class="se-component-content"]//span/text()').extract()
        
        title_idx = 0
        for idx, text_chunk in enumerate(text_box):
            if '\n' in text_chunk:
                title_idx = idx - 1
                break
        
        item['title'] = ' '.join(chunk.strip() for chunk in text_box[:title_idx + 1] if chunk.strip() != '')
        
        if '시간 전' in text_box[title_idx + 4]:
            hour = int(text_box[title_idx + 4].replace('시간 전',''))
            pub_date = datetime.datetime.now() - datetime.timedelta(hours = 6)
            item['date'] = f"{pub_date.year:>4}-{pub_date.month:0>2}-{pub_date.day:0>2}"
        else:
            item['date'] = '-'.join(num.strip() for num in text_box[title_idx + 4].split('.')[:-1])
        
        content_box = [content.replace('\u200b','').strip() for content in text_box[title_idx + 6:] ]
        item['contents'] = ' '.join( [ content for content in content_box if content not in ['', ' ', '\n','\t','\r'] ] )
        
        #print(f"title : {item['title']}")
        #print(f"{response.url}")
        #print(f"contents : {item['contents'][:10]}")
        #print('==========================')
        
        return item
        