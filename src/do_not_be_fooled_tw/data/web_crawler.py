from typing import List 
from urllib.parse import urlparse 
import scrapy 

import datetime 

from data_manager import DataManager 

# ====
# Globals 
# ====
WHITE_URL_HOSTNAME_SUFFIXES = [
    'setn.com', 
    'tw.news.yahoo.com', 
    'www.chinatimes.com'
]

BLACK_URL_SEGMENTS = [
    '/login/'
]

# ==== 
# Utils for data retrieval  
# ====
def is_meaningful_article (article): 
    if (len(article) < 4): 
        return False 
    return True 

def get_title (web_res): 
    assert(isinstance(web_res, scrapy.http.Response))
    all_titles = [] 

    all_titles = all_titles + web_res.css('h1::text').getall() 
    all_titles = list(map(lambda t: t.strip(), all_titles))
    all_titles = list(filter(lambda t: t!='', all_titles))

    if (len(all_titles) == 0): 
        all_titles = all_titles + web_res.css('h2::text').getall() 
        all_titles = list(map(lambda t: t.strip(), all_titles))
        all_titles = list(filter(lambda t: t!='', all_titles))

    if (len(all_titles) == 0):
        all_titles = all_titles + web_res.css('h3::text').getall() 
        all_titles = list(map(lambda t: t.strip(), all_titles))
        all_titles = list(filter(lambda t: t!='', all_titles))

    return ('\n'.join(all_titles)).strip()

def get_article (web_res): 
    assert(isinstance(web_res, scrapy.http.Response))
    articles_span_text = web_res.css('span::text').getall() 
    articles_p = web_res.css('p::text').getall() 
    all_articles = articles_span_text + articles_p 

    all_articles = list(filter(is_meaningful_article, all_articles))

    return ('\n'.join(all_articles)).strip() 

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

        assert('output' in arg), '[ERROR] argument "output" is missed...'
        output_filepath = arg['output']

        if ('life_in_sec' in arg): 
            self.life_in_sec = int(arg['life_in_sec']) 
        else: 
            self.life_in_sec = 1 

        self.data_manager = DataManager(output_filepath=output_filepath)
        
        self.start_time = datetime.datetime.now() 
    
    def start_requests (self): 
        assert(type(self.start_at ) is str) 
        yield scrapy.Request(self.start_at, self.parse)

    def is_timeout (self): 
        now_time = datetime.datetime.now() 
        if (now_time - self.start_time > datetime.timedelta(seconds=self.life_in_sec)): 
            return True
        return False 

    def is_interesting_url (self, url): 
        parsed_url = urlparse(url) 

        is_whitelisted = False 

        for h_suffix in WHITE_URL_HOSTNAME_SUFFIXES: 
            if (parsed_url.hostname.endswith(h_suffix)): 
                is_whitelisted = True 

        if (not is_whitelisted): 
            return False 
            
        for seg in BLACK_URL_SEGMENTS: 
            if (url.find(seg) >= 0): 
                return False 

        return True 

    def parse (self, response):
        url = response.url 
        title = get_title(response) 
        article = get_article(response) 
        links = get_links(response) 

        if (self.is_timeout()): 
            return 

        if (not self.is_interesting_url(url)): 
            return 

        if (len(article) > 0): 
            if (not self.data_manager.is_visited(url)): 
                self.data_manager.add(
                    url=url, 
                    title=title, 
                    article=article
                )

                for l in links: 
                    try: 
                        yield scrapy.Request(l, self.parse)
                    except: 
                        pass 

    def close (self, reason): 
        self.data_manager.save() 