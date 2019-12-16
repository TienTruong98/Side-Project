import requests
import bs4
import time
import multiprocessing
import multiprocessing.pool
import re
import logging
import pymongo


class NoDaemonProcess(multiprocessing.Process):
    def _get_daemon(self):
        return False

    def _set_daemon(self, value):
        pass

    daemon = property(_get_daemon, _set_daemon)


class MyPool(multiprocessing.pool.Pool):
    Process = NoDaemonProcess


class DataPipeline:
    database_name = 'Tiki_2'
    client = pymongo.MongoClient('localhost', 27017)
    database = client[database_name]

    @classmethod
    def importData(self, collection_name):
        try:
            collection = DataPipeline.database[collection_name]
            complete.logger.debug('Export data from collection "{}"'.format(collection_name))
            return collection.find()
        except Exception as e:
            error.logger.exception(e)

    @classmethod
    def exportData(self, collection_name, data):
        try:
            collection = DataPipeline.database[collection_name]
            for x in data:
                if collection.find_one({'link': {"$eq": x['link']}}) is None:
                    collection.insert_one(x)
            complete.logger.debug('Export data to collection "{}"'.format(collection_name))
        except Exception as e:
            error.logger.exception(e)

    @classmethod
    def update(self, collection_name, key_name, key_value, field_name, field_value):
        try:
            collection = DataPipeline.database[collection_name]
            collection.update_one({key_name: key_value}, {'$set': {field_name: field_value}})
        except Exception as e:
            print(e)
            error.logger.exception(e)


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
                try:
                    if int(response.headers['Content-Length']) < 1000:
                        # find the redirect url
                        error.logger.info('Redirect: ' + url)
                        regex = 'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
                        redirect_url = soup.find_all('script')[0].text
                        redirect_url = re.findall(regex, redirect_url)[0]
                        # change the request to the redirect URL
                        response = requests.get(redirect_url)
                        soup = bs4.BeautifulSoup(response.text, 'lxml')
                except:
                    pass

                name = soup.select_one('.icon-tikinow-26+ span').text
                price = soup.select_one('#span-price').text
                rating = soup.find("meta", attrs={"itemprop": "ratingValue"})['content']

                response.close()
                soup.decompose()
                complete.logger.info('Complete getting item: ' + name)
                return {'name': name, 'price': price, 'rating': rating, 'link': url}
            except Exception as e:
                error.logger.exception(e)
                attempt += 1
        missing.logger.info('Missing item: ' + url)
        return {'name': None, 'price': None, 'rating': None, 'link': url}

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
    def main(url_list=None):
        '''
        crawl and scrap items information from a list of URLs
        :param url: list of URLs
        :return: info: items information
        '''
        if not url_list:
            url_list = [x for x in DataPipeline.importData('leaf-categories') if x['item-status']]
            last_page = []
            a = []
            for x in url_list:
                a.extend(
                    [{'link': '{}page={}'.format(x['link'][:-8], y), 'category_id': x['_id'], 'status': True} for y in
                     range(1, x['length'] + 1)])
                last_page.append({'link': '{}page={}'.format(x['link'][:-8], x['length']), 'category_id': x['_id']})
            for i in range(0, len(a), batch_num):
                print('batch: {}'.format(i // batch_num))
                batch = [x['link'] for x in a[i:i + batch_num]]
                try:
                    p = MyPool()
                    result = p.map(ItemScrapper.scrapItemInfo, batch)
                    for x in result:
                        DataPipeline.exportData('Item',x)
                except Exception as e:
                    error.logger.exception(e)

                for x in batch:
                    try:
                        end_page = next(i for i in last_page if i['link'] == x)
                        DataPipeline.update('leaf-categories', '_id', end_page['category_id'], 'item-status', False)
                    except StopIteration:
                        pass
                p.close()
                p.join()
        else:
            result = []
            for i in range(0, len(url_list), batch_num):
                print('batch: {}'.format(i // batch_num))
                batch = url_list[i:i + batch_num]
                p = MyPool()
                result.append(p.map(ItemScrapper.scrapItemInfo, batch))
                p.close()
                p.join()
            return result


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
            quantity = int(soup.select_one('.filter-list-box h4').text.strip()[:-8])

            response.close()
            soup.decompose()
            # check if sub-category ends or not
            if len(sub_list) == 0 or sub_list[0] == current_url:
                queue.put({'name': name, 'quantity': quantity, 'link': url, 'status': True, 'item-status': True})
                return []
            else:
                return sub_list
        except Exception as e:
            error.logger.exception('Exception occur at: ' + url)
            error.logger.exception(e)
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
    def main(url_list=None):
        '''
        get leaf categories of a page
        :param url_list: list of url page need to find leaf category
        :return: leaf_category_list: infomation of leaf categories
        '''
        # get tiki main category
        if not url_list:
            try:
                url = 'https://tiki.vn'
                re = requests.get(url)
                soup = bs4.BeautifulSoup(re.text, 'lxml')
                url_list = [x['href'] for x in soup.select('.efuIbv')]
            except Exception as e:
                error.logger.error(e)

        queue = multiprocessing.Manager().Queue()
        Category.traverseCategoryTree(url_list, queue)
        leaf_category_list = []
        while not queue.empty():
            leaf_category_list.append(queue.get())
        complete.logger.debug('Complete getting leaf-categories')
        return leaf_category_list


class EndPage:
    @staticmethod
    def checkEnd(link):
        '''
        checking whether the page still the 'next page' button
        :param link: the page's url
        :return: True: if doesn't has the button
                 False: if has the button or something goes wrong
        '''
        try:
            res = requests.get(link)
            soup = bs4.BeautifulSoup(res.text, 'lxml')
            # find the 'next page' button
            if soup.find('a', class_="next") is None:
                return True
            else:
                return False
        except Exception:
            logging.exception(Exception)
            return False

    @staticmethod
    def getEndPage(url):
        '''
        getting all pages containing items of the category
        using the hopping method to iterate through pages
        :param link: the category url sample
        :return: list of all category sub page
        '''
        if not url:
            return 0
        count = 0
        print('Getting sub category of {}...'.format(url))
        k = 100
        # find the last page that still contains items
        while True:
            new_count = count + k
            new_link = url[:-8] + 'page=' + str(new_count)
            end = EndPage.checkEnd(new_link)
            if end and k == 1:
                count = new_count
                break
            if end:
                k = k // 10
            else:
                count = new_count
        return count

    @staticmethod
    def main(url=None):
        if not url:
            url = [x for x in DataPipeline.importData('leaf-categories') if x['status']]
            print(url)
            for i in range(0, len(url), batch_num):
                print('batch: {}'.format(i // batch_num))
                batch = [x['link'] if x['status'] else None for x in url[i:i + batch_num]]
                p = multiprocessing.Pool()
                result = p.map(EndPage.getEndPage, batch)
                for index, value in enumerate(batch):
                    if value:
                        DataPipeline.update('leaf-categories', 'link', value, 'length', result[index])
                        DataPipeline.update('leaf-categories', 'link', value, 'status', False)
                p.close()
                p.join()
        else:
            result = []
            for i in range(0, len(url), batch_num):
                print('batch: {}'.format(i // batch_num))
                batch = url[i:i + batch_num]
                p = multiprocessing.Pool()
                result.append(p.map(EndPage.getEndPage, batch))
                p.close()
                p.join()
            return result


batch_num = 12
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
        'https://tiki.vn/dien-thoai-smartphone/c1795?src=tree',
        'https://tiki.vn/noi/c891?src=tree',
        'https://tiki.vn/toeic/c896?src=tree',
        'https://tiki.vn/nghe/c890?src=tree'
    ]
    ItemScrapper.main()
    t2 = time.time()
    print(t2 - t1)
