import pandas as pd 
import threading 
import datetime 

class DataManager (object): 
    url_col = 'URL'
    title_col = 'TITLE'
    article_col = 'ARTICLE'
    timestamp_col = 'TIMESTAMP'

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
                visited = (len(self.df) == 0 or (url in self.df[self.url_col]))
        finally: 
            if (acquired): 
                self.lock.release() 

        return visited 

    def add (
        self, 
        url, 
        title, 
        article
    ): 
        sample = {
            self.url_col: url, 
            self.title_col: title, 
            self.article_col: article, 
            self.timestamp_col: str(datetime.datetime.now())
        }

        acquired = self.lock.acquire(blocking=True, timeout=10) 
        try: 
            if (acquired): 
                if (len(self.df) == 0 or (url not in self.df[self.url_col])): 
                    self.df = self.df.append(
                        sample, 
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