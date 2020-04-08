import data_process
from data_process import DataProcessor
from locate import distance_to_BS, locate_by_pointlist,distance
import matplotlib.pyplot as plt 
from test import checkValid,calculate_error,plot_img


if __name__ == "__main__":
    path=['./data/bkg data/04-07-Abeacon3.csv']
    Processor = DataProcessor(plan=1,window_size=20)
    output = []
    for data_path in path:
        data = Processor.process(data_path=data_path)
        for key, value in data.items():
            locate = locate_by_pointlist(value)
            if locate[0] == 0 or locate[1] == 0:
                continue
            output.append([locate[0],locate[1],key])
    
    ax = plt.axes(xlim=(0, 42.5), ylim=(0, 29))
    imgP = plt.imread('./data/bkg data/map.PNG')
    ax.imshow(imgP, zorder=0, extent=[0, 42.5, 0.0, 29])  # 背景图片
    for item in output:
        plt.scatter(item[0],item[1])
    
    plt.show()

    # checkValid(output)
    # print(output)
    # pred=calculate_error(output)
    # plot_img(output)
    # print(pred)