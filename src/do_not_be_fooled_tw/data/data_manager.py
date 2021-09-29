import pandas as pd 
import threading 
import regex as re 
import datetime 

# ====
# Globals
# ====
MIN_TITLE_LENGTH = 1 
MIN_ARTICLE_LENGTH = 10

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
            self.df.to_excel(self.output_filepath) 
        finally: 
            self.lock.release() 

    # ====
    # Function: sample pre-processing 
    # ====
    def preproc_text (self, text :str): 
        assert(type(text) is str) 

        text = text.strip() 
        text = re.sub('[\s]+', ' ', text)

        return text 

    def preproc_sample (self, sample :Sample): 
        assert(isinstance(sample, Sample))

        post_sample = sample.clone() 

        # title 
        post_sample.data['title']   = self.preproc_text(post_sample.data['title']) 

        # article 
        post_sample.data['article'] = self.preproc_text(post_sample.data['article'])

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