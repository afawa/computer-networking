import xlrd
import xlwt
import datetime
import matplotlib.pyplot as plt
from locate import distance_to_BS, locate_by_pointlist,distance
import sys
import pandas as pd
import csv
import pprint
import math

gateway = [[], [22, 6.41], [22.62, 22.59], [41, 17.4], [31.875, 2.29], [8.35, 22.59]]
checkpoint =[[],[39.145,17.124],[],[],[],[],[6.151,3.314],[],[],[],[8.947,19.886],[15.658,20.162],[24.326,20.162]]
time_window = 1  # min
raw_gd=[["2020/3/28 16:05",1],
    ["2020/3/28 16:39",6],
    ["2020/3/28 16:44",11],
    ["2020/3/28 16:49",10],
    ["2020/3/28 17:10",12],
    ["2020/3/28 17:18",12],
    ["2020/3/28 17:27",1]]
gd={}

def lsm(logs):
    data=[]
    print(gd)
    for key in logs.keys():
        for sample in logs[key]:
            if sample[2] in gd.keys():
                gdp=gd[sample[2]]
                x=gateway[sample[1]][0]
                y=gateway[sample[1]][1]
                tmp=[math.log10(distance(gdp,[x,y])),abs(sample[0])]
                if not(tmp in data):
                    data.append(tmp) #distance,rssi
    pprint.pprint(data)
    data=eliminate_duplicates(data)
    sum_xy=0
    avg_x=0
    avg_y=0
    sum_xx=0
    num=len(data)
    x=[]
    y=[]
    for d in data:
        if d[1]>=90:#threshold
            continue
        x.append(d[1])
        y.append(d[0])
        sum_xy=sum_xy+d[0]*d[1]
        avg_x=avg_x+d[1]
        avg_y=avg_y+d[0]
        sum_xx=sum_xx+d[1]*d[1]
    avg_x=avg_x/num
    avg_y=avg_y/num
    b=(sum_xy-num*avg_x*avg_y)/(sum_xx-num*avg_x*avg_x)
    aa=avg_y-b*avg_x
    n=1/(10*b)
    a=aa/(-b)
    pprint.pprint(data)
    print(n)
    print(a)
    for d in data:
        print(d[1],10**d[0],distance_to_BS(d[1],a,n))
    plt.scatter(x,y)
    plt.show()
    #return 54,4
    return a,n

def calculate_error(output):
    ret=0
    count=0
    for i in output:
        if i[2] in gd:
            x=gd[i[2]][0]
            y=gd[i[2]][1]
            ret=ret+((i[0]-x)**2+(i[1]-y)**2)**0.5
            count=count+1
    print("Error is:",ret/count)

def read_data(file_path_list):
    for i in raw_gd:
        date = datetime.datetime.strptime(i[0],'%Y/%m/%d %H:%M')
        gd[date]=[checkpoint[i[1]][0],checkpoint[i[1]][1]]
    devicelogs = {}
    for file_path in file_path_list:
        pointIndex=file_path.rfind('.')
        if file_path[pointIndex+1:]=="csv":
            with open(file_path) as f:
                reader = list(csv.reader(f))
                log_list = []
                #print(reader)
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
                    temp.append(float(sheet.cell(j, 3).value))
                    temp.append(int(sheet.cell(j, 6).value))
                    temp.append(xlrd.xldate.xldate_as_datetime(sheet.cell(j,9).value,0))
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
            #now_date = now_date + datetime.timedelta(minutes = time_window)
    #sum = sum + len(temp)
    temp = eliminate_duplicates(temp)
    # 转化格式
    for i in range(len(temp)):
        temp[i] = [gateway[temp[i][0]][0], gateway[temp[i][0]][1], distance_to_BS(temp[i][1],a,n)]
    result[now_date] = temp
    #print("In process_data:sum=",sum)
    #print("In process_data:raw_list=",len(raw_list))
    return result  # {datetime:[[gateway_x, gateway_y, distance],...]}


def eliminate_duplicates(temp_l):
    count = {}
    result = []
    for x in temp_l:
        if x[0] not in count:
            count[x[0]] = [x[1]]
        else:
            count[x[0]].append(x[1])
    for key, value in count.items():
        result.append([key, sum(value)/len(value)])  # 消除重复的策略可改，这里定的是均值
    return result


if __name__ == "__main__":
    path =['./data/bkg data/03-28-Abeacon3.csv','./data/bkg data/03-28-mi.csv']
    result_path = './result/result4.xlsx'
    raw_data,a,n = read_data(path)
    wb = xlwt.Workbook(encoding='utf-8')
    style = xlwt.XFStyle()
    style.num_format_str = 'M/D/YY h:mm'
    # plt.xlabel('X')
    # plt.ylabel('Y')
    # plt.xlim(xmax=45,xmin=0)
    # plt.ylim(ymax=29,ymin=0)
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
    calculate_error(output)
    wb.save(result_path)
