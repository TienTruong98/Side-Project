import bs4
import requests
import logging
import pymongo
import time


def loggingInitiate():
    '''
    configing the logging
    :return: none
    '''
    urllib3_log = logging.getLogger("urllib3")
    urllib3_log.setLevel(logging.CRITICAL)
    logging.basicConfig(handlers=[logging.FileHandler('tiki.log', encoding='utf-8')], level=logging.DEBUG,
                        format='%(levelname)s:%(asctime)s: %(message)s')


class DataPipeline:
    database_name = 'Tiki'
    client = pymongo.MongoClient('localhost', 27017)
    database = client[database_name]

    @classmethod
    def importData(self, collection_name):
        try:
            collection = DataPipeline.database[collection_name]
            logging.debug('Export data from collection "{}"'.format(collection_name))
            return collection.find()
        except Exception:
            logging.exception(Exception)

    @classmethod
    def exportData(self, collection_name, data):
        try:
            collection = DataPipeline.database[collection_name]
            for x in data:
                if collection.find_one({'link': {"$eq": x['link']}}) is None:
                    collection.insert_one(x)
            logging.debug('Import data to collection "{}"'.format(collection_name))
        except Exception:
            logging.exception(Exception)

    @classmethod
    def updateStatus(self, collection_name, document_link, status):
        try:
            collection = DataPipeline.database[collection_name]
            collection.update_one({'link': document_link}, {'$set': {"status": status}})
        except Exception:
            logging.exception(Exception)


class Category:
    @staticmethod
    def getCategoryLinkList():
        '''
        scrapping through tiki main page and search the category of items
        :return: a dictionary includes names of the category and the relevant link samples
        '''
        category_link_list = []
        category_name = []
        print('Getting category link.....')
        logging.debug('Get Category link list')
        try:
            res = requests.get("https://tiki.vn/")
            soup = bs4.BeautifulSoup(res.text, 'lxml')
            for i in soup.find_all("a", class_='MenuItem__MenuLink-tii3xq-1 efuIbv'):
                category_link = i['href']
                end_pos = list(category_link).index('?') + 1
                # get the url sample for iterating through sub page
                category_link = category_link[:end_pos]
                category_link_list.append(category_link)
                # get the category's name
                category_name.append(i.text)
        except Exception:
            print(Exception)
            logging.exception(Exception)
        logging.debug('Finished getting Category link list')
        print('Finished getting Category link list')
        return [{'name': x, 'link': y, 'status': True} for x, y in zip(category_name, category_link_list)]


class SubCategory:

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
    def getCategorySubPage(name, link):
        '''
        getting all pages containing items of the category
        using the hopping method to iterate through pages
        :param link: the category url sample
        :return: list of all category sub page
        '''
        print('Getting sub category of {}...'.format(name))
        count = 0
        sub_page_link_list = []
        k = 100
        # find the last page that still contains items
        while True:
            new_count = count + k
            new_link = link + 'page=' + str(new_count)
            check = SubCategory.checkEnd(new_link)
            if check and k == 1:
                count = new_count
                break
            if check:
                k = k // 10
            else:
                count = new_count
        # generate all the sub pages
        for i in range(1, count + 1):
            new_link = link + 'page=' + str(i)
            sub_page_link_list.append({'name': name, 'page': i, 'link': new_link, 'status': True})
        print('Finished getting sub category of {}'.format(name))
        return sub_page_link_list

    @staticmethod
    def iteratingCategoryLinks():
        '''
        iterating through the 'Category links' collection and making the relevant sub links
        and export to 'Sub links' collection
        :return:
        '''
        for x in DataPipeline.importData('Category links'):
            logging.debug('Scraping "{}"'.format(x['name']))
            if x['status']:
                DataPipeline.exportData('Sub links', SubCategory.getCategorySubPage(x['name'], x['link']))
                DataPipeline.updateStatus('Category links', x['link'], False)
            else:
                print('"{}" is already exist'.format(x['name']))
            logging.debug('Finished scraping "{}"'.format(x['name']))
        logging.debug('Finished scrapping sub category links')


class Item:
    @staticmethod
    def getItemID(soup):
        '''
        getting ID of an item
        :param soup: the page source
        :return: id_list: list of items ID
        '''
        id_list = []
        id_script = ""
        for context in soup.find_all("script"):
            if "ga('ec:addImpression'," in context.text:
                id_script = context.text.strip()
        id_script = id_script.split("ga('ec:addImpression', {")
        id_script.pop(0)
        for i in range(len(id_script)):
            id = id_script[i]
            id = id.strip()
            id = id.split('\n')
            id = int(id[0][6:-2])
            id_list.append(id)
        return id_list

    @staticmethod
    def getInfoItem(link):
        '''
        get information of an item. That includes name, brand, price, rating of the item
        :param link: the page link
        :return: dictionary of items information
        '''
        try:
            res = requests.get(link)
            soup = bs4.BeautifulSoup(res.text, 'lxml')

            name = soup.find("h1")
            name = name.text.strip()

            brand = soup.find("div", class_="item-brand")
            brand = brand.find('p')
            brand = brand.text.strip()

            price = soup.find("span", id="span-price")
            price = price.text

            rating = soup.find("meta", attrs={"itemprop": "ratingValue"})
            rating = rating['content']
            logging.debug('Get {}'.format(name))
            return {'name': name, 'brand': brand, 'price': price, 'rating': rating, 'link': link}
        except:
            return {'name': '', 'brand': '', 'price': '', 'rating': '', 'link': link}

    @staticmethod
    def getItem(link):
        '''
        this function will first scrap the page and find all items ID
        second it will find the link corresponding to that item ID and scrap the item's information
        :param link: the menu page link
        :return: items_info_list f
        '''
        items_info_list = []
        try:
            res = requests.get(link)
            soup = bs4.BeautifulSoup(res.text, 'lxml')
            # get items ID
            item_IDs = Item.getItemID(soup)
            for id in item_IDs:
                item_link = soup.find('a', attrs={"data-id": id})['href']
                # get item's information
                item_information = Item.getInfoItem(item_link)
                items_info_list.append(item_information)
        except Exception as e:
            print(e)
        return items_info_list

    @staticmethod
    def iteratingSubList():
        '''
        iterating through the 'Sub links' collection and get items information
        and export data to the corresponding collection
        :return:
        '''
        for x in DataPipeline.importData('Sub links'):
            logging.debug('Getting item info from {} page {}'.format(x['name'], x['page']))
            if x['status']:
                print('Getting item info from {} page {}...'.format(x['name'], x['page']))
                items_info_list = Item.getItem(x['link'])
                DataPipeline.exportData(x['name'], items_info_list)
                DataPipeline.updateStatus('Sub links', x['link'], False)
                print('Finished getting item info from {} page {}'.format(x['name'], x['page']))
            else:
                print('Item info from {} page {} is already exist'.format(x['name'], x['page']))
            logging.debug('Finished getting item info from {} page {}'.format(x['name'], x['page']))


if __name__ == '__main__':
    t1 = time.time()
    loggingInitiate()
    DataPipeline.exportData('Category links', Category.getCategoryLinkList())
    SubCategory.iteratingCategoryLinks()
    Item.iteratingSubList()
    t2 = time.time()
    print(t2 - t1)
