import scrapy
import urllib.parse
import os
import json
from youtube.items import YoutubeItem

#os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
API_KEY = 'AIzaSyCnU1SN56rFEdmccXhyjXmSh5zAvUHq3K0'
API_SEARCH_REQ = 'https://www.googleapis.com/youtube/v3/search'
API_COMMENTTHREAD_REQ = 'https://www.googleapis.com/youtube/v3/commentThreads'

SEARCH_PARAMS = {
    'key' : API_KEY, #auth가 아니라 key이다. 기억해두자.
    'part' : 'id',
    'maxResults' : '10',
    'type' : 'video',
    'regionCode' : 'us',
    'order' : 'date'
}

COMMENT_PARAMS = {
    'key':API_KEY,
    'part' : 'snippet,replies',
    'maxResults' : '50'
}

class youtubespider(scrapy.Spider):
    name='ys'
    #max contents -> 최대 몇개의 유투브를 긁어올 것인가
    #코멘트 단위
    def __init__(self, keyword, max_contents='10', regioncode='us'):
        SEARCH_PARAMS['q'] = keyword
        SEARCH_PARAMS['maxResults'] = max_contents
        SEARCH_PARAMS['regionCode'] = regioncode
        super().__init__()
    
    def start_requests(self):
        yield scrapy.Request(API_SEARCH_REQ+'?'+urllib.parse.urlencode(SEARCH_PARAMS))
    
    def parse(self, res):
        #reduce index
        #get current response
        curres = json.loads(res.text)
        #print(curres)
        
        curitems = curres['items']
        print(len(curitems))
        
        # for item in curitems:
        #     print(item['id']['videoId'])
        
        for item in curitems:
            print(item['id']['videoId'])
            curid = item['id']['videoId']
            curparam = COMMENT_PARAMS
            curparam['videoId'] = curid
            yield scrapy.Request(API_COMMENTTHREAD_REQ+'?'+urllib.parse.urlencode(COMMENT_PARAMS),meta={'vid':curid} ,callback=self.parse_commmets)

        # if next_token and self.recurr:
        #     curParms = SEARCH_PARAMS
        #     curParms['nextPageToken'] = next_token
        #     yield scrapy.Request(API_REQ+'?'+urllib.parse.urlencode(curParms))
        
    def parse_commmets(self, res):
        curres = json.loads(res.text)
        next_token=curres['nextPageToken'] if 'nextPageToken' in curres.keys() else ''
        
        curitems = curres['items']
        
        for i in curitems:
            #print(i['snippet']["topLevelComment"]["snippet"]["textOriginal"])
            c = YoutubeItem()
            c['comment'] = i['snippet']["topLevelComment"]["snippet"]["textOriginal"]
            c['published'] = i['snippet']["topLevelComment"]['snippet']['publishedAt'][:10]
            print(c['published'])
            #print("comment published at: "+i['snippet']["topLevelComment"]['snippet']['publishedAt'])
            yield c
            
            if i["snippet"]["totalReplyCount"]:
                #print(i["snippet"]["totalReplyCount"])
                if 'replies' in i.keys():
                    #print('found replies')
                    for j in i['replies']["comments"]:
                        #print(j['snippet']['textOriginal'])
                        r = YoutubeItem()
                        r['comment']=j['snippet']['textOriginal']
                        r['published'] = j['snippet']['publishedAt'][:10]
                        print(r['published'])
                        #print('reply: '+ r['comment'])
                        #print('reply published at: '+r['published'])
                        yield r
        curid = res.meta['vid']
        if next_token:
            #print(next_token, '다음 장을 찾았습니다')
            curparam = COMMENT_PARAMS
            curparam['videoId'] = curid
            curparam['pageToken'] = next_token
            yield scrapy.Request(API_COMMENTTHREAD_REQ+'?'+urllib.parse.urlencode(COMMENT_PARAMS),meta={'vid':curid} ,callback=self.parse_commmets)