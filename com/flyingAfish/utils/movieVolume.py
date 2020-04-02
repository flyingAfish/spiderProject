# coding=utf-8
import os, time
from multiprocessing import Pool
from threading import Thread
from moviepy.editor import VideoFileClip, concatenate_videoclips
"""
但实测会出现错误AttributeError: 'NoneType' object has no attribute 'stdout'，
经研究后，似乎是moviepy版本的问题，
最新的版本为1.0.1，
可以于anaconda prompt中下指令pip list查看自己所有已安装的模块版本。
实测要安装moviepy版本1.0.0才可正常使用，
在anaconda prompt使用pip install moviepy==1.0.0指令即可运作上述代码。
"""

def volumeX(fnames,path, x=5, threads=8):
    origin_path = os.getcwd()
    os.chdir(path)
    if isinstance(fnames, str):
        fname = fnames
        print(fname, '    开转换该视频')
        clip = VideoFileClip(fname)
        newclip = clip.volumex(x)
        newclip.write_videofile("new_" + fname, threads=threads)
    elif isinstance(fnames, list):
        for fname in fnames:
            print('转换开始：\n')
            print(fname, '    开转换该视频')
            clip = VideoFileClip(fname)
            newclip = clip.volumex(x)
            newclip.write_videofile("new_" + fname, threads=threads)
    else:
        print(fnames + 'should in (str, list) type')
    os.chdir(origin_path)

def getFnames(path, paraller=False):
    """
    函数功能：在指定路径下，将该文件夹的视频声音调为x倍
    目录下存在以下三种文件：
        new_Ｌ１－Ｄ１－１.mp4    1.转换后的文件
        new_Ｌ１－Ｄ１－２TEMP_MPY_wvf_snd.mp3    2.正在转换的文件
        Ｌ１－Ｄ１－１.mp4    3.原视频文件
    :param path: 需要转换的视频文件夹路径
    :param paraller: 是否允许多线程并行执行
    :return:
    """
    fnames = []
    origin_path = os.getcwd()
    os.chdir(path)
    print(origin_path)
    for fname in os.listdir():
        if str(fname).startswith('new_'):
            print(fname, '    目标视频跳过不转换')
            continue

        # 原视频加new_前缀，并判断是否存在，存在则跳过，否则转换
        isExists = False
        for orgFname in os.listdir():
            if 'new_' + fname == orgFname:
                isExists = True
            if not paraller:
                if 'new_' + fname == orgFname.split('TEMP')[0] + '.mp4':
                    isExists = False
        if isExists:
            print(fname, '    该视频已经转换完成无需再转换')
        else:
            print(fname, '    开转换该视频')
            fnames.append(fname)

    os.chdir(origin_path)
    return fnames, path

def start(path):
    fnames, ipath = getFnames(path=path, paraller=True)  # 获取待转换的视频名字
    pool = Pool(processes=8)  # 设置处理器个数
    pool.map(volumeX(fnames=fnames, path=ipath), fnames)
    pool.close()

def begin(path):
    fnames, ipath = getFnames(path=path, paraller=False)  # 获取待转换的视频名字
    volumeX(fnames, ipath, 5, 8)

def start1(path, threads=1):
    for i in range(threads+1):
        th = Thread(target=begin, name=i, args=(path,))
        th.start()
        th.join()
        print(th.getName(), '\n')
        time.sleep(1)

if __name__ == '__main__':
    path = 'G:\哔哩哔哩视频\华清远见2-linuxC语言高级'
    start1(path, 8)
