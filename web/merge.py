import pymysql
from .dbscan import gps_anomaly
from .phonecall import phonecall_anomaly
from .sms import sms_anomaly
from datetime import datetime
import time

ip="ip"
port=3306
user="database user"
passwd="password"

# id-社区矫正人员编号,int/str  days-检测天数,int
def get_gps(id, days):
    # mysql connection
    db = pymysql.connect(host=ip, port=port,
                         user=user, passwd=password, db="justice", charset='utf8')
    cursor = db.cursor()

    # gps part
    gps_sql = "select WD,JD,SJ from GPS where SQJZRYBH='%s' ORDER BY SJ DESC"%(id)
    cursor.execute(gps_sql)
    gps_data = cursor.fetchall()
    # 未读取到该id的相关数据
    if gps_data == ():
        description = '未读取到编号'+str(id)+'的相关GPS数据'
        gps_index = 0
        print(gps_index, description)
        return gps_index, description
    gps_lat = []
    gps_lng = []
    timestamp = []
    for row in gps_data:
        gps_lat.append(row[0])
        gps_lng.append(row[1])
        timestamp.append(int(row[2])/1000.0)
    db.close()
    if len(gps_lng)<400:
        description = '编号'+str(id)+'GPS数据较少，无法计算'
        gps_index = 0
        print(gps_index, description)
        return gps_index, description
    time_now = timestamp[0]
    week_sec = days*24*60*60  # use 143*24*60*60 to test
    time_boundary = time_now - week_sec
    dt = datetime.fromtimestamp(time_boundary).strftime("%Y-%m-%d")
    train_lat, test_lat, train_lng, test_lng = [], [], [], []
    for i in range(len(timestamp)):
        if timestamp[i] > time_boundary:
            test_lat.append(gps_lat[i])
            test_lng.append(gps_lng[i])
        else:
            train_lat.append(gps_lat[i])
            train_lng.append(gps_lng[i])
    # print(len(train_lng),len(test_lng))
    if len(train_lng)<200:
        description = '编号'+str(id)+'历史GPS数据较少，无法计算'
        gps_index = 0
        print(gps_index, description)
        return gps_index, description
    if len(test_lat)==0:
        description = '自'+str(dt)+'起'+str(days)+'天内无运动轨迹'
        gps_index = 0
        print(gps_index, description)
        return gps_index, description
    gps_index = gps_anomaly(train_lat, train_lng, test_lat, test_lng)
    description = '自'+str(dt)+'起'+str(days)+'天内运动轨迹超出历史正常范围的占比为%.2f%%' % (gps_index)
    print(gps_index, description)

    return gps_index, description

def get_phonecall(id, days):
    # mysql connection
    db = pymysql.connect(host=ip, port=port,
                         user=user, passwd=password, db="justice", charset='utf8')
    cursor = db.cursor()
    # phonecall part
    call_sql1 = "select DFSJH,CXSJ,JTSJ from PhoneCall where SQJZRYBH='%s' ORDER BY JTSJ DESC"%(id)
    cursor.execute(call_sql1)
    call_data = cursor.fetchall()
    # 未读取到该id的相关数据
    if call_data == ():
        description = '未读取到编号' + str(id) + '的相关PhoneCall数据'
        call_index = 0
        print(call_index, description)
        return call_index, description
    call_num, call_time, book_num = [], [], []
    timestamp = []
    for row in call_data:
        call_num.append(row[0])
        call_time.append(row[1])
        timestamp.append(int(row[2])/1000.0)
    call_sql2 = "select SJH from PhoneBook where SQJZRYBH='%s' "%(id)
    cursor.execute(call_sql2)
    call_data2 = cursor.fetchall()
    for row in call_data2:
        book_num.append(row[0])
    db.close()

    time_now = timestamp[0]
    week_sec = days * 24 * 60 * 60  # use 150*24*60*60 to test
    time_boundary = time_now - week_sec
    dt = datetime.fromtimestamp(time_boundary).strftime("%Y-%m-%d")
    train_num, test_num, train_time, test_time = [], [], [], []
    for i in range(len(timestamp)):
        if timestamp[i] > time_boundary:
            test_num.append(call_num[i])
            test_time.append(call_time[i])
        else:
            train_num.append(call_num[i])
            train_time.append(call_time[i])
    # print(len(train_num), len(test_num))
    train_freq, train_during = phonecall_anomaly(train_num, train_time, book_num)
    test_freq, test_during = phonecall_anomaly(test_num, test_time, book_num)
    if train_freq==0:
        description = '编号' + str(id) + '无陌生通话相关历史记录'
        call_index = 0
        print(call_index, description)
        return call_index, description
    if test_freq==0:
        description = '编号' + str(id) + '无陌生通话相关检测记录'
        call_index = 0
        print(call_index, description)
        return call_index, description

    freq_rate = 100*(test_freq-train_freq)/train_freq
    during_rate = 100*(test_during-train_during)/train_during

    if freq_rate>=0:
        des1 = '自'+str(dt)+'起'+str(days)+'天内与陌生人通话频率超出历史水平的%.2f%%，' % freq_rate
    else:
        des1 = '自'+str(dt)+'起'+str(days)+'天内与陌生人通话频率低于历史水平的%.2f%%，' % abs(freq_rate)

    if during_rate>=0:
        des2 = '通话时长超出历史水平的%.2f%%' % during_rate
    else:
        des2 = '通话时长低于历史水平的%.2f%%' % abs(during_rate)

    description = des1+des2
    alpha = 0.5
    phonecall_index = min(100,(alpha*abs(freq_rate)+(1-alpha)*abs(during_rate)))
    print(phonecall_index, description)

    return phonecall_index, description


def get_sms(id, days):
    # mysql connection
    db = pymysql.connect(host=ip, port=port,
                         user=user, passwd=password, db="justice", charset='utf8')
    cursor = db.cursor()
    # sms part
    sms_sql = "select DXNR,SFSJ from SMS where SQJZRYBH='%s' ORDER BY SFSJ DESC"%(id)
    cursor.execute(sms_sql)
    sms_data = cursor.fetchall()
    # 未读取到该id的相关数据
    if sms_data == ():
        description = '未读取到编号' + str(id) + '的相关SMS数据'
        sms_index = 0
        print(sms_index, description)
        return sms_index, description

    sms_content,timestamp = [], []
    for row in sms_data:
        sms_content.append(row[0])
        timestamp.append(int(row[1])/1000.0)
    db.close()

    time_now = timestamp[0]
    week_sec = days * 24 * 60 * 60  # use 152*24*60*60 to test
    time_boundary = time_now - week_sec
    dt = datetime.fromtimestamp(time_boundary).strftime("%Y-%m-%d")
    train_content, test_content = [], []
    for i in range(len(timestamp)):
        if timestamp[i] > time_boundary:
            train_content.append(sms_content[i])
        else:
            test_content.append(sms_content[i])
    # print(len(train_content), len(test_content))
    in_anomaly, out_anomaly = sms_anomaly(train_content, test_content)
    des1, des2 = '', ''
    if in_anomaly>0:
        des1='自'+str(dt)+'起'+str(days)+'天内资金收入高出历史水平的%.2f%%，'%in_anomaly
    elif in_anomaly<0:
        des1 = '自'+str(dt)+'起'+str(days)+'天内资金收入低于历史水平的%.2f%%，' % abs(in_anomaly)
    if out_anomaly>0:
        des2='支出高出历史水平的%.2f%%'%out_anomaly
    elif out_anomaly<0:
        des2 = '支出低于历史水平的%.2f%%' % abs(out_anomaly)

    description = des1+des2
    if description == '':
        description = '无资金收入或支出相关信息'
        print(0, description)
        return 0, description
    rate = 0.5
    sms_index = min(100, (rate * in_anomaly + (1 - rate) * out_anomaly))

    print(sms_index, description)
    return sms_index, description


######## 用于测试的代码 ##########
# a, b = get_gps(phonenum, 7)  # 该用户用最近1天结果较好
# a, b = get_gps(phonenum, 7)  # 该用户用最近7天结果较好
# a, b = get_gps(111, 7)  # 测试找不到id相关数据

# a, b = get_phonecall(phonenum, 7)  # 最近七天 通话频率超出历史水平的44.44%，通话时长超出历史水平的445.57%
# a, b = get_phonecall(phonenum, 7)  # 最近七天 通话频率低于历史水平的9.71%，通话时长低于历史水平的6.48%
# a, b = get_phonecall(111, 7)  # 测试找不到id相关数据

# a, b = get_sms(phonenum, 7)  # 7天内资金收入高出历史水平的84.21%，支出高出历史水平的176.60%
# a, b = get_sms(phonenum, 7)  # 用于检测没有资金流动信息的人员，会输出无资金xx相关xx信息
# a, b = get_sms(111, 7) # 测试找不到id相关数据
