number = input('输入要下载的视频序号：').split('.')
print(number)
print(type(number))
print([infors[int(i) - 1][-1] for i in number])
# 2.3.4.5.6.7.8.9.10.11.12.13.14.15.16.17
# 低调学习的人华清远见