## 输入 input_file，json格式
## 更新数据 update_file，json格式
## 测试数据 test_data，string型
## 输出训练后，更新后的资金流动统计数据，以及测试数据的异常指数
## 方法：利用正则表达式匹配流入、流出资金，并动态地统计数据，以超出平均水平的程度作为异常指数
import json
import re

import numpy as np

# 用训练样本计算收入支取均值
def train(data):
    pattern1 = r'银行'
    pattern2 = r'(支取|收入).*?([0-9]+\.[0-9]+)元'

    income = []
    outgo = []

    for sms in data['data']:
        content = sms['Content']
        if re.search(pattern1, content):
            num = re.search(pattern2, content)
            if num:
                if num.group(1) == '支取':
                    outgo.append(float(num.group(2)))
                else:
                    income.append(float(num.group(2)))

    in_avg = np.mean(income)
    out_avg = np.mean(outgo)

    return income, outgo, in_avg, out_avg


# 用新增训练样本更新收入支取均值
def update(income, outgo, in_avg, out_avg, data):
    pattern1 = r'银行'
    pattern2 = r'(支取|收入).*?([0-9]+\.[0-9]+)元'
    for sms in data['data']:
        content = sms['Content']
        if re.search(pattern1, content):
            num = re.search(pattern2, content)
            if num:
                if num.group(1) == '支取':
                    money = float(num.group(2))
                    out_avg = (out_avg * (len(outgo)) + money)/(len(outgo)+1)
                    outgo.append(money)

                else:
                    money = float(num.group(2))
                    in_avg = (in_avg * (len(income)) + money)/(len(income)+1)
                    income.append(money)
    return income, outgo, in_avg, out_avg


# 用测试样本测试异常指数
def compute_anomaly(in_avg, out_avg, data):
    pattern1 = r'银行'
    pattern2 = r'(支取|收入).*?([0-9]+\.[0-9]+)元'
    if re.search(pattern1, data):
        num = re.search(pattern2, data)
        if num:
            if num.group(1) == '支取':
                money = float(num.group(2))
                anomaly = (money - out_avg)/out_avg
                anomaly = min(max(anomaly, 0), 1)
            else:
                money = float(num.group(2))
                anomaly = (money - in_avg) / in_avg
                anomaly = min(max(anomaly, 0), 1)
    return anomaly*100

def match_inout(content, flag):
    pattern1 = r'银行'
    pattern2 = r'(支取|收入).*?([0-9]+\.[0-9]+)元'
    income = []
    outgo = []
    for i in content:
        if re.search(pattern1, i):
            num = re.search(pattern2, i)
            if num:
                if num.group(1) == '支取':
                    outgo.append(float(num.group(2)))
                else:
                    income.append(float(num.group(2)))
    if income == []:
        # print('无资金收入相关'+flag+'信息')
        income = 0
    if outgo == []:
        # print('无资金支出相关'+flag+'信息')
        outgo = 0
    return income, outgo

def sms_anomaly(content, test_content):
    income, outgo = match_inout(content, '历史')
    in_avg = np.mean(income)
    out_avg = np.mean(outgo)
    test_in, test_out = match_inout(test_content, '检测')
    # print(in_avg, out_avg)
    in_anomaly, out_anomaly = 0,0
    count = 0
    if test_in!=0:
        for i in test_in:
            diff = i - in_avg
            if diff > 0:
                in_anomaly += (diff / in_avg)
                count += 1
        if count == 0:
            in_anomaly = -100
        else:
            in_anomaly = 100*in_anomaly/count

    count = 0
    if test_out!=0:
        for i in test_out:
            diff = i - out_avg
            if diff > 0:
                out_anomaly += (diff / out_avg)
                count += 1
        if count==0:
            out_anomaly=-100
        else:
            out_anomaly = 100*out_anomaly/count

    # rate = 0.5
    # anomaly = 100*(rate * in_anomaly + (1 - rate) * out_anomaly)

    # print(anomaly, in_anomaly, out_anomaly)

    return in_anomaly, out_anomaly





