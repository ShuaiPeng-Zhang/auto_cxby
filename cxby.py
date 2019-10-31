#coding=utf-8
import json
import requests
import datetime
import time
import re
import config
from pandas.core.frame import DataFrame

#获取日期
def get_date():#获取日期
    # print('获取日期')
    curr_day = datetime.datetime.now().strftime('%Y-%m-%d')
    curr_time = datetime.datetime.now().strftime('%H:%M:%S')
    time_after = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    # print(curr_day, curr_time, time_after)
    return curr_day,curr_time,time_after
#短信发送结果
def send_result(gateway_ip, time_after, time_before):
    print('短信发送结果')
    url = 'http://' + gateway_ip + '/api/query_sms_result'
    print(url)
    data = {
        "number": [config.number],
        "port": config.port_group,
        "time_after": time_after,
        "time_before": time_before,
    }
    # print(json.dumps(data))
    res = s.post(url, data=json.dumps(data), headers=head).content
    # print(res)
    error_code = json.loads(res)['error_code']
    # print(error_code)
    if error_code == 200:
        print('表示请求已经成功')
        res = json.loads(res)['result']
        # print(res)
        count = len(res)
        # print(count)
        for i in range(count):
            port = res[i]['port']
            status = res[i]['status']
            # print(port,status)
            if status == 'FAILED':
                print('%s端口发送短信失败'%port)
                with open(config.url_false,'a+') as f:
                    f.write('%s网关%s端口发送短信失败\n'%(tel_name,port))
                    f.close()

    elif error_code == 400:
        print('请求的格式有错误')
    elif error_code == 413:
        print('号码数量超过32个')
    elif error_code == 500:
        print('其他错误')
#读取短信
def read_sms(gateway_ip):
    print('读取%s网关短信'%gateway_ip)
    for i in range(32):
        print('正在读取%s端口短信......' %i)
        url = 'http://'+gateway_ip+'/api/query_incoming_sms'
        param = {
            'flag':'unread',
            'port': [i]
        }
        res = s.get(url,params=param).content.decode('utf-8')
        # print(res,type(res))
        try:
            res = json.loads(res)
            print(res["error_code"])
            if res["error_code"] == 200:
                print('请求成功')
                # print(res["sms"])
                count = len(res["sms"])
                print('共有%s条短信结果'%count)
                for i in range(count):
                    # print(res["sms"][i])
                    if res["sms"][i]['number'] == config.number:
                        port = res["sms"][i]['port']
                        text = res["sms"][i]['text']
                        if text[0:6] == '【包月查询】':
                            print(port,text)
                            if '【语音】共' in text:
                                print('查询剩余语音中......')
                                all_min = int(re.findall(r'【语音】共(.*?)分钟，',text)[0])
                                try:
                                    used_min = int(re.findall(r'已用(.*?)分钟',text)[0])
                                    try:
                                        if used_min == '1000':
                                            off_power(gateway_ip=gateway_ip, port=port)
                                            print('%s端口因免费语音使用完毕已关闭模块' % port)
                                            with open(config.url_LostMin, 'a+') as f:
                                                f.write('%s--%s网关%s端口因免费语音使用完毕已关闭模块\n' % (get_date()[2],tel_name, port))
                                                f.close()
                                        lost_min = str(int(all_min)-int(used_min))
                                        print('共%s分钟，已用%s分钟,剩余%s分钟'%(all_min,used_min,lost_min))
                                        print(port,lost_min)
                                        with open(config.url_LostMin, 'a+') as f:
                                            f.write('%s--%s网关%s端口剩余%s分钟\n' % (get_date()[2],tel_name, port,lost_min))
                                            f.close()
                                        lost_min = int(lost_min)
                                        if lost_min <= config.lostMin:
                                            off_power(gateway_ip=gateway_ip,port=port)
                                            print('%s端口因免费语音不足已关闭模块'%port)
                                            with open(config.url_LostMin, 'a+') as f:
                                                f.write('%s--%s网关%s端口因免费语音剩余%d分钟已关闭模块\n' % (get_date()[2],tel_name, port,lost_min))
                                                f.close()
                                        else:
                                            print('%s端口免费通话时间正常!'%port)
                                    except:
                                        pass
                                except:
                                    with open(config.url_LostMin, 'a+') as f:
                                        f.write('%s--%s网关%s端口剩余%s分钟\n' % (
                                        get_date()[2], tel_name, port,all_min))
                                        f.close()
                            if '您的自由话费余额' in text:
                                print('查询话费余额中......')
                                lost_money = float(re.findall(r'您的自由话费余额为(.*?)元,专项使用费余额为', text)[0])
                                print('话费余额为%s元'%lost_money)
                                with open(config.url_LostMon, 'a+') as f:
                                    f.write('%s--%s网关%s端口话费余额为%s元\n' % (get_date()[2],tel_name, port,lost_money))
                                    f.close()
                                print(port,lost_money)
                                if lost_money <= lost_money:
                                    off_power(gateway_ip=gateway_ip,port=port)
                                    print('%s端口因话费余额不足已关闭模块'%(port))
                                    with open(config.url_LostMon, 'a+') as f:
                                        f.write('%s--%s网关%s端口因话费余额为%s元已关闭模块\n' % (get_date()[2],tel_name, port,lost_money))
                                        f.close()
                                else:
                                    print('%s端口话费充足!'%port)
            elif res["error_code"] == 500:
                print('其他错误')
        except:
            print('解析错误404')
            pass
#关闭模块
def off_power(gateway_ip,port):
    print('%s端口关闭模块'%port)
    url = 'http://'+gateway_ip+'/api/set_port_info'
    data = {
        'port':port,
        'action':'power',
        'param':'off',
    }
    res = s.get(url,params=data).content
    print(res)
if __name__ == '__main__':
    s = requests.session()
    s.auth = (config.username,config.passwd)  # 将用户名密码存在session
    head = {"Content-Type": "application/json; charset=UTF-8", 'Connection': 'close'}
    for item in config.services:
        gateway_ip = item
        tel_name = gateway_ip[-2:]
        # print(tel_name)
        print('正在测试%s网关,请稍后......'%gateway_ip)
        time_after = get_date()[2]#开始测试时间
        time_before = get_date()[2]#测试结果时间
        send_result(gateway_ip=gateway_ip,time_after=time_after,time_before=time_before)
        read_sms(gateway_ip=gateway_ip)
