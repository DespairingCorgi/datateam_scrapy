import scrapy
from scrapy.spiders import CrawlSpider
from scrapy_app.items import ScrapyAppItem

class VelogSpider(CrawlSpider):
    name = 'velog'

    def __init__(self, *a, **kw):
        self.keyword = kw.get('keyword')
        self.user = kw.get('user')
        self.start_urls = f'https://velog.io/search?q={self.keyword}'
        super(VelogSpider, self).__init__(*a, **kw)

    def start_requests(self):
        yield scrapy.Request(url=self.start_urls, callback=self.parse_posts)

    # 검색 페이지 전체 포스트들 파싱
    def parse_posts(self, response) :
        # 모든 포스트들 파싱
        posts = response.xpath('//*[@id="root"]/div[2]/div[3]/div[2]/div')
        
        # 각 포스트들 href 추출
        for post in posts :
            self.post_url = "https://velog.io" + post.xpath('a/@href').get() 
            # href 추출할 때마다 post_url을 가지고 parse_post 함수 실행
            yield scrapy.Request(self.post_url, callback=self.parse_post)

    # 각 포스트들 파싱
    def parse_post(self, response) :   
        title = response.xpath('//*[@id="root"]/div[2]/div[3]/div/h1/text()').get()
        author = response.xpath('//*[@id="root"]/div[2]/div[3]/div/div[1]/div[1]/span[1]/a/text()').get()
        date = response.xpath('//*[@id="root"]/div[2]/div[3]/div/div[1]/div[1]/span[3]/text()').get()
        tags = response.xpath('//*[@id="root"]/div[2]/div[3]/div/div[2]/a/text()').getall()
        likes = int(response.xpath('//*[@id="root"]/div[2]/div[3]/div/div[3]/div/div/div[2]/text()').get())
        contents = ''.join(response.xpath('//*[@id="root"]/div[2]/div[5]/div/div/p/text()').getall())
        total_comments = response.xpath('//*[@id="root"]/div[2]/div[9]/h4/text()[1]').get()
        comments = response.xpath('//*[@id="root"]/div[2]/div[9]/div/div[2]/div/div/div/div/div/div/p/text()').getall()
        
        # item에 저장
        item = ScrapyAppItem()

        item['title'] = title
        item['author'] = author
        item['date'] = date
        item['tags'] = tags
        item['likes'] = likes
        item['contents'] = contents
        item['total_comments'] = total_comments
        item['comments'] = comments
        item['username'] = self.user
    
        yield item      