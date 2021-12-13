## 输入 filename，csv格式
## 输出 异常指数
## 方法，通过结合与陌生人的通话频率和通话时长这两个因素对异常进行评分
import re
import pandas as pd
import numpy as np


def phonecall_anomaly(phone_num, during, phonebook): ## 如 id = '001'
    # filename = 'phonecall/001_phone.csv'
    # data = pd.read_csv(filename)
    # alias = data['Alias']
    # during = data['During']
    unkonwn_list = []
    index = 0
    for i in range(len(phonebook)):
        phonebook[i] = re.sub('\+86| ', '', phonebook[i])

    for i in phone_num:
        if i not in phonebook:
            unkonwn_list.append(index)
        index += 1
    if unkonwn_list==[]:
        return 0, 0
    # 频次统计
    all_un_freq = len(unkonwn_list)
    all_freq = len(phone_num)
    freq_rate = all_un_freq/all_freq

    # 时长统计
    during = np.array(during)
    unkonwn_during = during[unkonwn_list]
    un_dur_sum = unkonwn_during.sum()
    all_dur_sum = during.sum()
    during_rate = un_dur_sum/all_dur_sum

    # # 以alpha为比率结合以上两项
    # alpha = 0.7
    # anomaly = (alpha*freq_rate+(1-alpha)*during_rate)*100

    # print("%.2f"%(anomaly))
    return freq_rate, during_rate
