#!/usr/bin/python
# -*-encoding: utf-8-*-

#爬取猫眼电影top100
import requests
from bs4 import BeautifulSoup


def getHtml(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'}
    r = requests.get(url, headers=headers)
    r.encoding = 'utf-8'
    return r.text


def infowriting(url):
    html = getHtml(url)
    soup = BeautifulSoup(html, 'lxml')
    content = soup.find_all(attrs={'class': 'board-item-main'})
    with open('top.txt', 'a',encoding='utf-8') as f:
        for i in content:
            f.write(str(i.text.split())+'\n')

def main():
    start = 'http://maoyan.com/board/4?offset='
    for i in range(0,11):
        url = start + str(i*10)
        infowriting(url)

if __name__ == '__main__':
	main()
