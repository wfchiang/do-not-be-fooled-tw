from typing import List 
import scrapy 

import datetime 

from data_manager import DataManager 

# ==== 
# Utils for data retrieval  
# ====
def get_title (web_res): 
    assert(isinstance(web_res, scrapy.http.Response))
    titles = web_res.css('title::text').getall() 
    return ' '.join(titles)

def get_articles (web_res): 
    assert(isinstance(web_res, scrapy.http.Response))
    articles = web_res.css('span::text').getall() 
    return articles

def get_links (web_res): 
    assert(isinstance(web_res, scrapy.http.Response))
    links = web_res.css('a::attr(href)').getall() 
    return links 

# ====
# Spider class 
# ====
class WebSpiderMan (scrapy.Spider): 
    name = 'WebSpiderMan' 

    def __init__ (self, **arg): 
        assert('start_at' in arg), '[ERROR] argument "start_at" is missed...'
        self.start_at = arg['start_at']

        if ('life_in_sec' in arg): 
            self.life_in_sec = int(arg['life_in_sec']) 
        else: 
            self.life_in_sec = 1 

        self.data_manager = DataManager(output_filepath='./test.xlsx')
        
        self.start_time = datetime.datetime.now() 
    
    def start_requests (self): 
        assert(type(self.start_at ) is str) 
        yield scrapy.Request(self.start_at, self.parse)

    def parse (self, response):
        url = response.url 
        title = get_title(response) 
        articles = get_articles(response) 
        links = get_links(response) 

        if (len(articles) > 0): 
            article = ' '.join(articles)

            if (not self.data_manager.is_visited(url)): 
                self.data_manager.add(
                    url=url, 
                    title=title, 
                    article=article
                )

                for l in links: 
                    now_time = datetime.datetime.now() 
                    if (now_time - self.start_time > datetime.timedelta(seconds=self.life_in_sec)): 
                        break 

                    try: 
                        yield scrapy.Request(l, self.parse)
                    except: 
                        pass 

    def close (self, reason): 
        self.data_manager.save() 