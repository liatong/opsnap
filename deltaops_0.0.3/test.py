#!/usr/sbin/env python
#-*- coding: utf-8 -*-
# cronte to udpate database table device_sns traffic_state 
# Author: wentong.li@deltaww.com.cn 
# 
import os 
import time 
import psycopg2

import smtplib
from email.mime.text import MIMEText  
from email.header import Header 

def sendmail(content):
    sender='woshiliwentong@163.com'
    receiver='wentong.li@deltaww.com.cn'
    subject="Cron ta update device_sns table"
    smtpserver = 'smtp.163.com'
    username=sender
    password='chaoren880820'
    
    msg = MIMEText(content,_subtype='plain',_charset='gb2312') 
    try:
        smtp = smtplib.SMTP()
        smtp.connect('smtp.163.com')
        smtp.login(username,password)
        smtp.sendmail(sender,receiver,msg.as_string())
    except:
        pass
        
def main():
    db = psycopg2.connect(database="m3vg",user="delta",password="Delta1234",host="127.0.0.1",port="5432")
    cur = db.cursor()
    sql = "SELECT * FROM device_sns SET WHERE traffic_state=1 "
    try:
        cur.execute(sql)
        db.commit()
        sendmail('UPDATE TABLE device_sns SUCCESS')
    except:
        sendmail('UPDATE TABLE device_sns FAIL!!!')
        db.rollback()
    db.close()
    
if __name__ == "__main__":
    main()
    