import requests
import bs4
import time
import multiprocessing
import multiprocessing.pool
import re


class NoDaemonProcess(multiprocessing.Process):
    def _get_daemon(self):
        return False

    def _set_daemon(self, value):
        pass

    daemon = property(_get_daemon, _set_daemon)


class MyPool(multiprocessing.pool.Pool):
    Process = NoDaemonProcess

class ItemScrapper:
    '''
    Scrap flow:
        1. Crawl the display menu page and Get the item URL from the display menu
        2. Enter the item source page and scrap the item info
    '''
    max_attemp = 5
    @staticmethod
    def getItemInfo(url):
        '''
        get the items information (name, price, rating)
        :param url: the item source page
        :return: dict contains item information (name,price,rating,url)
        '''
        attempt = 0
        while attempt < ItemScrapper.max_attemp:
            try:
                response = requests.get(url)
                soup = bs4.BeautifulSoup(response.text, 'lxml')
                # check redirect url
                if int(response.headers['Content-Length']) < 1000:
                    # find the redirect url
                    regex = 'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
                    redirect_url = soup.find_all('script')[0].text
                    redirect_url = re.findall(regex, redirect_url)[0]
                    # change the request to the redirect URL
                    response = requests.get(redirect_url)
                    soup = bs4.BeautifulSoup(response.text, 'lxml')

                name = soup.select_one('.icon-tikinow-26+ span').text
                price = soup.select_one('#span-price').text
                rating = soup.find("meta", attrs={"itemprop": "ratingValue"})['content']

                response.close()
                soup.decompose()
                return {'name': name, 'price': price, 'rating': rating, 'url': url}
            except Exception as e:
                attempt += 1
        return {'name': None, 'price': None, 'rating': None, 'url': url}
    @staticmethod
    def getItemUrls(url):
        '''
        scrap the items URL from the display menu page
        :param url: page URL
        :return: item_url_list: list of items URl
        '''
        try:
            response = requests.get(url)
            soup = bs4.BeautifulSoup(response.text, 'lxml')
            item_url_list = [x['href'] for x in soup.select('.product-box-list .product-item > a')]
            soup.decompose()
            response.close()
            return item_url_list
        except:
            pass
    @staticmethod
    def scrapItemInfo(url):
        '''
        get all information of all items on a display menu
        :param url: the URL of a display menu page
        :return: item_info: list of items information
        '''
        url_list = ItemScrapper.getItemUrls(url)
        item_info = []
        try:
            pool = multiprocessing.Pool()
            item_info = pool.map(ItemScrapper.getItemInfo, url_list)
            pool.close()
            pool.join()
        except Exception as e:
            print(e)
        return item_info
    @staticmethod
    def crawlPage(url):
        '''
        crawl and scrap items information from a list of URLs
        :param url: list of URLs
        :return: info: items information
        '''
        p = MyPool()
        info = p.map(ItemScrapper.scrapItemInfo, url)
        p.close()
        p.join()
        return info



if __name__ == "__main__":
    t1 = time.time()
    url = [
        'https://tiki.vn/may-doc-sach/c28856?src=tree',
        'https://tiki.vn/may-tinh-bang/c1794?src=tree',
        'https://tiki.vn/dien-thoai-pho-thong/c1796?src=tree',
        'https://tiki.vn/dien-thoai-smartphone/c1795?src=tree',
        'https://tiki.vn/dien-thoai-ban/c8061?src=tree'
    ]
    result = ItemScrapper.crawlPage(url)
    i = 0
    for x in result:
        for y in x:
            print(y)
            i += 1
    t2 = time.time()
    print(i)
    print(t2 - t1)
