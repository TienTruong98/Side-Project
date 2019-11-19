import bs4
import requests
import csv
import logging
import pymongo
import pymongo.errors


def loggingInitiate():
    '''
    configing the logging
    :return: none
    '''
    urllib3_log = logging.getLogger("urllib3")
    urllib3_log.setLevel(logging.CRITICAL)
    logging.basicConfig(filename='tiki.log', level=logging.DEBUG, format='%(levelname)s:%(asctime)s: %(message)s')


class Category:
    @staticmethod
    def getCategoryLinkList():
        '''
        scrapping through tiki main page and search the category of items
        :return: a dictionary includes names of the category and the relevant link samples
        '''
        category_link_list = []
        category_name = []
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
        logging.debug('Finished get Category link list')
        return [{'name': x, 'link': y} for x, y in zip(category_name, category_link_list)]

    @staticmethod
    def loadDatabase():
        '''
        load the list onto 'Category link list' collection in 'Tiki' database
        :return:
        '''
        try:
            client = pymongo.MongoClient('localhost', 27017)
            database = client['Tiki']
            col = database['Category link list']
            list = Category.getCategoryLinkList()
            for x in list:
                if col.find_one(x) == None:
                    col.insert_one(x)
            logging.debug("Finished scrapping category link onto 'Category link list' collection in 'Tiki' database")
        except pymongo.errors.PyMongoError as e:
            logging.exception(e)


def getItemID(soup):
    '''
    getting item's id
    :param soup:
    :return:
    '''
    id_list = []
    script = ""
    for context in soup.find_all("script"):
        if "ga('ec:addImpression'," in context.text:
            script = context.text.strip()
    script = script.split("ga('ec:addImpression', {")
    script.pop(0)
    for i in range(len(script)):
        id = script[i]
        id = id.strip()
        id = id.split('\n')
        id = int(id[0][6:-2])
        id_list.append(id)
    return id_list


def getInfoItem(link):
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
        return [name, brand, price, rating, link]
    except:
        return ['', '', '', '', link]


def getItem(link):
    current_page_item_link_list = []
    try:
        res = requests.get(link)
        soup = bs4.BeautifulSoup(res.text, 'lxml')
        # get id of current page's items
        item_id = getItemID(soup)
        for id in item_id:
            item_link = soup.find('a', attrs={"data-id": id})['href']
            item_information = getInfoItem(item_link)
            current_page_item_link_list.append(item_information)
    except Exception as e:
        print(e)
    return current_page_item_link_list


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
    except Exception as e:
        print(e)
        return False


def getCategorySubPage(link):
    '''
    getting all pages containing items of the category
    using the hopping method to iterate through pages
    :param link: the category url sample
    :return: list of all category sub page
    '''
    count = 0
    sub_page_link_list = []
    k = 100
    # find the last page that still contains items
    while True:
        new_count = count + k
        new_link = link + 'page=' + str(new_count)
        check = checkEnd(new_link)
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
        sub_page_link_list.append(new_link)
    return sub_page_link_list


def getFileName():
    with open('./tiki/category.txt', mode='r', encoding='utf-8-sig') as file:
        lines = file.readlines()
    category_name = []
    for i in range(0, len(lines), 2):
        category_name.append(lines[i].strip())
    return category_name


def createCSV():
    category_name = getFileName()
    for name in category_name:
        with open('./tiki/' + name + '.txt', mode='r') as file:
            links = file.readlines()
        with open(name + '.csv', mode='w', newline='', encoding='utf-8-sig') as file_w:
            for link in links:
                print(link)
                list = getItem(link.strip())
                writer = csv.writer(file_w)
                for i in list:
                    print(i)
                    writer.writerow(i)


if __name__ == '__main__':
    loggingInitiate()
    Category.loadDatabase()
