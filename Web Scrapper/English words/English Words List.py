'''
    Scrapping English words from https://meaningpedia.com/
'''
import bs4
import requests
import logging
import os
import string


def makeListURL():
    '''
    generating file with list of URLs with sample https://meaningpedia.com/words-that-start-with-?[a-z]
    :return: none
    '''
    url_list = []
    for i in string.ascii_lowercase:
        url_list.append('https://meaningpedia.com/words-that-start-with-'+i)
    with open('word-list-url.txt', mode='w') as f:
        for url in url_list:
            f.write(url)
            f.write('\n')
    logging.debug("Finish writing list URLs into 'word-list-url.txt'")


def getWords(url):
    '''
    get every word in url an write onto a file and return the number of words
    :param URL
    :return: number of words
    '''
    request = requests.get(url)
    if request.status_code != 200:
        logging.warning('HTTP code != 200')
        exit()
    soup = bs4.BeautifulSoup(request.text, 'lxml')
    span = soup.find_all('span', {'itemprop': 'name'})
    with open(url.strip()[-2:] + '.txt', mode='w') as f:
        for x in span:
            f.write(x.text)
            f.write('\n')
    return len(span)


def iteratingURLs():
    '''
    iterating over the 'word-list-url.txt' to scrapping the URLs
    :return: sum of all the worlds
    '''
    with open('word-list-url.txt', mode='r') as f:
        url_list = f.readlines()
    sum = 0
    for url in url_list:
        if not os.path.exists(url.strip()[-2:] + '.txt'):
            temp = getWords(url.strip())
            print(temp)
            sum += temp
            logging.debug('Finish get word in {}'.format(url.strip()))
    return sum


def loggingInitiate():
    '''
    configing the logging
    :return: none
    '''
    urllib3_log = logging.getLogger("urllib3")
    urllib3_log.setLevel(logging.CRITICAL)
    logging.basicConfig(filename='words-list.log', level=logging.DEBUG, format='%(asctime)s: %(message)s')


loggingInitiate()
print(iteratingURLs())