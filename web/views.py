# coding=utf-8
import datetime

from django.shortcuts import render

from django.http import JsonResponse
from django.http import HttpResponse
from django.shortcuts import render
import json
import os
import random
import xml.dom.minidom
import unicodedata
import time

# Create your views here.
from numpy.core import unicode
from . import merge

import csv

#行为异常
def Behavior(request):
    '''
    客户端行为异常请求接口
    传过来两类人员编号，调用短信、通话记录、gps等异常检测函数，返回值整理之后，传回给客户端。
    :param request: 'sqjzrybh'
    :return
        data (dict):将所有值整合到一个dict中，返回 {“code”:string,"data":{}}

    '''
    res={}
    user_id=json.loads(str(request.body.decode()))['sqjzrybh']
    print(user_id)
    #数据不对应，采集的有32，给的有50，大于32的都给一个固定的
    #if user_id>='S3701022019120034' and user_id<='S3701022019120051':
     #   user_id='S3701022019120028'
    if Block_id(id): 
        res["code"]=0
        data={}
        data["title"]="异常行为"
        list=[]
        list.append({"name":'移动轨迹异常',
                     "score":0,
                     "content":"未读取到编号"+id+"相关的GPS数据"})
        list.append({"name":"短信异常",
                     "score":0,
                     "content":"未读取到编号"+id+"相关的SMS数据"})
        list.append({"name": "通话异常",
                     "score": 0,
                     "content": "未读取到编号"+id+"相关的PhoneCall数据"})
        data["list"]=list
        res["data"]=data
    else:

        user_id=Deal_id(user_id)
        res["code"]=0
        data={}
        data["title"]="异常行为"
        list=[]
        gps_index, gps_description=merge.get_gps(user_id,7)
        print(gps_index, gps_description)
        list.append({"name":'移动轨迹异常',
                     "score":gps_index,
                     "content":gps_description})
        sms_index, sms_description=merge.get_sms(user_id,7)
        print(sms_index, sms_description)
        list.append({"name":"短信异常",
                     "score":sms_index,
                     "content":sms_description})
        phonecall_index, phonecall_description=merge.get_phonecall(user_id,7)
        print(phonecall_index, phonecall_description)
        list.append({"name": "通话异常",
                     "score": phonecall_index,
                     "content": phonecall_description})
        data["list"]=list
        res["data"]=data

    return HttpResponse(json.dumps(res))

def Block_id(id):
    SQJZRYBHs=[]
    with open('block.csv') as csvfile:
        csv_reader = csv.reader(csvfile)
        for row in csv_reader:
            SQJZRYBHs.append(row[0])
    if id in SQJZRYBHs:
        return True
    
def Deal_id(id):
    SQJZRYBHs=[]
    with open('name_new.csv') as csvfile:
        csv_reader = csv.reader(csvfile)
        for row in csv_reader:
            SQJZRYBHs.append(row[0])
    #print(SQJZRYBHs)
    if id in SQJZRYBHs:
        index=SQJZRYBHs.index(str(id))
        return SQJZRYBHs[index%32]
    return id


def LogInfo(request):
    '''
    手机端采集数据注册接口
    :param request:
    :return:
    '''
    user=json.loads(str(request.body.decode()))
    print(user)
    res = {}
    res['res'] = 200
    res['msg']='success'
    if(user['PhoneNum']==None or user['PhoneNum']==""):
        res['res']=201
        res['msg']='phonenumber is null'

    path ="userdata/"+user['PhoneNum']
    if not os.path.exists(path):
        os.makedirs(path)
        if not os.path.exists(path+"/userinfo.txt"):
            os.mknod(path+"/userinfo.txt")
            with open(path+"/userinfo.txt","w",encoding="utf-8") as f:
                json.dump(user,f,ensure_ascii=False)
    else:
        res['res'] = 202
        res['msg'] = 'User is already'
    return HttpResponse(json.dumps(res))

def PhoneCall(request):
    res = {}
    data = json.loads(str(request.body.decode()))
    print(data)
    path = "userdata/" + data["PhoneNum"]
    if not os.path.exists(path+"/phonecall.txt"):
        os.mknod(path+"/phonecall.txt")
        with open(path + "/phonecall.txt", "w", encoding="utf-8") as f:
            load_dict ={}
            load_dict["data"]=[]
            json.dump(load_dict, f,ensure_ascii=False)
    load_dict={}
    with open(path+"/phonecall.txt","r",encoding="utf-8") as f1:
        load_dict=json.load(f1)
        for call in load_dict['data']:
            if call['TimeStamp'] == data['TimeStamp']:
                res['res'] = 202
                res['msg'] = 'call is already'
                return HttpResponse(json.dumps(res))
        load_dict["data"].append(data)
        #print(load_dict)
    with open(path + "/phonecall.txt", "w", encoding="utf-8") as f2:
        json.dump(load_dict,f2,ensure_ascii=False)
        # print(load_dict1)


    res['res'] = 200
    res['msg'] = 'success'
    return HttpResponse(json.dumps(res))

def PhoneBook(request):
    data = json.loads(str(request.body.decode()))
    print(data)

    res = {}
    res['res'] = 200
    res['msg'] = 'success'

    path ="userdata/"+data["PhoneNum"]+'/phonebook.txt'

    if not os.path.exists(path):
        os.mknod(path)
    else:
        res['res'] = 202
        res['msg'] = 'phonebook is already'
        return HttpResponse(json.dumps(res))
    with open(path,"w",encoding="utf-8") as f:
        json.dump({"data":data['data']},f,ensure_ascii=False)

    return HttpResponse(json.dumps(res))

def SmsCall(request):
    res = {}
    data=json.loads(str(request.body.decode()))
    print(data)

    path = "userdata/" + data["PhoneNum"]+"/smscall.txt"
    if not os.path.exists(path):
        os.mknod(path)
        with open(path, "w", encoding="utf-8") as f:
            load_dict = {}
            load_dict["data"] = []
            json.dump(load_dict, f,ensure_ascii=False)
    load_dict = {}
    with open(path, "r", encoding="utf-8") as f1:
        load_dict = json.load(f1)
        for sms in load_dict['data']:
            if sms['TimeStamp']==data['TimeStamp']:
                res['res'] = 202
                res['msg'] = 'sms is already'
                return HttpResponse(json.dumps(res))
        load_dict['data'].append(data)
        #print(load_dict)
    with open(path , "w", encoding="utf-8") as f2:
        json.dump(load_dict, f2,ensure_ascii=False)
        # print(load_dict1)


    res['res'] = 200
    res['msg'] = 'success'
    return HttpResponse(json.dumps(res))

def Gps(request):
    res = {}
    data = json.loads(str(request.body.decode()))
    print(data)
    path = "userdata/" + data["PhoneNum"] + "/gps.txt"
    if not os.path.exists(path):
        os.mknod(path)
        with open(path, "w", encoding="utf-8") as f:
            load_dict = {}
            load_dict["data"] = []
            json.dump(load_dict, f,ensure_ascii=False)
    load_dict = {}
    with open(path, "r", encoding="utf-8") as f1:
        load_dict = json.load(f1)
        for sms in load_dict['data']:
            if sms['TimeStamp']==data['TimeStamp']:
                res['res'] = 202
                res['msg'] = 'gps is already'
                return HttpResponse(json.dumps(res))
        load_dict['data'].append(data)
        # print(load_dict)
    with open(path , "w", encoding="utf-8") as f2:
        json.dump(load_dict, f2,ensure_ascii=False)

    res['res'] = 200
    res['msg'] = 'success'
    return HttpResponse(json.dumps(res))

def PowerInfo(request):
    data=json.loads(str(request.body.decode()))

    path = "userdata/" + data["PhoneNum"] + "/powerinfo.txt"
    if not os.path.exists(path):
        os.mknod(path)
    with open(path, "w", encoding="utf-8") as f2:
        json.dump(data, f2,ensure_ascii=False)

    res = {}
    res['res'] = 200
    res['msg'] = 'success'
    return HttpResponse(json.dumps(res))

def Question(request):
    # time=request.GET.get('time')
    PhoneNum=request.GET.get('PhoneNum')
    print(time,type(time))

    now_time=(datetime.datetime.now() + datetime.timedelta(hours=8)).strftime('%H:%M:%S')
    date=(datetime.datetime.now()+datetime.timedelta(hours=8)).strftime('%Y-%m-%d')
    if now_time>='05:00:00' and now_time<='12:00:00':
        path = "userdata/" + PhoneNum + "/morning.txt"
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f1:
                load_dict = json.load(f1)
                for question in load_dict['data']:
                    if question['date'] == date:
                        return render(request, 'morning.html')
        return render(request, 'question.html')
    elif now_time>='18:00:00' and now_time<='23:59:59':
        path = "userdata/" + PhoneNum + "/night.txt"
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f1:
                load_dict = json.load(f1)
                for question in load_dict['data']:
                    if question['date'] == date:
                        return render(request, 'night.html')
        return render(request, 'question2.html')
    else:
        return render(request, 'other.html')

def Morning(request):
    data = json.loads(str(request.body.decode()))
    data['date']=(datetime.datetime.now()+datetime.timedelta(hours=8)).strftime('%Y-%m-%d')
    data['time'] = (datetime.datetime.now() + datetime.timedelta(hours=8)).strftime('%H:%M:%S')
    print(data)
    path = "userdata/" + data["PhoneNum"] + "/morning.txt"

    if not os.path.exists(path):
        os.mknod(path)
        with open(path, "w", encoding="utf-8") as f:
            load_dict = {}
            load_dict["data"] = []
            json.dump(load_dict, f,ensure_ascii=False)
    load_dict = {}
    with open(path, "r", encoding="utf-8") as f1:
        load_dict = json.load(f1)
        load_dict['data'].append(data)
        print(load_dict)
    with open(path , "w", encoding="utf-8") as f2:
        json.dump(load_dict, f2,ensure_ascii=False)

    return HttpResponse("success")

def Night(request):
    data = json.loads(str(request.body.decode()))
    data['date'] = (datetime.datetime.now() + datetime.timedelta(hours=8)).strftime('%Y-%m-%d')
    data['time'] = (datetime.datetime.now() + datetime.timedelta(hours=8)).strftime('%H:%M:%S')
    print(data)
    path = "userdata/" + data["PhoneNum"] + "/night.txt"

    if not os.path.exists(path):
        os.mknod(path)
        with open(path, "w", encoding="utf-8") as f:
            load_dict = {}
            load_dict["data"] = []
            json.dump(load_dict, f, ensure_ascii=False)
    load_dict = {}
    with open(path, "r", encoding="utf-8") as f1:
        load_dict = json.load(f1)
        load_dict['data'].append(data)
        print(load_dict)
    with open(path, "w", encoding="utf-8") as f2:
        json.dump(load_dict, f2, ensure_ascii=False)

    return HttpResponse("success")
