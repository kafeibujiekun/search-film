#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/3/10 0:27
# @Author  : 
# @File    : functions.py
# @Software: PyCharm
import requests
import re
import os
from bs4 import BeautifulSoup
from urllib import parse
from contextlib import closing

req_header = {
                 'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                 'accept-encoding': 'gzip, deflate, br',
                 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36'
              }
search_header = {
                 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36'
                 }
searchBaseUrl = 'http://www.415.net/search-index-keyword-{}.htm'


def searchFilm(filmName):
    request_url = searchBaseUrl.format(parse.quote(filmName))
    searchResult = {}

    # print("search", request_url)
    resp = requests.get(request_url, headers=search_header).text
    soup = BeautifulSoup(resp, "html.parser")
    label_table = soup.find('div', class_='body threadlist').find_all('table')
    for table in label_table:
        # print('----------------------------------------------------------------')
        label_a = table.find_all('a')

        filmInfo = []
        for a in range(len(label_a)):
            if a == 0 or a == 1 or a == len(label_a) - 1:
                continue
            if a == len(label_a)-2:
                for i in range(len(label_a[a].contents)):
                    label_a[a].contents[i] = re.compile("<.*?>").subn('', str(label_a[a].contents[i]))[0]
                filmInfo.append("\n" + ''.join(label_a[a].contents) + "\n")
                # print(''.join(label_a[a].contents))
                continue
            for i in range(len(label_a[a].contents)):
                label_a[a].contents[i] = re.compile("<.*?>").subn('', str(label_a[a].contents[i]))[0]
            filmInfo.append(''.join(label_a[a].contents))

            # print(''.join(label_a[a].contents))
            # filmInfo.append(''.join(label_a[a].contents))
            # info = ''.join(label_a[a].contents).strip()

        # print(label_a[0]['href'])
        # filmInfo.append(label_a[0]['href'] + "\n")
        searchResult.update({''.join(filmInfo): label_a[0]['href']})
    return searchResult


def getFilmInfo(url):
    filmInfo = []
    url_request = url
    data = requests.get(url_request, headers=search_header).text
    soup = BeautifulSoup(data, "html.parser")

    result = str(soup.find('div', class_='message'))
    info = "<!DOCTYPE html>\n<html>\n<p>Not Found</p>\n</head>\n</html>\n"
    info = re.sub(re.compile(r'<p>.*</p>'), result, info)
    filmInfo.append(info)

    result = soup.find('div', class_='attachlist').find_all('a')
    for a in result:
        matchObj = re.match(r'http:\/\/.*.htm', a['href'])
        if matchObj:
            BTFileName = str(a.contents[1])
            filmInfo.append(BTFileName)
            downloadUrl = matchObj.group(0)
            filmInfo.append(downloadUrl)
    return filmInfo

def downloadBtFile(fileName, url):
    if not os.path.exists("download"):
        os.mkdir("download")

    data = requests.get(url).text
    soup = BeautifulSoup(data, "html.parser")
    downloadUrl = soup.find('a')['href'].strip("\\\"").replace("\\", '')
    # print(downloadUrl)

    session = requests.Session()
    resp = requests.get(url=downloadUrl, headers=req_header, allow_redirects=False)
    # print(resp.headers['Location'])
    BTUrl = resp.headers['Location']
    r = requests.get(BTUrl)
    with open("download/" + fileName, "wb") as code:
        code.write(r.content)
        code.close()

def isConnected():
    try:
        html = requests.get("http://www.baidu.com", timeout=4)
    except:
        return False
    return True


if __name__ == '__main__':
    if isConnected() == True:
        print("网络已连接")
    else:
        print("网络断开")
    # test = searchFilm("海王")
    # print(test)
    # for i in test:
    #     print(i)

    info = getFilmInfo('http://www.btbtt06.com/thread-index-fid-1-tid-18672.htm')
    downloadBtFile(info[1], info[2])