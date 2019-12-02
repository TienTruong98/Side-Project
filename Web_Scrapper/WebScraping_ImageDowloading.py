# this project was made by Natton on 31st, Aug, 2019
import requests
import bs4
import os
import re
import send2trash


def initiate_url():
    '''
    initiate_url will ask for user URL input and get the request from that website
    :return: res: request from user URl
    '''
    while True:
        try:
            url = input('Enter web url: ')
            res = requests.get(url)
        except Exception as e:
            print('Your URL has problem!')
            print(e)
            print('Please try again')
        else:
            return res


def initiate_folder():
    '''
    initiate_folder: will create a new folder for contain downloaded images
    :return: none
    '''
    folder_status = True
    while folder_status:
        try:
            folder_name = input('Enter folder name: ')
            folder_path = os.getcwd() + '\\' + folder_name
            os.mkdir(folder_name)  # create new folder
        except FileExistsError as f:
            print(f)
            # ask user whether delete the existing folder
            while True:
                delete_request = input('Do you want to delete that folder: (Y/N)')
                if delete_request == 'Y':
                    try:
                        send2trash.send2trash(folder_path)
                        os.mkdir(folder_name)
                        os.chdir(folder_path)
                        folder_status = False
                        break
                    except:
                        # if something wrong happend obliterate the folder
                        os.unlink(folder_path)
                elif delete_request == 'N':
                    break
                else:
                    print('Wrong input format')
        except Exception as e:
            print('Something wrong with the OS')
            print(e)
            print('Please try again')
        else:
            os.chdir(folder_path)  # change working path
            folder_status = False


def format_image_link(raw_link):
    '''
    format_image_link: will take the raw_link from soup and change it to the right URL format
    :param raw_link: link form soup.select
    :return:
    '''
    image_link = raw_link
    pattern1 = re.compile(r'https://[\w]+')
    pattern2 = re.compile(r'//[\w]+')
    if re.search(pattern1, image_link):
        pass
    elif re.search(pattern2, image_link):
        image_link = 'https:' + image_link
    else:
        image_link = 'https://' + image_link
    return image_link


def format_image_name(raw_name, image_link, count):
    '''
    format_image_name: will format the image's name based on the 'alt' atributes in 'img' tab
    :param raw_name: 'alt' name
    :param image_link: link of the image
    :param count: image count
    :return:
    '''
    # if there is no 'alt' name: the image will take the default name
    image_name = raw_name
    if image_name == '':
        image_name = 'image' + str(count)
    # check whether the link already has an extension
    if image_link[-5] == '.':
        image_name = image_name + image_link[-1:-5:-1][::-1]
    else:
        image_name = image_name + '.png'
    return image_name


def write_image(image_name, image_request):
    '''
    write_image: write the image as binany stream
    :param image_name:
    :param image_request:
    :return:
    '''
    image = open(image_name, 'wb')
    image.write(image_request.content)
    image.close()


def image_download(res):
    '''
    image_download: download the image from website
    :param res: the website requset
    :return: 
    '''
    soup = bs4.BeautifulSoup(res.text, 'lxml')
    count = 0
    for img in soup.find_all('img'):
        try:
            image_link = format_image_link(img['src'])
            img_res = requests.get(image_link, 'lxml')
            image_name = format_image_name(img['alt'], image_link, count)
            print(image_name + ': ' + image_link)
            write_image(image_name, img_res)
            count += 1
        except Exception as ex:
            print('Something wrong with downloading the image')
            print(ex)


if __name__ == '__main__':
    request = initiate_url()
    initiate_folder()
    image_download(request)
