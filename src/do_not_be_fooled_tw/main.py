import os 
import click 
import logging 
import warnings
from . import web_crawler 

# ====
# Main 
# ====
@click.command() 
@click.option('--start-at', type=str, required=True)
@click.option('--life-in-sec', type=int, required=True)
@click.option('--output', type=str, required=True)
@click.option('--debug', type=bool, default=False)
def main(
    start_at :str, 
    life_in_sec :int, 
    output :str,
    debug :bool
):     
    # Turn off warning if not in the debug mode 
    if (not debug): 
        warnings.filterwarnings('ignore')

    # Find out where this web_crawler.py is 
    web_crawler_path = str(web_crawler.__file__)
    print('Web Crawler Path: {}'.format(web_crawler_path))

    # Compose the scrapy command 
    scrapy_command = f'scrapy runspider {web_crawler_path} -a start_at={start_at} -a life_in_sec={life_in_sec} -a output={output}'
    if (not debug): 
        scrapy_command = scrapy_command + ' --nolog' 

    # Run the scrapy command 
    os.system(scrapy_command)
    

if __name__ == '__main__': 
    main() 