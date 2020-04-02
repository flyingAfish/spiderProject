# -*- coding=utf-8 -*-
import traceback
import requests
from requests import Response
import random
import datetime
import json
import time
import xlwings
import os, re
import pandas as pd
import numpy as np
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

    def isExists(self, filepath, fundname, code, index_='1'):
        if os.path.exists('./data\\' + filepath + 'netValue.xlsx'):
            print(index_, '跳过下载：\t', fundname, code, '文件已经存在跳过下载...')
            index_ += 1
            return True
        else:
            return False

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

    def saveData(self, path, filename, data):
        dataPath = './data/' + path
        if not os.path.exists(dataPath):
            os.makedirs(dataPath)
        with open(dataPath + filename, 'at', encoding='utf-8', buffering=4028) as f:
            f.write(data + '\n')
            f.flush()

    def saveExcel(self, dfData, path='', filename='funddata.xlsx'):
        dataPath = './data/' + path
        if not os.path.exists(dataPath):
            os.makedirs(dataPath)
        if not dataPath.endswith(('/', '\\')):
            dataPath += '\\\\'
        if not filename.endswith('.xlsx'):
            filename += '.xlsx'
        with pd.ExcelWriter(dataPath + filename,
                            date_format='YYYY-MM-DD',
                            datetime_format='YYYY-MM-DD HH:MM:SS') as writer:
            dfData.to_excel(writer)

    def getBasicData(self, url):
        html = self.parseUrl(url)
        bs = BeautifulSoup(html, 'html.parser')
        trList = bs.select('div[id="kfsFundNetWrap"] > table > tbody > tr')
        headersList = self.generateHeader(len(trList))
        print('tr：', len(trList))

        baseDatas = []
        for tr in trList:
            dataDict = {}
            randHeaders = headersList[random.randint(0, len(trList) - 1)]
            href = tr.select('td > a')[0]['href'] if len(tr.select('td > a')) > 0 else self.printLog(dataDict['基金名称'],
                                                                                                     'no href')
            dataDict['href'] = href
            dataDict['基金名称'] = tr.select('td > a')[0]['title'] if len(tr.select('td > a')) > 0 else self.printLog(
                dataDict['基金名称'], 'no 基金名称')
            dataDict['基金代号'] = tr.select('td > a')[1].get_text() if len(tr.select('td > a')) > 1 else self.printLog(
                dataDict['基金名称'], 'no 基金代号')

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
                dataDict['基金类型'] = aList[0].get_text() if len(aList) > 0 else self.printLog(dataDict['基金名称'],
                                                                                            'no fundType')
                dataDict['基金规模'] = aList[1].get_text() if len(aList) > 1 else self.printLog(dataDict['基金名称'],
                                                                                            'no fundScale')
                dataDict['基金经理'] = aList[2].get_text() if len(aList) > 2 else self.printLog(dataDict['基金名称'],
                                                                                            'no fundManager')
                dataDict['成立日期'] = tdList[0].get_text() if len(tdList) > 0 else self.printLog(dataDict['基金名称'],
                                                                                              'no estbDate')
                dataDict['管理公司'] = tdList[1].get_text() if len(tdList) > 1 else self.printLog(dataDict['基金名称'],
                                                                                              'no company')
                jjpj1 = tdList[2].get_text() if len(tdList) > 2 else self.printLog(dataDict['基金名称'], 'no fundScore')
                jjpj2 = tdList[2].find('div')['class'] if (tdList[2].find('div') if len(
                    tdList) > 2 else None) is not None else ''
                dataDict['基金评级'] = jjpj1 if jjpj1 is not None else '' + jjpj2 if isinstance(jjpj2, str) else ''
                print('dataDict', dataDict)
                baseDatas.append(dataDict)

            # self.saveData("基金基础数据.txt", str(dataDict))
        return baseDatas

    def getNetValue(self, code, per=10, sdate='', edate='', proxies=None):
        url = 'http://fund.eastmoney.com/f10/F10DataApi.aspx'
        params = {'type': 'lsjz', 'code': code, 'page': 1, 'per': per, 'sdate': sdate, 'edate': edate}
        headers = self.generateHeader(1)[0]
        html = self.parseUrl(url, params, proxies, headers)
        soup = BeautifulSoup(html, 'html.parser')
        print(html)

        # 获取总页数
        pattern = re.compile(r'pages:(.*),')
        result = re.search(pattern, html).group(1)
        pages = int(result)

        # 获取表头
        heads = []
        for head in soup.findAll("th"):
            heads.append(head.contents[0])
        # 数据存取列表
        records = []
        # 从第1页开始抓取所有页面数据
        page = 1
        while page <= pages:
            params = {'type': 'lsjz', 'code': code, 'page': page, 'per': per, 'sdate': sdate, 'edate': edate}
            html = self.parseUrl(url, params, proxies, headers)
            soup = BeautifulSoup(html, 'html.parser')

            # 获取数据
            for row in soup.findAll("tbody")[0].findAll("tr"):
                row_records = []
                for record in row.findAll('td'):
                    val = record.contents
                    # 处理空值
                    if val == []:
                        row_records.append(np.nan)
                    else:
                        row_records.append(val[0])
                # 记录数据
                records.append(row_records)
            # 下一页
            page = page + 1

        # 数据整理到 dataframe
        np_records = np.array(records)
        data = pd.DataFrame()
        for col, col_name in enumerate(heads):
            data[col_name] = np_records[:, col]
        return data

    def dealFundData(self, url):
        bDatas = self.getBasicData(url)

        index = 1
        for bData in bDatas:
            code = bData.get('基金代号')
            company = bData.get('管理公司') if bData.get('管理公司') else 'notcompany'
            fundname = bData.get('基金名称') if bData.get('基金名称') else 'defaultfundname' + index
            if not (code and company and fundname):
                print(index, '错误：\t', code, company, fundname, '有空错误！！！')
            filepath = company + '\\' + fundname + '\\'

            if self.isExists(filepath, fundname, code, index):
                index += 1
                continue

            print(index, '正在下载：', fundname, code + '...')
            netValue = self.getNetValue(code)
            print(index, '正在保存：', fundname, code + '...')
            self.saveData(path=filepath, filename='basicData', data=str(bData))
            self.saveExcel(path=filepath, filename='netValue.xlsx', dfData=netValue)
            time.sleep(1)
            index += 1

if __name__ == '__main__':
    url = 'http://fund.eastmoney.com/company/80065113.html'
    zof = zoFund()
    zof.dealFundData(url)












    #
    # def getData(self, url):
    #
    #
    #         # 获取 净值 数据
    #         self.fundCode = dataDict['基金代号']
    #         self.updateUrl()
    #         try:
    #             randHeaders['Referer'] = url
    #             print(self.netUrl)
    #             jsonData = self.parseUrl(self.netUrl, headers=randHeaders)
    #             jsonObj = json.loads(jsonData)
    #             netVDatas = jsonObj['Data']['LSJZList']
    #             svData = dataDict['基金代号'] + '￥#￥' + str(netVDatas)
    #             self.saveData("基金净值数据.txt", svData)
    #         except Exception as e:
    #             print('parse netUrl erro:', self.netUrl)
    #             continue
    #         print(jsonData)
    #     # time.sleep(1)
    #     return dataDict, netVDatas