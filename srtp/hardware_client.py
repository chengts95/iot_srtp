# -*- coding: utf-8 -*-
import json
import time
import threading
from bpr import bpsensor
import paho.mqtt.client as paho


port='COM5'



isfinished=threading.Event()

client = paho.Client("blood_pressure")
uid='ID002'
client.connect("iot.eclipse.org")
def getdata(sensor):
    try:
        sensor.open()
        sensor.start()
    except Exception:
        print('连接线松动，设备丢失！')
        isfinished.set()
    
    isfinished.set()
try:
   
    a=bpsensor(port)
    while client.loop()==0:
        
        data=input("是否开始测量y/n:")  #测试时用命令行，也可改成按钮
        
        if data=="y" or data=='Y':
            isfinished.clear()
            t1=threading.Thread(target=getdata,args=[a])
            t1.start()
            print('测量中...')
            isfinished.wait()
            if a.done:
                ts=time.strftime("%Y-%m-%dT%H:%M:%S")
                payload=json.dumps({'GY':{'ts':ts,'value':a.m_wSP},'DY':{'ts':ts,'value':a.m_wDP},'MB':{'ts':ts,'value':a.m_wPR}})
                client.publish('patients/%s'%uid,payload,1) 
                print(payload)  
                a.done=False 
            else:
                print(a.strInfo)
        else:
            print('退出')
            client.disconnect()
except KeyboardInterrupt:
        print("bye!")
        client.disconnect()
    
