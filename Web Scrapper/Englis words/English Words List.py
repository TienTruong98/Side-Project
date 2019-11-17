'''
    Scrapping English words from https://meaningpedia.com/
'''
import bs4
import requests
import logging
import os


def getListURL():
    '''
    scrapping through the https://meaningpedia.com/about.php to get all the word-list's URLs
    :return: a list of URLs
    '''
    url = 'https://meaningpedia.com/about.php'
    request = requests.get(url)
    if request.status_code != 200:
        print(request.status_code)
        exit()
    soup = bs4.BeautifulSoup(request.text, 'lxml')
    list = soup.find_all('li', {'class': 'col-md-3'})
    url_list = []
    regex = 'words starting from'
    for x in list:
        links = x.find_all('a')
        for link in links:
            if regex in link.text.lower():
                url_list.append(link['href'])
    logging.debug('Finish scrapping list URLs')
    with open('word-list-url.txt', mode='w') as f:
        for url in url_list:
            f.writelines(url)
    logging.debug("Finish writing list URLs into 'word-list-url.txt'")


def getWords(url):
    request = requests.get(url)
    if request.status_code != 200:
        exit()
    soup = bs4.BeautifulSoup(request.text, 'lxml')
    span = soup.find_all('span', {'itemprop': 'name'})
    with open(url[-2:]+'.txt',mode='w') as f:
        for x in span:
            f.writelines(url.strip()[-2:])


def iteratingURLs():
    with open('word-list-url.txt', mode='r') as f:
        url_list = f.readlines()
    for url in url_list:
        if os.path.exists(url.strip()[-2:]+'.txt'):
            pass
        else:
            getWords(url.strip())
            logging.debug('Finish get word in {}'.format(url.strip()))




def loggingInitiate():
    urllib3_log = logging.getLogger("urllib3")
    urllib3_log.setLevel(logging.CRITICAL)
    logging.basicConfig(filename='words-list.log', level=logging.DEBUG, format='%(asctime)s: %(message)s')

loggingInitiate()
iteratingURLs()

