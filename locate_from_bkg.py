from math import sqrt, cos, sin, pi
import pandas as pd
import sympy
import numpy as np
import itertools
import sys

RSSI_threshold = 90

cor_gateway = [[0, 0], [22, 6.41], [22.62, 22.59], [41, 17.4], [31.875, 2.29], [8.35, 22.59],[6.15,3,37]]#网关坐标
center_x,center_y=20,15#中心坐标
angle_center=[0,1.5*pi,0.5*pi,0,1.75*pi,0.75*pi,1.25*pi]#中心与网关连线角度，270，90，0，315，135，225
cor_point = [[0, 0], [39.14, 17.12], [39.14, 11.6], [34.11, 6.9], [26.56, 3.87], [18.17, 3.87], [6.15, 3.31],
             [19.57, 8.83], [30.76, 8.83], [8.39, 14.36], [8.95, 19.88], [15.66, 20.16], [24.33, 20.16], [34.67, 20.16],
             [35.79, 25.13], [29.92, 25.13]]#测量点坐标
angle_gateway = [0, 1.5*pi, 0.5*pi, 1.25 * pi, 0.75 * pi, 1.75*pi,0.25 * pi]#单网关定位时的角度，270，90，225，135，315，45

def time2point(y):  # y时间，a=1表示ABeacon3，a=2表示小米手环
    if '10:55'<=y<"11:03":
        return 1
    if '11:03'<=y<"11:09":
        return 2
    if '11:09'<=y<'11:15':
        return 3
    if '11:15'<=y<'11:22':
        return 4
    if '11:22'<=y<'11:35':
        return 5
    if '11:35'<=y<'11:44':
        return 6
    if '11:44'<=y<'11:50':
        return 7
    if '11:50'<=y<'11:56':
        return 8
    if '11:56'<=y<'12:03':
        return 9
    if '12:03'<=y<'12:14':
        return 10
    if '12:14'<=y<'12:23':
        return 11
    if '12:23'<=y<'12:29':
        return 12
    if '12:29'<=y<'12:35':
        return 13
    if '12:35'<=y<'13:03':
        return 1
    return 0

def dataprocess(mypd):
    data1 = {'time': [], 'point': [], 'rssi1': [], 'rssi2': [], 'rssi3': [], 'rssi4': [], 'rssi5': [],'rssi6':[]}
    data2 = {'time': [], 'point': [], 'cnt1': [], 'cnt2': [], 'cnt3': [], 'cnt4': [], 'cnt5': [],'cnt6':[]}#记录每个网关每分钟连接次数
    temp = pd.DataFrame(data1)
    cnt = pd.DataFrame(data2)
    X, Y = mypd.shape
    row = 0#行数
    for i in range(X):
        s = mypd.loc[i, 'createdAt'].split()[1]#时间（分钟）
        p = time2point(s)#测量点编号
        q = mypd.loc[i, 'rssi']#rssi强度
        r = mypd.loc[i, 'gatewayId']#网关编号
        if p == 0:
            continue
        h = temp['time']
        if h.empty or h[h.values == s].index.empty:#该分钟未创立条目，新建一行
            df1 = pd.DataFrame(
                {'time': [s], 'point': [p], 'rssi1': [0], 'rssi2': [0], 'rssi3': [0], 'rssi4': [0], 'rssi5': [0],'rssi6':[0]})
            df2 = pd.DataFrame(
                {'time': [s], 'point': [p], 'cnt1': [0], 'cnt2': [0], 'cnt3': [0], 'cnt4': [0], 'cnt5': [0],'cnt6':[0]})
            temp = temp.append(df1, ignore_index=True)
            cnt = cnt.append(df2, ignore_index=True)
            row = row + 1
        temp.loc[row - 1, 'rssi' + str(r)] += q
        cnt.loc[row - 1, 'cnt' + str(r)] += 1
    A, B = temp.shape
    for i in range(A):#求每分钟网关强度的平均
        for j in range(6):
            if cnt.loc[i, 'cnt' + str(j + 1)] != 0:
                temp.loc[i, 'rssi' + str(j + 1)] = temp.loc[i, 'rssi' + str(j + 1)] / cnt.loc[i, 'cnt' + str(j + 1)]
    return temp

def distance_to_BS(rssi, a=45, n=4):
    """
    根据RSSI计算距离
    :param rssi:
    :param a: 距离发射器1m时的RSSI值，单位:-dbm，默认为42
    :param n: 衰减系数，默认为3.3
    :return:
    """
    return 10 ** ((abs(rssi) - a) / (10 * n)) if abs(rssi) < RSSI_threshold else None

def distance(p1, p2):
    return sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


def mycount(mypd):#返回有连接的信标编号
    result = []
    for i in range(6):
        if 0.1 <= mypd['rssi' + str(i + 1)] <= RSSI_threshold - 0.1:
            result.append(i + 1)
    return result

def in_wall(x,y):#是否在墙内
    return (9<=x<=33 and 9<=y<=20)

def locate(mypd):
    c = mycount(mypd)
    mylen = len(c)
    x, y = 0, 0
    if mylen == 0:
        return [0, 0] #srb:感觉还不如返回None,这个[0,0]在画轨迹的时候肯定是过滤掉比较好
    mymax = c[0]
    if mylen == 1:#只有一个网关有信号
        x = cor_gateway[c[0]][0] + cos(angle_gateway[c[0]]) * distance_to_BS(mypd['rssi' + str(c[0])])
        y = cor_gateway[c[0]][1] + sin(angle_gateway[c[0]]) * distance_to_BS(mypd['rssi' + str(c[0])])
    if mylen >= 2:#有两个以上网关有信号
        for i in c:#求信号最强的网关
            if mypd['rssi' + str(i)] < mypd['rssi' + str(mymax)]:
                mymax = i
        d1 = distance_to_BS(mypd['rssi' + str(mymax)])
        for i in c:
            if i == mymax:
                continue
            d2 = distance_to_BS(mypd['rssi' + str(i)])
            x += cor_gateway[mymax][0] * d2 / (d1 + d2) + cor_gateway[i][0] * d1 / (d1 + d2)
            y += cor_gateway[mymax][1] * d2 / (d1 + d2) + cor_gateway[i][1] * d1 / (d1 + d2)
        x = x / (mylen - 1)
        y = y / (mylen - 1)
    if in_wall(x,y):#推出墙外
        d=distance([center_x,center_y],[cor_gateway[mymax][0],cor_gateway[mymax][1]])
        i=1
        while i<d:
            if not in_wall(center_x+i*cos(angle_center[mymax]),center_y+i*sin(angle_center[mymax])):
                break
            i=i+1
        x=center_x+i*cos(angle_center[mymax])
        y=center_y+i*sin(angle_center[mymax])
    return [x,y]

def cal_error(x):
    return distance([x['real_x'], x['real_y']], [x['calculated_x'], x['calculated_y']])


if __name__ == "__main__":
    #x = pd.read_csv(open('D:\\边凯归\\蓝牙定位\\数据\\第四组\\test2.csv'))
    #data_xls = pd.read_excel('./data/bkg data/04-07-Abeacon3.xlsx')
    #data_xls.to_csv('./data/bkg data/04-07-Abeacon3.csv', encoding='utf-8')
    #sys.exit(0)
    x = pd.read_csv(open('data/bkg data/04-07-Abeacon3.csv'))
    result = dataprocess(x)
    x1, y1, x2, y2 = [], [], [], []
    X, Y = result.shape
    for i in range(X):
        p = result.loc[i, 'point']
        x1.append(cor_point[int(p)][0])
        y1.append(cor_point[int(p)][1])
        a = locate(result.loc[i, :])
        x2.append(a[0])
        y2.append(a[1])
    df = pd.DataFrame({'real_x': x1, 'real_y': y1, 'calculated_x': x2, 'calculated_y': y2})
    result = pd.concat([result, df], axis=1)
    result.loc[:, 'error'] = result.apply(cal_error, axis=1)
    print(result)
    #result.to_csv('D:\\边凯归\\蓝牙定位\\数据\\第四组\\result1.csv')
