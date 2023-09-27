import scrapy
import json

index = 0
URL='https://www.ted.com/graphql'
GET_LANG_DATA_QUERY = '''
    query ($videoId:ID!){
        video(id: $videoId){
            title
            slug
            description
            publishedAt
            hasTranslations
            publishedSubtitleLanguages{
                edges{
                    node{
                        internalLanguageCode
                    }
                }
            }
        }
    }

'''
GET_TRANSCRIPT_QUERY=''' 
    query ($videoId: ID!, $language: String!){
        video(id: $videoId, language:$language){
            title
            slug
            description
            publishedAt
            internalLanguageCode
            hasTranslations
            
            publishedSubtitleLanguages{
                edges{
                    node{
                        internalLanguageCode
                    }
                }
            }
            
        }
    
    translation(language: $language, videoId: $videoId){
        paragraphs{
            cues{
                    text
                }
            }  
        }
    }
    
'''

GETRECENT_VIDEOS = '''
    query ($first: Int!){
        videos(first: $first){
  	        edges{
                cursor
                node{
                    id
                    slug
                }
            }
        }
    }
'''
HEADERS = {'Content-Type': 'application/json'}

class tedTalksSpider (scrapy.Spider):
    name="tedTalkSpider"
    
    def __init__(self, numVid):
        self.numVid = int(numVid)
        print(self.numVid)
        super().__init__()
    
    def start_requests(self):
        
        variables = {
            "first": self.numVid
        }
        
        
        data = json.dumps({
            "query":GETRECENT_VIDEOS, 
            "variables": variables
        })
        
        yield scrapy.Request(url=URL, 
                             method='POST',
                             headers=HEADERS,
                             dont_filter=True,
                             body=data,
                             callback=self.parse
                             )
    
    def parse(self, res):
        videolst = json.loads(res.text)
        edges = videolst["data"]["videos"]["edges"]
        
        slugs = [e["node"]["slug"] for e in edges]
        
        for slug in slugs:
            variables={
                "videoId": slug,
            }
            data=json.dumps({
                "query":GET_LANG_DATA_QUERY,
                "variables":variables
            })
            
            yield scrapy.Request(url=URL,
                                 method='POST',
                                 headers=HEADERS,
                                 dont_filter=True,
                                 body=data,
                                 callback=self.get_langs,
                                 meta={'slug': slug})
               
        #print(res.text)
        
    def get_langs(self, res):
        video = json.loads(res.text)
        langlist = [e["node"]["internalLanguageCode"] for e in video["data"]["video"]["publishedSubtitleLanguages"]["edges"]]
        print(langlist)
        
        for l in langlist:
            slug = res.meta['slug']
            language = l
            
            variables = {
                "videoId": slug,
                "language": language
            }
            
            data=json.dumps({
                "query": GET_TRANSCRIPT_QUERY,
                "variables": variables
            })
            
            result=scrapy.Request(url=URL,
                                 method='POST',
                                 headers=HEADERS,
                                 dont_filter=True,
                                 body=data,
                                 callback=self.parse_data,
                                 meta={'slug': slug, 'language': language})
            yield result
            print(result.meta['result'])
        
        
            
    def parse_data(self, res):
        global index 
        ###언어가 있는데도 제대로 로딩이 안되는 에러케이스 핸들링 필요####
        
        index+=1
        print(f"{index}: {res.meta['slug']}_{res.meta['language']} done!")
        
        
        #################
        #text
        
        jsondata = json.loads(res.text)
        pragraphs = jsondata['data']['translation']['paragraphs']
        
        #t=''
        for p in pragraphs:
            cue = p['cues']
            for d in cue:
                text = d['text']
                #print(text)
                #텍스트 데이터 저장코드
                #t+=text+'\n'
                #####################
        #res.meta['result'] = t
        