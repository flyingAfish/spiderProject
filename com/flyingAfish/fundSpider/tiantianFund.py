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

class zoFund():
    """
    中欧基金管理公司-天天基金网
    """
    def __init__(self):
        self.fundCode = ''
        self.netUrl = 'http://api.fund.eastmoney.com/f10/lsjz?fundCode=%s&pageIndex=1&pageSize=99999'%(self.fundCode)

    def updateUrl(self):
        self.netUrl = 'http://api.fund.eastmoney.com/f10/lsjz?fundCode=%s&pageIndex=1&pageSize=99999'%(self.fundCode)

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
        with open(logPth + '/' + filename, 'at', encoding='utf-8', buffering=4028) as f:
            f.write(_log + '\n')
            f.flush()

    def saveData(self, filename, data):
        dataPath = './data/'
        if not os.path.exists(dataPath):
            os.makedirs(dataPath)
        with open(dataPath + filename, 'at', encoding='utf-8', buffering=4028) as f:
            f.write(data + '\n')
            f.flush()

    def generateHeader(self, sum):
        headersList = []
        for i in range(sum):
            header = {'User-Agent': UserAgent().random}
            headersList.append(header)
        return headersList

    def parseUrl(self, url, params=None, proxies=None, headers=None):
        if headers is None:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'}
        response: Response = requests.get(url, params=params, proxies=proxies, headers=headers)
        response.raise_for_status()
        response.encoding = 'utf-8'
        return response.text

    def saveExcel(self, range, data, bookName, sheetName=0):
        """"
        """
        excelPath = './data/excelData/'
        if not os.path.exists(excelPath):
            os.makedirs(excelPath)
        app = xlwings.App(visible=True, add_book=False)
        wb = app.books.add()
        wb.name = bookName
        sheet = wb.sheets.add(sheetName)
        sheet.range(range).value = data
        wb.save(excelPath + bookName +'.xlsx')
        wb.close()
        app.quit()

    def getData(self, url):
        html = self.parseUrl(url)
        bs = BeautifulSoup(html, 'html.parser')
        trList = bs.select('div[id="kfsFundNetWrap"] > table > tbody > tr')
        headersList = self.generateHeader(len(trList))
        print('tr：', len(trList))
        for tr in trList:
            dataDict = {}
            randHeaders = headersList[random.randint(0, len(trList) - 1)]
            href = tr.select('td > a')[0]['href'] if len(tr.select('td > a')) > 0 else self.printLog(dataDict['基金名称'], 'no href')
            dataDict['href'] = href
            dataDict['基金名称'] = tr.select('td > a')[0]['title'] if len(tr.select('td > a')) > 0 else self.printLog(dataDict['基金名称'], 'no 基金名称')
            dataDict['基金代号'] = tr.select('td > a')[1].get_text() if len(tr.select('td > a')) > 1 else self.printLog(dataDict['基金名称'], 'no 基金代号')

            try:
                innerHtml = self.parseUrl(href, headers=randHeaders)
            except Exception as e:
                self.printLog(dataDict['基金名称'], 'parse href erro:' + href)
                continue
            innerBs = BeautifulSoup(innerHtml, 'html.parser')
            wrappers = innerBs.find_all('div', attrs={"class": "wrapper"})
            # 获取 基础 信息
            if len(wrappers) >= 9:
                innerTrs = wrappers[8].select("div[class='infoOfFund'] table > tr")
                print(innerTrs)
                aList = innerTrs[0].find_all('td') if len(innerTrs) > 0 else []
                tdList = innerTrs[1].find_all('td') if len(innerTrs) > 0 else []
                dataDict['基金类型'] = aList[0].get_text() if len(aList) > 0 else self.printLog(dataDict['基金名称'], 'no fundType')
                dataDict['基金规模'] = aList[1].get_text() if len(aList) > 1 else self.printLog(dataDict['基金名称'], 'no fundScale')
                dataDict['基金经理'] = aList[2].get_text() if len(aList) > 2 else self.printLog(dataDict['基金名称'], 'no fundManager')
                dataDict['成立日期'] = tdList[0].get_text() if len(tdList) > 0 else self.printLog(dataDict['基金名称'], 'no estbDate')
                dataDict['管理公司'] = tdList[1].get_text() if len(tdList) > 1 else self.printLog(dataDict['基金名称'], 'no company')
                jjpj1 = tdList[2].get_text() if len(tdList) > 2 else self.printLog(dataDict['基金名称'], 'no fundScore')
                jjpj2 = tdList[2].find('div')['class'] if(tdList[2].find('div') if len(tdList) > 2 else None) is not None else ''
                dataDict['基金评级'] = jjpj1 if jjpj1 is not None else '' + jjpj2 if isinstance(jjpj2, str) else ''
                print('dataDict', dataDict)

            self.saveData("基金基础数据.txt", str(dataDict))

            # 获取 净值 数据
            self.fundCode = dataDict['基金代号']
            self.updateUrl()
            try:
                randHeaders['Referer'] = url
                print(self.netUrl)
                jsonData = self.parseUrl(self.netUrl, headers=randHeaders)
                jsonObj = json.loads(jsonData)
                netVDatas = jsonObj['Data']['LSJZList']
                svData = dataDict['基金代号'] + '￥#￥' + str(netVDatas)
                self.saveData("基金净值数据.txt", svData)
                # self.saveExcel('A1', list(dataDict.keys()), '基金基础数据')
                # self.saveExcel('A2', list(dataDict.values()), '基金基础数据')
            except Exception as e:
                print('parse netUrl erro:', self.netUrl)
                continue
            print(jsonData)
        # time.sleep(1)
        return dataDict, netVDatas


if __name__ == '__main__':
    url = 'http://fund.eastmoney.com/company/80065113.html'
    zof = zoFund()
    data = zof.getData(url)
