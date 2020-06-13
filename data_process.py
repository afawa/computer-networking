import pandas as pd
from datetime import datetime
from locate import distance_to_BS

gateway = [[], [22, 6.41], [22.62, 22.59], [41, 17.4], [31.875, 2.29], [8.35, 22.59],[6.15,3.31]]
checkpoint =[[],[39.145,17.124],[39.145,11.6],[34.112,6.905],[26.5625,3.867],[18.174,3.867],
             [6.151,3.314],[19.572,8.838],[30.757,8.838],[8.388,14.362],[8.947,19.886],[15.658,20.162],
             [24.326,20.162],[34.671,20.162],[35.789,25.133],[29.918,25.133]]
restriction=[8.862,32.1915,9.729,18.523]#left,right,bottom,top

class DataProcessor():
    def __init__(self,window_size=5,a=42, n=3.3,plan=0):
        self.window_size = window_size
        self.a = a
        self.n = n
        self.plan = plan

    def process(self,data_path):
        data_list=self.read_data(data_path=data_path)
        processed_data=self.process_data(data_list,self.window_size)
        processed_data = self.rssi2distance(processed_data,self.plan)
        return processed_data

    def timeParse(self,time:str):
        T = datetime.strptime(time,"%Y/%m/%d %H:%M:%S")
        return T


    def read_data(self,data_path:list):
        output = []
        data = pd.read_csv(data_path)
        time_list = list(data['createdAt'])
        rssi_list = list(data['rssi'])
        gateway_list = list(data['gatewayId'])
        for index,time in enumerate(time_list) :
            key = self.timeParse(time)
            temp = []
            temp.append(key)
            temp.append(gateway_list[index])
            temp.append(rssi_list[index])
            output.append(temp)
        return output 

    def process_data(self,data_list:list,window_size):
        now_time = data_list[0][0]
        result = {}
        one_second_info = []
        for raw in data_list:
            #按照秒计数
            if (raw[0]-now_time).seconds<window_size:
                temp = [raw[1],raw[2]]
                one_second_info.append(temp)
            else:
                result[now_time]=one_second_info
                one_second_info=[[raw[1],raw[2]]]
                now_time = raw[0]
            
        result[now_time] = one_second_info
        return result # {datetime:[[gateway,rssi],[],...]}

    def eliminate_duplicates(self,temp_l):
        count = {}
        result = []
        for x in temp_l:
            if x[1] is not None:
                if x[0] not in count:
                    count[x[0]] = [x[1]]
                else:
                    count[x[0]].append(x[1])
        for key, value in count.items():
            result.append([key, sum(value)/len(value)])  # 消除重复的策略可改，这里定的是均值
        return result

    def rssi2distance(self,processed_data:dict,plan:int,a=42, n=3.3):
        if plan==0 : #rssi取平均后求距离
            for key in processed_data.keys():
                temp = self.eliminate_duplicates(processed_data[key])
                for i in range(len(temp)):
                    temp[i] = [gateway[temp[i][0]][0],gateway[temp[i][0]][1], distance_to_BS(temp[i][1],a,n)]
                processed_data[key] = temp
        else : #rssi 求距离后取平均
            for key in processed_data.keys():
                temp = processed_data[key]
                for i in range(len(temp)):
                    temp[i][1] = distance_to_BS(temp[i][1],a,n)
                temp = self.eliminate_duplicates(temp)
                for i in range(len(temp)):
                    temp[i] = [gateway[temp[i][0]][0],gateway[temp[i][0]][1], temp[i][1]]
                processed_data[key] = temp
        
        return processed_data
# def resize_window(processed_data:dict):
#     for keys in sorted(processed_data.keys()):
#         l = processed_data[keys]
#         temp = set()
#         for item in l:
#             temp.add(item[0])
#         if len(temp)==1:



def check_multi_gateway(processed_data):
    for key in processed_data.keys():
        l=processed_data[key]
        temp = set()
        for item in l:
            temp.add(item[0])
        print(temp)




if __name__ == "__main__":
    data_path = './data/data/04-07-Abeacon3.csv'
    # data_list=read_data(data_path=data_path)
    # processed_data=process_data(data_list,5)
    # processed_data = rssi2distance(processed_data,0)
    test = DataProcessor(plan=1)
    test.process(data_path=data_path)
