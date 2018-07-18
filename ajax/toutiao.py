import requests
import re
from urllib.parse import urlencode
from requests.exceptions import RequestException
from bs4 import BeautifulSoup
import pymongo
from config import *
import os
from hashlib import md5
from multiprocessing import Pool

client = pymongo.MongoClient(MONGO_URL)
db = client[MONGO_DB]
headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36"}

def get_page(offset,keyword):
    params ={
    "offset": offset,
    "format": "json",
    "keyword": keyword,
    "autoload": "true",
    "count": "20",
    "cur_tab": "1",
    "from": "search_tab",
    }
    head = {
        "authority": "www.toutiao.com",
        "referer": "https://www.toutiao.com/search/?keyword=%E8%A1%97%E6%8B%8D",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36",
        "x-requested-with": "XMLHttpRequest"
    }
    url = 'https://www.toutiao.com/search_content/?' + urlencode(params)
    try:
        response = requests.get(url, headers=head)
        if response.status_code == 200:
            return response.json()
        return None
    except RequestException:
        print("请求失败")
        return None
 
def parse_page_index(json):
    data = json.get('data')
    if data:
        for item in  data:
            url = item.get('article_url')
            if url:
                yield url

def get_page_detail(url):
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        print("请求失败")
        return None

def parse_page_detail(html,url):
    soup = BeautifulSoup(html,'lxml')
    title = soup.find('title').get_text()
    print(title)
    result = re.compile('JSON.parse((.*)),').search(html)
    data = eval(eval(result.group(1)))
    if data and 'sub_images' in data.keys():
        sub_images = data.get('sub_images')
        images = [item.get('url') for item in sub_images]
        for i in range(len(images)):
            image = images[i].replace('\\', '')
            download_image(image)
            images[i] = image
        return {
            'title':title,
            'image':images,
            'article_url':url
            }
        
def save_mongodb(result):
    try:
        if db[MONGO_TABLE].insert(result):
            print('已存储mongodb')
    except:
        print('存储失败')

def download_image(url):
    print('正在下载',url)
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            save_image(response.content)
    except RequestException:
        print("请求失败")
        
def save_image(content):
    if not os.path.exists('images'):
        os.mkdir('images')
    file_path = '{0}/{1}.{2}'.format('images',md5(content).hexdigest(),'jpg')
    if not os.path.exists(file_path):
        with open(file_path,'wb') as f:
            f.write(content)
    

def main(offset):
    json = get_page(offset,keyword)
    for url in parse_page_index(json):
        html = get_page_detail(url)
        result = parse_page_detail(html,url)
        save_mongodb(result)
        
    
if __name__ == '__main__':
    groups = [i*20 for i in range(GROUP_START,GROUP_END + 1)]
    pool = Pool()
    pool.map(main,groups)