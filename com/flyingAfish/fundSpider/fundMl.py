import numpy as np
import pandas as ps
import os
import json
from matplotlib.pyplot import plot

with open('./data/基金净值数据.txt', 'rt', encoding='utf-8') as f:
    for line in f.readlines():
        datas = line.split('￥#￥')
        if datas[0] != '003096':
            continue
        dt = datas[1].replace("'", '"').replace('None', '"None"')
        print(dt)
        jsonOb = json.loads(dt)
        dimArr = []
        for data in jsonOb:
            print(data)
            innerArr = []
            for value in data.values():
                innerArr.append(value)
            dimArr.append(innerArr)
        print(dimArr)
        print()
        df = ps.DataFrame(dimArr, columns=['净值日期', '单位净值', '累计净值',
                                           'SDATE', 'ACTUALSYI', 'NAVTYPE',
                                           '日增长率', '申购状态', '赎回状态',
                                           'FHFCZ', 'FHFCBZ', 'DTYPE', 'FHSP'])
        print(df)
        print(df['单位净值'])



