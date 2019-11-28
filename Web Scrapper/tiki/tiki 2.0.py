import requests
import bs4
import time
import multiprocessing
import multiprocessing.pool
import re
import logging


class NoDaemonProcess(multiprocessing.Process):
    def _get_daemon(self):
        return False

    def _set_daemon(self, value):
        pass

    daemon = property(_get_daemon, _set_daemon)


class MyPool(multiprocessing.pool.Pool):
    Process = NoDaemonProcess


class Logger:
    def __init__(self, name, log_file, level=logging.INFO):
        self.name = name
        self.log_file = log_file
        self.level = level

        urllib3_log = logging.getLogger("urllib3")
        urllib3_log.setLevel(logging.CRITICAL)

        formatter = logging.Formatter('%(levelname)s:%(asctime)s: %(message)s')
        handler = logging.FileHandler(self.log_file, encoding='utf-8')
        handler.setFormatter(formatter)

        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(self.level)
        self.logger.addHandler(handler)


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
                    error.logger.info('Redirect: ' + url)
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
                complete.logger.info('Complete getting item: ' + name)
                return {'name': name, 'price': price, 'rating': rating, 'url': url}
            except Exception as e:
                error.logger.exception(e)
                attempt += 1
        missing.logger.info('Missing item: ' + url)
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
        except Exception as e:
            print(e)
            error.logger.exception(e)
            return []

    @staticmethod
    def scrapItemInfo(url):
        '''
        get all information of all items on a display menu
        :param url: the URL of a display menu page
        :return: item_info: list of items information
        '''
        print('Getting items from {}...'.format(url))
        url_list = ItemScrapper.getItemUrls(url)
        item_info = []
        try:
            pool = multiprocessing.Pool()
            item_info = pool.map(ItemScrapper.getItemInfo, url_list)
            pool.close()
            pool.join()
            complete.logger.debug('Complete get page: ' + url)
        except Exception as e:
            print(e)
            error.logger.exception(e)
            missing.logger.debug('Missing page: ' + url)
        return item_info

    @staticmethod
    def crawlPage(url_list):
        '''
        crawl and scrap items information from a list of URLs
        :param url: list of URLs
        :return: info: items information
        '''
        try:
            p = MyPool()
            info = p.map(ItemScrapper.scrapItemInfo, url_list)
            p.close()
            p.join()
            return info
        except Exception as e:
            print(e)
            error.logger.exception(e)


class Category:
    @staticmethod
    def getSubCategory(data_tuple):
        '''
        get the sub-categories of a sub-category
        if the sub-category is the a leaf then store the sub-category data (name, quantity, link) to queue
                                               return []
        else return sub_list
        :param data_tuple: (url, queue)
                            url: sub-category page
                            queue: data queue
        :return: sub-list: list of sub-category
        '''
        url = data_tuple[0]
        queue = data_tuple[1]
        try:
            print('Getting {}...'.format(url))
            current_url = url
            response = requests.get(url, allow_redirects=False)
            # check for redirect page
            if response.status_code != 200:
                current_url = 'https' + response.headers['Location'][4:]  # get the right HTTP protocol
                response = requests.get(url, allow_redirects=True)
            soup = bs4.BeautifulSoup(response.text, 'lxml')
            # get information
            sub_list = ['https://tiki.vn' + x['href'] for x in soup.select('.is-child a')]
            name = soup.select_one('h1').text.strip()
            # quantity = int(''.join(x for x in soup.select_one('.filter-list-box h4').text.strip() if x in '012345679'))

            response.close()
            soup.decompose()
            # check if sub-category ends or not
            if len(sub_list) == 0 or sub_list[0] == current_url:
                queue.put({'name': name, 'quantity': 0, 'link': url})
                return []
            else:
                return sub_list
        except Exception as e:
            print('Exception {}'.format(url))
            print(e)
            return []

    @staticmethod
    def traverseCategoryTree(url_list, queue):
        '''
        recursively crawling through the category tree and get the leaf
        :param url_list: list of node url
               queue: data queue to store leaf
        :return:
        '''
        if len(url_list) != 0:
            pool = MyPool()
            result = pool.map(Category.getSubCategory, [(x, queue) for x in url_list])
            sub_categories = []
            for sub_category in result:
                sub_categories.extend(sub_category)
            pool.close()
            pool.join()
            Category.traverseCategoryTree(sub_categories, queue)

    @staticmethod
    def getLeafCategory(url_list):
        '''
        get leaf categories of a page
        :param url_list: list of url page need to find leaf category
        :return: leaf_category_list: infomation of leaf categories
        '''
        queue = multiprocessing.Manager().Queue()
        Category.traverseCategoryTree(url_list, queue)
        leaf_category_list = []
        while not queue.empty():
            leaf_category_list.append(queue.get())
        return leaf_category_list


error = Logger('error', 'error.log')
missing = Logger('missing', 'missing.log')
complete = Logger('complete', 'complete.log', logging.DEBUG)
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
    for x in result:
        print(x)
    t2 = time.time()
    print(t2 - t1)
