#coding=utf-8
import datetime

year = str(datetime.datetime.now().year)
month = str(datetime.datetime.now().month)
day = str(datetime.datetime.now().day)
hour = str(datetime.datetime.now().hour)
minute = str(datetime.datetime.now().minute)

#用户名密码
username = 'admin'
passwd = 'Zwl@1479!'

#服务器设置
services = [
    '192.168.2.15',
    '192.168.2.19',
    # '192.168.124.7',
]

#端口设置
port_config = 22
#发送太多端口会报错，一次最多只能15个,只能在短信发送结果中使用
port_group = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31]

#发送短信内容
content = 'cxby'

#发送短信的目标号码
number = '10086'

#日志文件保存路径
date = year+'年'+month+'月'+day+'日'+hour+'时'+minute+'分'

#发送失败端口信息保存路径
url_false = './发送失败信息/%s发送短信失败端口.log'%date

#剩余分钟数信息保存路径
url_LostMin = './电话信息/%s剩余分钟数.log'%date

#剩余话费信息保存路径
url_LostMon = './余额信息/%s话费余额.log'%date

#最低分钟设置
lostMin = 50
#最低余额设置
lostMon = 10