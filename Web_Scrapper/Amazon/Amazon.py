from selectorlib import Extractor
import requests
import json
import time
import random
import re
from scrapy import Selector


def getDataInfo(url, yaml_file):
    try:
        time.sleep(random.randint(1,3))
        e = Extractor.from_yaml_file(yaml_file)
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0",
                   "Accept-Encoding": "gzip, deflate",
                   "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "DNT": "1",
                   "Connection": "close", "Upgrade-Insecure-Requests": "1"}
        proxies = {
            'http': 'http://134.119.205.253:8080',
            'https': 'http://134.119.205.253:8080',
        }
        r = requests.get(url, headers=headers, proxies=proxies)
        return e.extract(r.text)
    except Exception as e:
        raise e

if __name__ == "__main__":
    t1 = time.time()
    next_page = True
    product = []
    i = 0
    regex = '^\$[0-9]*.[0-9]*'
    url = 'https://www.amazon.com/s?i=electronics-intl-ship&bbn=16225009011&rh=n%3A16225009011%2Cn%3A281407&qid=1574402091&ref=sr_pg_1'
    while i < 10:
        page =True
        while page:
            try:
                a = getDataInfo(url, 'amazon_next_page.yaml')
                link = []
                print(a['next_page'])
                url = 'https://www.amazon.com' + a['next_page']
                for x in set(a['Item']):
                    link.append('https://www.amazon.com' + x)

                for x in link:
                    scrap = True
                    while scrap:
                        try:
                            data = getDataInfo(x, 'Item_info.yaml')
                            product.append(json.dumps(data, indent=True))
                            scrap = False
                        except Exception as e:
                            continue
                page = False
            except Exception as e:
                continue
        i += 1

    print(json.dumps(product, indent=True))
    t2 = time.time()
    print('Taking {} items took {} second'.format(len(product), t2 - t1))
