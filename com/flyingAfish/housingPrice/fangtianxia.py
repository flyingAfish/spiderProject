# -*- coding=utf-8 -*-
import traceback
import requests
from requests import Response
import datetime
import json
import time
import xlwings
import os
from fake_useragent import UserAgent
from bs4 import BeautifulSoup, ResultSet, Tag

class fangtianxia:
    def __init__(self, citys=[], city='bj', page=1, innerPage=1, isEndPage=3):
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'}
        self.citys = citys
        self.city = city
        self.page = page
        self.innerPage = innerPage
        self.isEndPage = isEndPage  # 判断三次获取的内容都为空则说明是最后一页
        self.nhUrl = 'https://%s.newhouse.fang.com/house/s/b9%d/'%(self.city, self.page)  # 新房
        self.esfUrl = 'https://esfUrl.fang.com/'  # 二手房
        self.zuUrl = 'https://zuUrl.fang.com/'  # 租房
        self.cityUrl = 'https://www.fang.com/SoufunFamily.htm'  # 城市列表

    def playSound(self):
        from playsound import playsound
        playsound('../sound/111.mp3')

    def printLog(self, filename, log):
        logPth = './log'
        print(os.path.abspath('./'))
        if not os.path.exists(logPth):
            os.makedirs(logPth)
        _time = datetime.datetime.now()
        _log = "Logger:" + str(_time) + ' ' + log
        with open(logPth + '/' + self.city + '_' + filename, 'at', encoding='utf-8', buffering=4028) as f:
            f.write(_log + '\n')
            f.flush()

    def saveCity(self, cityData):
        cityPath = './data'
        if not os.path.exists(cityPath):
            os.makedirs(cityPath)
        # {id:{prov:[(city,py,bref)]}}
        if not isinstance(cityData, dict):
            print("cityDate must be dict type")
            return
        with open(cityPath + '/city.pro', 'wt', encoding='utf-8') as f:
            for prov in cityData.values():
                for cityList in list(prov.values())[0]:
                    data = cityList[0] + ' ' + cityList[1]
                    f.write(data + '\n')
       
            f.flush()
    def savePage(self, data):
        pagePath = './data'
        if not os.path.exists(pagePath):
            os.makedirs(pagePath)
        with open(pagePath + '/' + self.city +'_page.pro', 'at', encoding='utf-8') as f:
            f.write(data + '\n')
            f.flush()

    def saveExcel(self, data, bookName, sheetName):
        """"
        """
        wb = xlwings.Book(bookName)
        sheet = wb.sheets.add(sheetName)
        sheet.range('A').value = data
        wb.save('./data/excelData/' + bookName +'.xlsx')

    def generateHeader(self, sum):
        headersList = []
        for i in range(sum):
            header = {'User-Agent': UserAgent().random}
            headersList.append(header)
        return headersList

    def updateUrl(self):
        self.nhUrl = 'https://%s.newhouse.fang.com/house/s/b9%d/'%(self.city, self.page)  # 新房
        self.esfUrl = 'https://esfUrl.fang.com/'  # 二手房
        self.zuUrl = 'https://zuUrl.fang.com/'  # 租房
        self.cityUrl = 'https://www.fang.com/SoufunFamily.htm'  # 城市列表

    def parseUrl(self, url, params=None, proxies=None, headers=None):
        if headers is None:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'}
        response: Response = requests.get(url, params=params, proxies=proxies, headers=headers)
        response.raise_for_status()
        response.encoding = 'gb2312'
        return response.text

    def printResp(self, url):
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'}
        print(self.parseUrl(url, headers=headers))

    def getData(self, urlType, params=None, proxies=None):
        # 新房
        if urlType == 'nhUrl':
            houseInfos = {}
            while self.isEndPage:
                print(self.nhUrl)
                try:
                    html = self.parseUrl(self.nhUrl, params=params, proxies=proxies)
                except Exception:
                    self.savePage('page ' + str(self.page) + ' ' + self.nhUrl + ' ' + 'erro')
                    self.printLog('logFile.log', '[erro]page&&&' + self.nhUrl)
                    self.isEndPage -= 1
                    continue
                self.printLog('logFile.log', self.nhUrl)
                self.savePage('page ' + str(self.page) + ' ' + self.nhUrl + ' ' + 'ok')
                bs = BeautifulSoup(html, 'html.parser')
                houseList = bs.find('div', attrs={'id': 'newhouse_loupai_list'})\
                    .find('ul').find_all('li')
                print(houseList, ':', len(houseList))

                # 生成headers
                headersList = self.generateHeader(len(houseList))
                innerPage = 0
                for house in houseList:
                    # print(house)
                    # a = house.find(name='div', attrs={'class': 'clearfix'}).find('div').find('a')
                    a = house.select('div[class="clearfix"] > div > a')
                    if len(a) > 0 :
                        href = 'https:' + a[0]['href']
                        print(href)
                        # 更换headers
                        self.headers = headersList.pop()
                        print(self.headers)
                        innerPage += 1
                        if innerPage < self.innerPage:
                            self.innerPage = 1
                            continue
                        try:
                            innerHtml = self.parseUrl(href, params=None, headers=self.headers, proxies=proxies)
                        except Exception:
                            self.printLog('logFile.log', '[erro]&&&' + href)
                            self.savePage('innerPage ' + str(innerPage) + ' ' + href + ' ' + 'erro')
                            continue
                        self.printLog('logFile.log', href)
                        innerBs = BeautifulSoup(innerHtml, 'html.parser')
                        infoList = innerBs.find('div', attrs='information')
                        if isinstance(infoList, Tag):
                            title = infoList.find('div', attrs={'class': 'inf_left1'}).find('h1').get_text()
                            score = infoList.find('div', attrs={'class': 'inf_left1'}).find('a').get_text()
                            aList = infoList.find('div', attrs={'class': 'information_li pdb10'}).find('div').find_all('a')
                            symbol = set()
                            for a in aList:
                                symbol.add(a.get_text())
                            price = infoList.find('div', attrs={'class': 'information_li mb5'}).find('span').get_text()
                            try:
                                a2List = infoList.find_all('div', attrs={'class': 'information_li'})[2].find_all('a')
                            except Exception:
                                a2List = []
                            houseType = set()
                            for a in a2List:
                                houseType.add(a.get_text())
                            try:
                                proAdrr = infoList.find_all('div', attrs={'class': 'information_li'})[3].find('span').get_text()
                            except Exception:
                                proAdrr = ''
                            try:
                                kaiPan = infoList.find_all('div', attrs={'class': 'information_li'})[4].find('a').get_text()
                            except Exception:
                                kaiPan = ''
                            # 封装楼房信息
                            houseInfos['title'] = title
                            houseInfos['score'] = score
                            houseInfos['symbol'] = symbol
                            houseInfos['price'] = price
                            houseInfos['houseType'] = houseType
                            houseInfos['proAdrr'] = proAdrr
                            houseInfos['kaiPan'] = kaiPan
                            print(houseInfos)
                            self.savePage('innerPage ' + str(innerPage) + ' ' + href + ' ' + 'ok')
                            self.printLog('houseData.txt', str(houseInfos))
                        else:
                            self.savePage('innerPage ' + str(innerPage) + ' ' + href + ' ' + 'null')
                self.page += 1
                self.updateUrl()
                # 判断是否最后一页
                if len(houseList) == 0 or len(houseInfos) == 0:
                    self.savePage('page ' + str(self.page) + ' ' + self.nhUrl + ' ' + 'null')
                    self.isEndPage -= 1
                print(houseInfos, ":", len(houseInfos))
                time.sleep(3)
            return houseInfos

        if urlType == 'esfUrl':
            html = self.parseUrl(self.esfUrl, params=params, proxies=proxies)

        if urlType == 'zuUrl':
            html = self.parseUrl(self.zuUrl, params=params, proxies=proxies)

        if urlType == 'cityUrl':
            html = self.parseUrl(self.cityUrl, params=params, proxies=proxies)
            bs = BeautifulSoup(html, 'html.parser')
            # 按省份选择 begin
            provCitys = dict() # 存储结构{id:{prov:[(city,py,bref)]}}
            provTable: Tag = bs.find_all(name='table', attrs={'id': 'senfe'})[0]
            trList: ResultSet = provTable.find_all('tr')
            # 循环获取所有省份信息
            for tr in trList:
                id = tr.get('id', default='')
                prov = tr.find('strong').string if isinstance(tr.find('strong'), Tag) else ''
                citys = list()
                # 如果ID存在则从字典中获取省份信息
                if provCitys.get(id) is not None:
                    # print(tuple(provCitys.get(id).keys())[0])
                    prov = tuple(provCitys.get(id).keys())[0]  # python的keys必须强转为元组才能取出
                    citys = provCitys.get(id)[prov]
                # 循环获取所有城市信息
                for a in tr.find_all('td')[2].find_all('a'):
                    href = a.get('href') # eg.: http://hf.fang.com/
                    city = a.string
                    py = str(href).split('//')[1].split('.')[0] # 城市拼音简称
                    citys.append((city, py, href))
                # 省份装箱
                provCitys[id] = {prov: citys}
                self.printLog('city.log', id + '-' + prov + ':' + str(citys))
            return provCitys

if __name__ == '__main__':
    # url1 = 'https://bj.fang.com/' # 首页
    giveCitys = ['www','xj','kelamayi','kashi','bazhou','yili','akesu','alaer','betl','esf','hami','hetian','kzls','shihezi','tulufan','tmsk','wujiaqu','kuitun','kuerle','ali','changdu','lasa','linzhi','naqu','rikaze','shannan','hk','km','honghe','wenshan','qujing','yuxi','lijiang','dali','chuxiong','baoshan','zhaotong','dehong','lincang','xishuangbanna','puer','diqing','nujiang','anning','ynyl','hz','nb','jx','wz','jh','tz','sx','huzhou','quzhou','ls','zhoushan','changxing','deqing','ruian','yiwu','cixi','yueqing','haining','wenling','zhuji','linhai','yuyao','tongxiang','shangyu','yongkang','pinghu','ninghai','fenghua','jiande','zjtl','zjxs','yuhuan','chunan','zhenhai','haiyan','aj']
    for city in giveCitys:
        ftx = fangtianxia(page=1, innerPage=1, city=city)
        # citys = ftx.getData(urlType='cityUrl')
        # ftx.saveCity(citys)
        try:
            newHouse = ftx.getData('nhUrl')
            print(len(newHouse))
        except Exception as e:
            traceback.print_exc()
            import threading
            # 报错提示歌曲
            threading.Thread(target=ftx.playSound())
            print('请输入y跳过或者其他键暂停：')
            input = input()
            if input == 'y':
                continue
            else:
                break


