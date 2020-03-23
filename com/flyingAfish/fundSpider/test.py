# -*- coding=utf-8 -*-
import traceback
import requests
from requests import Response
import random
import datetime
import json
import time
import xlwings
import os
from fake_useragent import UserAgent
from bs4 import BeautifulSoup, ResultSet, Tag

def parseUrl(url, params=None, proxies=None, headers=None):
    if headers is None:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'}
    response: Response = requests.get(url, params=params, proxies=proxies, headers=headers)
    response.raise_for_status()
    response.encoding = 'utf-8'
    return response.text

if __name__ == '__main__':

    url = 'http://api.fund.eastmoney.com/f10/lsjz?fundCode=501081&pageIndex=1&pageSize=90000'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36'
                ,'Referer': 'http://fund.eastmoney.com/501081.html'
               }
    html = parseUrl(url, headers=headers)
    print(html)