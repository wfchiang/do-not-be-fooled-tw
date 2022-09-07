import json 
from typing import List, Union  
from urllib.parse import urlparse, urljoin 
import scrapy 
import pandas as pd 
import threading 
import regex as re 
import datetime 
import time 
import validators 

# ====
# Globals 
# ====
BLACK_URL_SEGMENTS = [
    '/login/'
]

MIN_TITLE_LENGTH = 1 
MIN_ARTICLE_LENGTH = 10

DEFAULT_CONFIG = {
    "stop_symbols": [
        "|", 
        "【", 
        "】", 
        "● ", 
        "◎ ", 
        "《", 
        "》", 
        "▲",
    ], 
    "stop_phrases": [
        "setn.com", 
        "SETN.COM", 
        "CTWANT", 
        "0:00", 
        "看更多", 
        "中華日報", 
        "民眾日報", 
        "專題報導", 
        "彰化報導", 
        "我要投票",
        "Yahoo奇摩", 
        "中時新聞網", 
        "中天快點TV", 
        "台灣新生報", 
        "台視新聞網", 
        "中廣新聞網", 
        "台灣好新聞", 
        "直接看結果", 
        "三立新聞網",
        "TVBS新聞網", 
        "Yahoo奇摩（新聞）",  
        "Yahoo奇摩（即時新聞）", 
        "今日新聞NOWnews", 
        "鏡週刊Mirror Media", 
        "三立新聞網24小時直播頻道", 
    ]
}

# ====
# Text preprocessor class 
# ====
class TextPreproc (object): 
    def __init__ (self, config_file :Union[str, None]=None): 
        if (config_file is None): 
            self.config = json.loads(json.dumps(DEFAULT_CONFIG)) 
            
        else: 
            with open(config_file, 'r') as f: 
                self.config = json.load(f) 

    def preproc (self, texts :Union[List[str], str]): 
        is_single_str = (type(texts) is str) 

        if (is_single_str): 
            texts = [texts]

        new_texts = [] 
        for t in texts: 
            # remove stop symbols 
            for ss in self.config['stop_symbols']: 
                t = re.sub(ss, ' ', t)
                
            # remove stop phrases
            def _remove_phrase (_p, _t): 
                _t = re.sub(f'^{_p}\s+', ' ', _t) 
                _t = re.sub(f'\s+{_p}$', ' ', _t) 
                _t = re.sub(f'\s+{_p}\s+', ' ', _t) 
                return _t 
                
            for sw in self.config['stop_phrases']: 
                t = _remove_phrase(sw, t) 
                t = _remove_phrase(' '.join(sw), t) 
                
            # reduce spaces 
            t = re.sub('[\s]+', ' ', t)
            t = t.strip() 

            # finish the preproc of a text 
            new_texts.append(t) 

        return (new_texts[0] if (is_single_str ) else new_texts) 

# ====
# Class: Sample
# ====
class Sample (object): 
    def __init__ (self, **args): 
        self.data = {
            'url': None, 
            'title': None, 
            'article': None, 
            'timestamp': str(datetime.datetime.now())
        }

        for argk, argv in args.items():
            assert(argk in self.data), f'[ERROR] invalid field name: {argk}' 

        self.data.update(args)

    def clone (self): 
        return Sample(**self.data)

# ====
# Class: DataManager 
# ====
class DataManager (object): 
    def __init__ (self, output_filepath :str): 
        assert(type(output_filepath) is str)

        self.output_filepath = output_filepath 
        self.df = pd.DataFrame() 

        self.lock = threading.Lock() 

        self.text_preproc = TextPreproc() 

    def is_visited (self, url :str): 
        assert(type(url) is str) 

        visited = True 
        acquired = self.lock.acquire(blocking=True, timeout=10) 
        try: 
            if (acquired): 
                if (len(self.df) == 0): 
                    visited = False 
                else: 
                    visited = (url in self.df['url']) 
        finally: 
            if (acquired): 
                self.lock.release() 

        return visited 

    def add (self, **args): 
        sample = Sample(**args) 

        assert('url' in args), '[ERROR] field "url" missed'
        url = args['url']

        sample = self.preproc_sample(sample)

        if (not self.filter_sample(sample)): 
            return 

        acquired = self.lock.acquire(blocking=True, timeout=10) 
        try: 
            if (acquired): 
                if (len(self.df) == 0 or (url not in self.df['url'])): 
                    self.df = self.df.append(
                        sample.data, 
                        ignore_index=True
                    )
        finally: 
            if (acquired): 
                self.lock.release() 

    def save (self): 
        acquired = self.lock.acquire(blocking=True, timeout=10) 
        assert(acquired)
        try: 
            print('DataManager saving for {} samples'.format(len(self.df)))
            self.df.to_excel(self.output_filepath, encoding='UTF-8', index=False) 
        finally: 
            self.lock.release() 

    # ====
    # Function: sample pre-processing 
    # ====
    def preproc_sample (self, sample :Sample): 
        assert(isinstance(sample, Sample))

        post_sample = sample.clone() 

        # title 
        post_sample.data['title']   = self.text_preproc.preproc(post_sample.data['title']) 

        # article 
        post_sample.data['article'] = self.text_preproc.preproc(post_sample.data['article'])

        # return 
        return post_sample 

    # ====
    # Function: sample filtering 
    # ====
    def filter_sample (self, sample :Sample): 
        assert(isinstance(sample, Sample))

        if (sample.data['url'].strip() == ''): 
            return False 
        
        if (len(sample.data['title']) < MIN_TITLE_LENGTH): 
            return False 

        article = sample.data['article']
        if (len(article) < MIN_ARTICLE_LENGTH): 
            return False 
        if (article.startswith('{{') and article.endswith('}}')): 
            return False 

        return True 

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

    return (' \n'.join(all_titles)).strip()

def get_article (web_res): 
    assert(isinstance(web_res, scrapy.http.Response))
    articles_span_text = web_res.css('span::text').getall() 
    articles_p = web_res.css('p::text').getall() 
    all_articles = articles_span_text + articles_p 

    all_articles = list(filter(is_meaningful_article, all_articles))

    return (' \n'.join(all_articles)).strip() 

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
        self.start_hostname = urlparse(self.start_at).hostname 

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
        if ((now_time - self.start_time).total_seconds() > self.life_in_sec): 
            return True
        return False 

    def is_interesting_url (self, url): 
        parsed_url = urlparse(url) 

        if (not validators.url(url)): 
            return False 

        current_url_host = parsed_url.hostname 
        if (not current_url_host.endswith(self.start_hostname)): 
            return False 
            
        for seg in BLACK_URL_SEGMENTS: 
            if (url.find(seg) >= 0): 
                return False 

        return True 

    def is_abs_url (self, url): 
        if (url.startswith('http') or url.startswith('www')): 
            return True 
        return False 

    def parse (self, response): 
        if (not self.is_timeout()): 
            url = response.url 
            title = get_title(response) 
            article = get_article(response) 
            links = get_links(response) 
        
            if (self.is_interesting_url(url) and len(article) > 0): 
                if (not self.data_manager.is_visited(url)): 
                    self.data_manager.add(
                        url=url, 
                        title=title, 
                        article=article
                    )
    
                    for l in links: 
                        try: 
                            if (not self.is_abs_url(l)): 
                                abs_l = urljoin(url, l)
                            else: 
                                abs_l = l    
                            if (self.is_interesting_url(abs_l)): 
                                yield scrapy.Request(abs_l, self.parse)
                        except: 
                            pass 

    def close (self, reason): 
        self.data_manager.save() 
