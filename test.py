import xlrd
import xlwt
import datetime
import matplotlib.pyplot as plt
import matplotlib.image as img
from locate import distance_to_BS, locate_by_pointlist,distance
import sys
import pandas as pd
import csv
import pprint
import math
import random
import sympy

gateway = [[], [22, 6.41], [22.62, 22.59], [41, 17.4], [31.875, 2.29], [8.35, 22.59],[6.15,3.31]]
checkpoint =[[],[39.145,17.124],[39.145,11.6],[34.112,6.905],[26.5625,3.867],[18.174,3.867],
             [6.151,3.314],[19.572,8.838],[30.757,8.838],[8.388,14.362],[8.947,19.886],[15.658,20.162],
             [24.326,20.162],[34.671,20.162],[35.789,25.133],[29.918,25.133]]
restriction=[8.862,32.1915,9.729,18.523]#left,right,bottom,top
time_window = 1  # min

raw_gd=[["2020/3/28 16:05",1],
    ["2020/3/28 16:39",6],
    ["2020/3/28 16:44",11],
    ["2020/3/28 16:49",10],
    ["2020/3/28 17:10",12],
    ["2020/3/28 17:18",12],
    ["2020/3/28 17:27",1],
    ["2020/4/7 10:55",1],
    ["2020/4/7 11:03",2],
    ["2020/4/7 11:09",3],
    ["2020/4/7 11:15",4],
    ["2020/4/7 11:22",5],
    ["2020/4/7 11:35",6],
    ["2020/4/7 11:44",7],
    ["2020/4/7 11:50",8],
    ["2020/4/7 11:56",9],
    ["2020/4/7 12:03",10],
    ["2020/4/7 12:14",11],
    ["2020/4/7 12:23",12],
    ["2020/4/7 12:29",13]]
gd={}

def newDis(p1,p2):
    return abs(p1[0]-p2[0])+abs(p1[1]-p2[1])
def lsm(logs):
    data=[]
    print(gd)
    for key in logs.keys():
        for sample in logs[key]:
            if sample[2] in gd.keys():
                gdp=gd[sample[2]]
                x=gateway[sample[1]][0]
                y=gateway[sample[1]][1]
                dis=math.log10(distance(gdp,[x,y]))
                tmp=[dis,abs(sample[0])]

                if not(tmp in data):
                    data.append(tmp) #distance,rssi
    data=eliminate_duplicates(data)
    sum_xy=0
    avg_x=0
    avg_y=0
    sum_xx=0
    num=0
    x=[]
    y=[]
    for d in data:
        x.append(d[1])
        y.append(d[0])
        sum_xy=sum_xy+d[0]*d[1]
        avg_x=avg_x+d[1]
        avg_y=avg_y+d[0]
        sum_xx=sum_xx+d[1]*d[1]
        num+=1
    avg_x=avg_x/num
    avg_y=avg_y/num
    b=(sum_xy-num*avg_x*avg_y)/(sum_xx-num*avg_x*avg_x)
    aa=avg_y-b*avg_x
    n=1/(10*b)
    a=aa/(-b)
    print("n:",n)
    print("a:",a)
    return 47.57802543307896,2.9505452333148887
    return a,n

def plot_img(output):
    truthX = []
    truthY = []
    myX = []
    myY = []

    for i in output:
        if i[2] in gd:
            x=gd[i[2]][0]
            y=gd[i[2]][1]
            truthX.append(x)
            truthY.append(y)
        myX.append(i[0])
        myY.append(i[1])
    print(truthX)
    print(truthY)
    ax = plt.axes(xlim=(0, 42.5), ylim=(0, 29))
    imgP = plt.imread('./data/bkg data/map.png')
    ax.imshow(imgP, zorder=0, extent=[0, 42.5, 0.0, 29])  # 背景图片
    ax.scatter(truthX,truthY, marker='+', s=150, c='r')
    ax.scatter(myX, myY,marker='*', s=15, c='b')
    plt.plot([8.862,8.862],[9.729,18.523])
    plt.plot([32.1915,32.1915], [9.729, 18.523])
    plt.plot([8.862, 32.1915], [18.523,18.523])
    plt.plot([8.862, 32.1915], [9.729, 9.729])
    plt.show()

def calculate_error(output):
    ret=0
    count=0
    pred=[]
    print("\n\n*******************************************")
    for i in output:
        if i[2] in gd:
            x=gd[i[2]][0]
            y=gd[i[2]][1]
            ret=ret+((i[0]-x)**2+(i[1]-y)**2)**0.5
            count=count+1
            pred.append(i)
            print(i[2],",",((i[0]-x)**2+(i[1]-y)**2)**0.5)
    print("*******************************************\n\n")
    print("Error is:",ret/count)
    return pred

def read_data(file_path_list):
    for i in raw_gd:
        date = datetime.datetime.strptime(i[0],'%Y/%m/%d %H:%M')
        gd[date]=[checkpoint[i[1]][0],checkpoint[i[1]][1]]
    print("gd",gd)
    devicelogs = {}
    for file_path in file_path_list:
        pointIndex=file_path.rfind('.')
        if file_path[pointIndex+1:]=="csv":
            with open(file_path) as f:
                reader = list(csv.reader(f))
                log_list = []
                for i in range(1,len(reader)):
                    temp=[]
                    temp.append(float(reader[i][3]))
                    temp.append(int(reader[i][6]))
                    datetime_obj=datetime.datetime.strptime(reader[i][9],'%Y/%m/%d %H:%M')
                    temp.append(datetime_obj)
                    log_list.append(temp)
            devicelogs[file_path[file_path.rfind('/')+1:pointIndex]]=log_list
        else:
            wb = xlrd.open_workbook(file_path)
            sheet_list = wb.sheet_names()
            print(sheet_list)
            for i in range(len(sheet_list)):
                sheet = wb.sheet_by_name(sheet_list[i])
                nrows = sheet.nrows
                log_list = []
                for j in range(1,nrows):
                    temp = []
                    rssi=float(sheet.cell(j, 3).value)
                    if rssi>85:# or rssi<60:
                        continue
                    temp.append(rssi)
                    temp.append(int(sheet.cell(j, 6).value))
                    datetime_obj=xlrd.xldate.xldate_as_datetime(sheet.cell(j,9).value,0)
                    #print(datetime_obj.second)
                    datetime_obj=datetime_obj - datetime.timedelta(seconds=datetime_obj.second)
                    temp.append(datetime_obj)
                    log_list.append(temp)
                devicelogs[sheet_list[i]] = log_list
    print(devicelogs)
    a,n=lsm(devicelogs)
    return devicelogs,a,n  # {'device_name' = [[rssi, gateway_id, datetime],...]}


def process_data(raw_list: list,a,n): # [[rssi, gateway_id, datetime],...]
    now_date = raw_list[0][2]
    print(now_date)
    result = {}
    temp = []
    #sum=0
    for x in raw_list:
        # 按分钟计时，根据time_window分割数据
        if (x[2] - now_date).seconds < time_window*60:
            t = [x[1],x[0]]
            if t not in temp:#这里要不要去掉？
                temp.append(t)
        else:
            # 消除重复网关
            #sum=sum+len(temp)
            temp = eliminate_duplicates(temp)
            # 转化格式
            for i in range(len(temp)):
                temp[i] = [gateway[temp[i][0]][0],gateway[temp[i][0]][1], distance_to_BS(temp[i][1],a,n)]
            
            result[now_date] = temp
            temp = [[x[1], x[0]]]
            now_date=x[2]
    temp = eliminate_duplicates(temp)
    # 转化格式
    for i in range(len(temp)):
        temp[i] = [gateway[temp[i][0]][0], gateway[temp[i][0]][1], distance_to_BS(temp[i][1],a,n)]
    result[now_date] = temp
    return result  # {datetime:[[gateway_x, gateway_y, distance],...]}


def eliminate_duplicates(temp_l):
    count = {}
    result = []
    for x in temp_l:
        if x[0] not in count:
            count[x[0]] = [x[1]]
        else:
            count[x[0]].append(x[1])
    print(count)
    for key, value in count.items():
        result.append([key, sum(value)/len(value)])  # 消除重复的策略可改，这里定的是均值
    print(result)
    return result

#def plot_image():
    datList = []
#    datMat = mat(datList)

def checkValid(output):
    for point in output:
        x=point[0]
        y=point[1]
        if x>=restriction[0] and x<=restriction[1] and y>=restriction[2] and y<=restriction[3]:
            tmp=[]
            tmp.append(abs(restriction[0]-x))
            tmp.append(abs(restriction[1]-x))
            tmp.append(abs(restriction[2]-y))
            tmp.append(abs(restriction[3]-y))
            ind=tmp.index(min(tmp))
            if ind<=1:
                point[0]=restriction[ind]
            else:
                point[1]=restriction[ind]

if __name__ == "__main__":
    path=['./data/bkg data/03-28-Abeacon3.csv','./data/bkg data/03-28-mi.csv','./data/bkg data/04-07-Abeacon3.xlsx']
    result_path = './result/result4.xlsx'
    raw_data,a,n = read_data(path)
    wb = xlwt.Workbook(encoding='utf-8')
    style = xlwt.XFStyle()
    style.num_format_str = 'M/D/YY h:mm'
    output = []
    for key in raw_data.keys():
        sheet = wb.add_sheet(key)
        i = 0
        print(raw_data[key])
        data = process_data(raw_data[key],a,n)
        pprint.pprint(data)

        for key, value in data.items():
            locate = locate_by_pointlist(value)
            if locate[0] == 0 or locate[1] == 0:
                continue
            output.append([locate[0],locate[1],key])
            sheet.write(i,0,float(locate[0]))
            sheet.write(i,1,float(locate[1]))
            sheet.write(i,2,key,style)
            i += 1
    print(len(output))
    checkValid(output)
    pred=calculate_error(output)
    plot_img(output)
    print(pred)
    wb.save(result_path)
