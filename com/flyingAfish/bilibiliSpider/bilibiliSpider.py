# coding=utf-8
from typing import List
import requests, re, os
from urllib.request import quote
from lxml import etree
from multiprocessing import Pool
from ffmpy3 import FFmpeg
from prettytable import PrettyTable
from selenium import webdriver
from time import sleep  # 这个后面会用到
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

order = 1
infors = []
table = PrettyTable(['序号', 'up主', '标题', '视频时长', '投稿日期', '播放量', '试看链接'])
path = 'G:\哔哩哔哩视频'
path_ = 'G:\哔哩哔哩视频\m4s文件集'

def _checkPath(path):
    if not os.path.exists(path):
        os.makedirs(path)

def _existFile(filePath):
    return os.path.exists(filePath)

def _getData(content, page):
    global order, infors
    url = 'https://search.bilibili.com/all?keyword=%s&from_source=banner_search&page=%d' % (quote(content), page)
    headers = {
        'Referer': 'https://www.bilibili.com/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'
    }
    html = etree.HTML(requests.get(url, headers=headers).content.decode('utf-8'))
    if page == 1:
        responses = html.xpath('//*[@id="all-list"]/div[1]/div[2]/ul[2]/li')
        if responses == []:
            responses = html.xpath('//*[@id="all-list"]/div[1]/div[2]/ul/li')
    else:
        responses = html.xpath('//*[@id="all-list"]/div[1]/ul/li')
    for response in responses:
        infors.append([str(order),  # 序号
                       response.xpath('./div/div[3]/span[4]/a/text()')[0],  # up主
                       response.xpath('./div/div[1]/a/@title')[0],  # 标题
                       response.xpath('./a/div/span[1]/text()')[0],  # 视频时长
                       response.xpath('./div/div[3]/span[3]/text()')[0]  # 投稿日期
                      .replace('\n', '').replace(' ', ''),
                       response.xpath('./div/div[3]/span[1]/text()')[0]  # 播放量
                      .replace('\n', '')
                      .replace(' ', ''),
                       'https:' + response.xpath('./div/div[1]/a/@href')[0]  # 试看链接
                      .split('?')[0]])
        order += 1  # 序号增加

def _getUrlsForPages(content, pages=1):
    global table, infors
    for page in range(1, pages + 1):
        _getData(content, page)
    for info in infors:
        table.add_row(info)
    print(table)
    print(infors)
    number = input('输入要下载的视频序号（多个视频用.隔开）：').split('.')
    return [infors[int(i) - 1][-1] for i in number]

def download(url, savePath, childPath, fileName):
    """
    下载并保存视频
    :param url: string网页url
    :param savePath: mp4文件保存目录
    :param childPath: m4p文件与mp3文件存放目录
    :param fileName: 视频文件名
    :return:
    """
    global path
    print(url)
    headers = {
        'Referer': url,
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
        'Range': 'bytes=0-'
    }
    hv = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'}
    response: str = requests.get(url, headers=hv).content.decode('utf-8')
    urls1 = re.findall('"baseUrl":"(.+?)"', response)  # 获取m3p视频url
    urls2 = re.findall('"url":"(.+?)"', response)  # 获取flv视频url
    # 下载m3p视频
    if urls1 != []:
        print(fileName + '开始下载!')
        print(urls1[0], "-----", urls1[-1])
        with open(childPath + '\%s.mp4' % (fileName), 'wb')as f:
            f.write(requests.get(urls1[0], headers=headers).content)
        with open(childPath + '\%s.mp3' % (fileName), 'wb')as f:
            f.write(requests.get(urls1[-1], headers=headers).content)
        combineM3pFile(childPath, fileName, savePath)
    # 下载flv视频
    else:
        print(fileName + '开始下载!')
        with open(savePath + '\%s.flv' % (fileName), 'wb')as f:
            f.write(requests.get(urls2[0], headers=headers).content)
        print(fileName + '下载完成!')

def combineM3pFile(childPath, fileName, savePath):
    """
    讲m4p文件与mp3文件合成为一个mp4文件
    :param childPath: m4p文件与mp3文件存放目录
    :param fileName: 视频文件名
    :param savePath: mp4文件存放目录
    :return:
    """
    try:
        ff: FFmpeg = FFmpeg(
            executable="G:\\ProgramFiles\\Python\\ffmpeg\\ffmpeg-20200224-bc9b635-win64-static\\bin\\ffmpeg.exe",
            inputs={childPath + '\%s.mp4' % (fileName): None, childPath + '\%s.mp3' % (fileName): None},
            outputs={
                savePath + '\%s.mp4' % (fileName): '-c:v copy -c:a aac -strict experimental'})  # '-c:v h264 -c:a ac3'
        print(ff, "-------------------------------------")
        ff.run()
    except:
        print(fileName + "音视频合成失败！！失败日志已被屏蔽！！")
    print(fileName + '下载完成!')

def downloadsAll(url, is_delete_m4p=False):
    """
    循环下载所有视频数据
    :param url: 下游网址
    :param is_delete_m4p: 是否删除m4p问价及目录
    :return:
    """
    minPage = 1
    maxPage = 1
    _checkPath(path)
    _checkPath(path_)
    hv = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'}
    html = etree.HTML(requests.get(url, headers=hv).content.decode('utf-8'))
    pageTile = html.xpath('//*[@id="viewbox_report"]/h1/@title')[0]
    print("pageTile:", pageTile)
    # 创建子目录
    childPath = path_ + "\\" + pageTile
    savePath = path + "\\" + pageTile
    _checkPath(childPath)
    _checkPath(savePath)
    multiPage = html.xpath('//*[@id="multi_page"]/div[2]/ul/li')
    # multiPage不为空则说明此链接下有视频选集（即多个子视频）
    if multiPage != []:
        maxPage = len(multiPage)
    print("maxPage:", maxPage)

    print('正在下载：', url)
    # https://www.bilibili.com/video/BV1BJ411U7hW?from=search&seid=532615407602652134
    # urlArr = url.split("?")[0].split('av')
    # aid = urlArr[len(urlArr) - 1]
    aid = url.split('?')[0].split('/')[-1]

    # 解析json获取视频选集名字典{pageNum: title}
    tileList = parseJson(aid)
    for p in range(minPage, maxPage + 1):
        _url = url + '?p=%d' %(p)
        # 如果是单视频则文件名就是父目录名
        if (maxPage == 1):
            fileName = pageTile
        # 否则是多视频，文件名为子目录名
        else:
            print(etree.tostring(multiPage[p - 1]))
            # 这里居然获取不到子视频集的名字，可能是js动态加载出来的，所以这里获取不到（网页源码是有的）
            # fileName = multiPage[p].xpath('./a/@title')[0]
            try:
                fileName = tileList[p-1]['part']
                print(fileName)
            except Exception:
                fileName = str(p)
        # 如果文件存在，则跳过本次下载
        if _existFile(savePath + '\%s.mp4' % (fileName)):
            continue
        if _existFile(childPath + '\%s.mp4' % (fileName)):
            continue
        download(_url, savePath, childPath, fileName)
    if is_delete_m4p:
        removeAll(path_)

def parseJson(aid):
    """
    解析网页返回的json格式数据
    :param aid: 网页id
    :return: list类型数据
    """
    hv = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'}
    # url = 'https://api.bilibili.com/x/player/pagelist?aid=%s&jsonp=jsonp'%(aid)
    url = 'https://api.bilibili.com/x/player/pagelist?bvid=%s&jsonp=jsonp'%(aid)
    jsonStr: str = requests.get(url, headers=hv).content.decode('utf-8')
    import json
    jsonObject: dict = json.loads(jsonStr)
    print(url, '\t', jsonStr)
    return jsonObject['data']

def removeAll(path):
    """
    递归地删除path文件或者文件夹下所有目录和文件包括path本身
    :param path: string路径
    :return:
    """
    if os.path.exists(path):
        if os.path.isfile(path):
            os.remove(path)
        else:
            dirs = os.listdir(path)
            if len(dirs) == 0:
                os.removedirs(path)
            for dir in dirs:
                innerPath = path + '\\' + dir
                print('正在删除：' + innerPath)
                removeAll(innerPath)

def start(content, pages, is_delete_m4p):
    urls = _getUrlsForPages(content, pages=pages)  # 获取待下载URL集
    pool = Pool(processes=4)  # 设置处理器个数
    pool.map(downloadsAll, urls)
    pool.close()
    if is_delete_m4p:
        removeAll(path_)

def driverSpader():
    # 创建Firefox驱动, 也可以按注释方法使用 headless 模式
    options = webdriver.firefox.options.Options()
    options.add_argument('-headless')
    driver = webdriver.Firefox(firefox_options=options,
                               executable_path="G:\ProgramFiles\Program Files\Mozilla Firefox\geckodriver.exe")  # 会打开firefox浏览器窗口, 也可以使用headless模式
    url = 'https://www.bilibili.com/video/av75859780'
    driver.get(url)
    print('cookies:', driver.get_cookies())
    print('name:', driver.name)
    print('title:', driver.title)
    print('mobile:', driver.mobile)
    # print('page_source:', driver.page_source)
    elements: List[WebElement] = driver.find_elements(by=By.ID, value='danmukuBox')
    print(len(elements))
    print(elements[0].text)
    print(driver.title)

if __name__ == '__main__':
    content = input('输入内容：')  # 爬取关键字
    pages = 3  # 爬取总页数
    start(content, pages, True)

    # 测试下载程序OK
    # downloadsAll("https://www.bilibili.com/video/av75859780", True)
    # downloadsAll("https://www.bilibili.com/video/av55181893", True)
    # https://www.bilibili.com/video/BV1BJ411U7hW?from=search&seid=532615407602652134
    # 'https://api.bilibili.com/x/player/pagelist?aid=55181893&jsonp=jsonp'
    # https://api.bilibili.com/x/player/pagelist?bvid=BV1BJ411U7hW&jsonp=jsonp
    # driverSpader()
