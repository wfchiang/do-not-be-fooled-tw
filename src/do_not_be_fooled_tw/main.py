import os 
import click 
from . import web_crawler 

# ====
# Main 
# ====
@click.command() 
@click.option('--start-at', type=str, required=True)
@click.option('--life-in-sec', type=int, required=True)
@click.option('--output', type=str, required=True)
def main(
    start_at :str, 
    life_in_sec :int, 
    output :str
): 
    web_crawler_path = str(web_crawler.__file__)
    os.system(f'scrapy runspider {web_crawler_path} -a start_at={start_at} -a life_in_sec={life_in_sec} -a output={output}')
    
    print(web_crawler_path)

if __name__ == '__main__': 
    main() 