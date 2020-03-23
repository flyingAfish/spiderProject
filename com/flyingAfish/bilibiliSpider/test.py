# coding=utf-8
import requests, re, os
from urllib.request import quote
from lxml import etree
from multiprocessing import Pool
from ffmpy3 import FFmpeg
from bs4 import BeautifulSoup
from prettytable import PrettyTable
# input1 = {"D:\av75859780.mp4":None,"D:\av75859780.mp3":None}
# input2 = {"D:\哔哩哔哩视频\m4s文件集\尚硅谷大数据全套视频教程40阶段（2019.6月线下班）\\10.mp4": None,
#             "D:\哔哩哔哩视频\m4s文件集\尚硅谷大数据全套视频教程40阶段（2019.6月线下班）\\10.mp3": None}
# output1 = {"D:\av75859780out.mp4":'-c:v h264 -c:a ac3'}
# output2 = {"D:\哔哩哔哩视频\尚硅谷大数据全套视频教程40阶段（2019.6月线下班）\\10.mp4": '-c:v copy -c:a aac -strict experimental'}
# ff: FFmpeg = FFmpeg(
#     executable="D:\\Python\\ffmpeg\\ffmpeg-20200224-bc9b635-win64-static\\bin\\ffmpeg.exe",
#     inputs=input2,
#     outputs=output2)  # '-c:v h264 -c:a ac3'
# print(ff, "-------------------------------------")
# ff.run()

# soup = BeautifulSoup('<b class="boldest">Extremely bold</b>',features='html.parser')
# tag = soup.b
# print(tag.name)
# print(type(tag))
# print(type(soup))
# tag['class'] = 'verybold'
# tag['id'] = 1
# print(tag)
# print(tag.attrs)
# <class 'bs4.element.Tag'>
# <class 'bs4.BeautifulSoup'>
# id = 75859780
hv = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'}
# url = 'https://api.bilibili.com/x/player/pagelist?aid=%s&jsonp=jsonp' %(id)
# jsonStr: str = requests.get(url, headers=hv).content.decode('utf-8')
# import json
# jsonObject: dict = json.loads(jsonStr)
# print(len(jsonObject['data']))
# print(type((jsonObject['data'][0]['page'], jsonObject['data'][0]['part'])))
# print(jsonObject['data'][0]['part'])

# url = "https://www.bilibili.com/video/av75859780"
# gg = url.split("?")[0].split('av')
# print(gg[len(gg) - 1]
#       )

def parseJson(aid):
    hv = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'}
    url = 'https://api.bilibili.com/x/player/pagelist?aid=%s&jsonp=jsonp'%(aid)
    jsonStr: str = requests.get(url, headers=hv).content.decode('utf-8')
    import json
    jsonObject: dict = json.loads(jsonStr)
    print(jsonObject['data'])
    jsonObject['data']

print(parseJson('75859780'))