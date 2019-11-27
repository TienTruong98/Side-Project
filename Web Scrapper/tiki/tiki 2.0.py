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


def getItemInfo(url):
    '''
    get the items information (name, price, rating)
    :param url: the item source page
    :return: dict contains item information (name,price,rating,url)
    '''
    atemp = 0
    while atemp<5:
        try:
            regex = 'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
            r = requests.get(url)
            soup = bs4.BeautifulSoup(r.text, 'lxml')
            # check redirect url
            if int(r.headers['Content-Length']) < 1000:
                x = soup.find_all('script')[0].text
                x = re.findall(regex, x)[0]
                r = requests.get(x)
                soup = bs4.BeautifulSoup(r.text, 'lxml')

            name = soup.select_one('.icon-tikinow-26+ span').text
            price = soup.select_one('#span-price').text
            rating = soup.find("meta", attrs={"itemprop": "ratingValue"})['content']
            r.close()
            soup.decompose()
            return {'name': name, 'price': price, 'rating': rating, 'url':url}
        except Exception as e:
            atemp +=1
    return {'name': '', 'price': '', 'rating': '', 'url':url}


def getItemUrls(url):
    try:
        r = requests.get(url)
        soup = bs4.BeautifulSoup(r.text, 'lxml')
        product = soup.select('.product-box-list .product-item > a')
        soup.decompose()
        r.close()
        url_list = []
        item_info = []
        for x in product:
            url_list.append(x['href'])
        try:
            p = multiprocessing.Pool()
            item_info = p.map(getItemInfo, url_list)
            p.close()
            p.join()
        except Exception as e:
            print(e)
        return item_info
    except:
        pass


if __name__ == "__main__":
    t1 = time.time()
    url = [
        'https://tiki.vn/may-doc-sach/c28856?src=tree',
        'https://tiki.vn/may-tinh-bang/c1794?src=tree',
        'https://tiki.vn/dien-thoai-pho-thong/c1796?src=tree',
        'https://tiki.vn/dien-thoai-smartphone/c1795?src=tree',
        'https://tiki.vn/dien-thoai-ban/c8061?src=tree'
    ]
    p = MyPool()
    result = p.map(getItemUrls, url)
    p.close()
    p.join()
    i = 0
    for x in result:
        for y in x:
            print(y)
            i += 1
    t2 = time.time()
    print(i)
    print(t2 - t1)
