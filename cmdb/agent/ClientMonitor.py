#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File  : ClientMonitor.py
# Author: chenweizhang
# Date  : 2019/9/20
import datetime
import inspect
import json
import math
import multiprocessing
import os
import platform
import socket
import subprocess

import psutil
from twisted.protocols import basic
from twisted.internet import protocol, defer, task
import Get_basic_info_2 as Huoqu
import guardian as shouhu
import time
from twisted.application import service, internet

class InfoGather(object):

    def __init__(self):
        '''
        初始化信息，采集一些公用信息
        '''
        self.agent_data = dict()
        self.now_capture_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        '''
        self.hostname = socket.gethostname()

        try:
            csock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
            csock.connect(('8.8.8.8',80))
            (addr,port) = csock.getsockname()
            self.ip = addr
        except socket.error:
            self.ip = '127.0.0.1'
        finally:
            csock.close()
       # self.agent_data['hostname'] = self.hostname
        self.agent_data['ip'] = self.ip
        '''
        self.agent_data['capturetime'] = self.now_capture_time
    def get_hostname(self):

        self.hostname = socket.gethostname()
        return self.hostname
    def get_ip(self):

        try:
            csock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            csock.connect(('8.8.8.8', 80))
            (addr, port) = csock.getsockname()
            self.ip = addr
        except socket.error:
            self.ip = '127.0.0.1'
        finally:
            csock.close()
        return self.ip

    def get_platform(self):
        '''

        获取服务器操心系统信息
        '''
        try:
            osname = platform.platform()
            uname = platform.uname()

            if osname == ' ':
                osname = uname[0]

            data = {'osname':osname,'kernel':uname[2],'hostname':uname[1]}
        except Exception as f:
            print(f)
            data = str(f)
        return data
    def get_uptime(self):
        '''
        获取服务器运行时间
        :return:
        '''
        try:
            with open('/proc/uptime','r') as f:
                uptime_seconds = float(f.readline().split()[0])
                uptime_time = str(datetime.timedelta(seconds=uptime_seconds))
                date = uptime_time.split('.',1)[0]
        except Exception as f:
            print(f)
            date = f
        return date
    def get_load(self):
        '''
        获取系统平均负负载
        :return:
        '''
        try:
            data = os.getloadavg()[0]
        except Exception as err:
            print(err)
            data = err
        return data

    def get_cpus(self):
        '''
        获取cpu型号等相关硬件信息
        :return:
        '''
        try:
            pipe = subprocess.Popen("cat /proc/cpuinfo | grep 'model name'",shell=True,stdout=subprocess.PIPE)
            date = str(pipe.stdout.read().strip(),encoding='utf-8').split(':')[-1].strip()
            if not date:
                date = None
            cpus = multiprocessing.cpu_count()

            date = "{CPUS} X {CPU_TYPE}".format(CPUS=cpus,CPU_TYPE=date)
        except Exception as err:
            print(err)
            date = str(err)
        return date

    def get_cpus_usage(self):
        '''
        获取cpu使用率
        ['avg-cpu:', '%user', '%nice', '%system', '%iowait', '%steal', '%idle'], ['0.68', '0.00', '0.26', '0.04', '0.00', '99.02']
        '''
        try:
            cpu_pipe = subprocess.Popen("iostat",shell=True,stdout=subprocess.PIPE)
            cpu_res = [str(line,encoding='utf-8').strip('\n').split() for line in cpu_pipe.stdout.readlines()]

            cpu_date = cpu_res[3]

            user_cpu = float(cpu_date[0])
            nice_cpu = float(cpu_date[1])
            system_cpu = float(cpu_date[2])
            iowait_cpu = float(cpu_date[3])
            steal_cpu = float(cpu_date[4])
            idle_cpu = float(cpu_date[5])

            usage_cpu = 100 - idle_cpu

            cpu_usage_date = {
                'user_cpu':user_cpu,
                'nice_cpu':nice_cpu,
                'system_cpu':system_cpu,
                'iowait_cpu':iowait_cpu,
                'steal_cpu':steal_cpu,
                'idle_cpu':idle_cpu,
                'usage_cpu':usage_cpu,
            }
            data = cpu_usage_date

        except Exception as err:
            print(err)
            data = str(err)

        return data

    def get_mem(self):
        try:
            mem_info = subprocess.Popen("free -m",shell=True,stdout=subprocess.PIPE)
            mem_res = [str(line,encoding='utf-8').strip('\n').split() for line in mem_info.stdout.readlines() ]

            if len(mem_res) == 3:
                men_date = mem_res[1]
                men_swap = mem_res[2]

                mem_total = men_date[1]
                mem_used = men_date[2]
                mem_free = men_date[3]

                swap_total = men_swap[1]
                swap_used = men_swap[2]
                swap_free = men_swap[3]
                mem_percent = str(round(int(mem_used)*100/int(mem_total),2))
            elif len(mem_res) == 4:
                men_date = mem_res[1]
                men_swap = mem_res[3]

                mem_total = men_date[1]
                mem_used = men_date[2]
                mem_free = men_date[3]

                swap_total = men_swap[1]
                swap_used = men_swap[2]
                swap_free = men_swap[3]
                mem_percent = str(round(int(mem_used) * 100 / int(mem_total), 2))
            else:
                # 未知错误
                mem_total = 0
                mem_used = 0
                mem_free = 0

                swap_total = 0
                swap_used = 0
                swap_free = 0
                mem_percent = 0
            date = {
                'mem_total':mem_total,
                'mem_used':mem_used,
                'mem_free':mem_free,
                'swap_total':swap_total,
                'swap_used':swap_used,
                'swap_free':swap_free,
                'mem_percent':mem_percent,
            }
        except Exception as f:
            print(f)
            date = str(f)

        return  date
    def get_disk(self):
        '''
        获取硬盘使用情况

        '''
        try:
            disk_info = subprocess.Popen("df -Ph | grep -v Filesystem | awk '{print $1, $2, $3, $4, $5, $6}'",
                                         shell=True,stdout=subprocess.PIPE)
            date = str(disk_info.stdout.read(),encoding='utf8').strip().split('\n')
            date = [line.strip().split() for line in date]

        except Exception as err:
            print(err)
            date = str(err)

        return date

    def get_disk_rw(self):
        '''
        硬盘读写IO情况
        '''
        try:
            disk_rw_info = subprocess.Popen("iostat -kx",shell=True,stdout=subprocess.PIPE)

            disk_rw = disk_rw_info.stdout.readlines()

            disk_res = [str(line,encoding='utf-8').strip('\n').split() for line in disk_rw]

            disk_io_date = disk_res[6:-1]
            '''
            ===============================disk_io_date数据示列===================================
            数据的每一列题头
            [Device,rrqm/s,wrqm/s,r/s,w/s,rkB/s,wkB/s,avgrq-sz,avgqu-sz,await,r_await,w_await,svctm,%util]
            实际的数据
            [vda,0.00,0.21,0.00,0.41,0.06,3.78,18.57,0.00,7.50,3.95,7.53,1.21,0.05]
            '''
            date = disk_io_date

        except Exception as err:
            print(err)
            date = err

        return date



    def get_traffic(self):
        '''
        获取网卡流量信息
        '''
        try:
            key_info = psutil.net_io_counters(pernic=True).keys()
            result = psutil.net_io_counters(pernic=True)

            date = list()
            for key in  key_info:
                flag = list()
                if key == 'lo':
                    continue
                flag.append(key)
                flag.append(int(result.get(key).bytes_recv)/1024)
                flag.append(int(result.get(key).bytes_sent)/1024)
                date.append(flag)

        except Exception as err:
            print(err)
            date = str(err)

        return date


    def get_sockets(self):
        '''
        获取sockets连接信息
        :return:
        '''
        try:
            cmd = "ss -tnp | grep ESTAB | awk '{print $4, $5}'| sed 's/::ffff://g' | " \
                    "awk -F: '{print $1, $2}' | awk 'NF > 0' | sort -n | uniq -c"
            sub = subprocess.Popen(cmd,shell=True, stdout=subprocess.PIPE)

            result = str(sub.stdout.read(),encoding='utf-8').strip().split('\n')

            date = [ i.split(None,4) for i in result]

        except Exception as err:
            print(err)
            date = str(err)
        return date


    def run_all_get_fun(self):

        for func in inspect.getmembers(self,predicate=inspect.ismethod):
            #print(func)
            if func[0][:3] == 'get':

                self.agent_data[func[0][4:]] = func[1]()


        return json.dumps(self.agent_data)
class Monitor_Protocol(basic.LineReceiver):
    # 自定义客户端和服务端的连接协议，从basic的line继承

    def __init__(self):
        #
        pass

    @staticmethod
    def huoqu_shuju():

        result = InfoGather().run_all_get_fun()
        d = defer.Deferred()
        # 使用defered返回结果
        d.callback(result)
        return d

    def xunhuan(self, list):
        # 定义循环发送函数

        for i in range(1,math.ceil(len(list)/300)+1):

            tmp = list[0:300]
            list = list[300*i::]
            self.sendLine(tmp)



    def fasong(self):
        # 定义程序运行顺序，取得信息后用callback交给发送函数发送
        self.huoqu_shuju().addCallback(self.xunhuan)

    def loop(self):
        # 使用twist内置的循环函数定义几秒监控数据传送到服务端
        l = task.LoopingCall(self.fasong)
        l.start(1)

    def connectionMade(self):
        # 覆盖协议的connectmade函数，定义于服务端的连接建立后开始循环
        print
        'Connected!......ok!'
        self.loop()

    def lineReceived(self, line):
        # 必须覆盖接受函数，否则twist会报not importent错误！
        pass


class Moinitor_client_factory(protocol.ReconnectingClientFactory):

    def __init__(self, service):
        # 还没想要要写什么
        self.service = service

    protocol = Monitor_Protocol


class Client_Service(service.Service):

    def __init__(self):
        pass

    def startService(self):
        service.Service.startService(self)


# 配置文件开始
port = 10000
host = '127.0.0.1'

# 守护进程
top_service = service.MultiService()  # 定义服务容器

client_service = Client_Service()  # 实例化服务类
client_service.setServiceParent(top_service)  # 把自己定义的服务丢到服务容器中

factory = Moinitor_client_factory(client_service)  # 定义服务工厂化

tcp_service = internet.TCPClient(host, port, factory)  # 定义tcp连接的服务
tcp_service.setServiceParent(top_service)  # 把tcp服务丢到服务容器中去

application = service.Application('Fish_Service')  # 定义应用名字
top_service.setServiceParent(application)  # 把服务容器丢到应用中去