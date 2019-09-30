#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File  : ServiceMonitor.py
# Author: chenweizhang
# Date  : 2019/9/21
import json
import os
import sys

from twisted.internet import reactor
from twisted.python import log,logfile
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

sys.path.append(base_dir)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cmdb_web.settings")
import django
django.setup()

from cmdb.models import  ac_cpu, ac_mem, ac_disk, ac_net
from twisted.internet.protocol import ServerFactory
from twisted.protocols import basic
from twisted.application import service, internet
BASE_LOG_DIR = os.path.join(base_dir, "log")
f = logfile.DailyLogFile('service_agent.log', BASE_LOG_DIR)
log.startLogging(f)
class Mornitor_Protocol(basic.LineReceiver):

    def __init__(self):
        #

        pass
    def update(self,line):

        '''

        接受到json参数格式如下:
            {
            "hostname": "iZbp14xkfh6vkt9ane0gb8Z",
            "ip": "47.97.30.46",
            "capturetime": "2018-11-06 13:21:05",
            "cpus": "2 X Intel(R) Xeon(R) Platinum 8163 CPU @ 2.50GHz",
            "cpus_usage": {
                "user_cpu": 7.37,
                "nice_cpu": 0.0,
                "system_cpu": 1.09,
                "iowait_cpu": 4.98,
                "steal_cpu": 0.0,
                "usage_cpu": 13.439999999999998
            },
            "disk": [['/dev/vda1', '40G', '19G', '19G', '51%', '/'], ['/dev/vdb', '197G', '140G', '48G', '75%', '/data']],
            "disk_rw": [
                ["vda", "1.06", "1.89", "3.09", "1.46", "42.98", "16.27", "26.07", "0.03", "7.69", "6.24", "10.77", "1.83", "0.83"],
                ["vdb", "0.00", "334.14", "11.23", "99.21", "293.01", "1921.32", "40.10", "0.04", "0.34", "6.32", "2.56", "0.75", "8.32"]
            ],
            "load": 0.27,
            "mem": {'mem_total': '3951', 'mem_used': '3184', 'mem_free': '108', 'swap_total': '4095', 'swap_used': '2546', 'swap_free': '1549', 'mem_percent': 80.59},
            "platform": {
                "osname": "Linux-4.4.95-1.al7.x86_64-x86_64-with-centos-17.01.2-Golden_Toad",
                "kernel": "4.4.95-1.al7.x86_64",
                "hostname": "iZbp14xkfh6vkt9ane0gb8Z"
            },
            "sockets": [
                ["1", "10.81.45.158", "33506", "10.31.129.160"],
                ["1", "10.81.45.158", "49382", "100.100.30.25"]

            ],
            "traffic": [
                ["eth1", 1277952235, 86291093 ],
                ["eth0", 2086103, 34240133, ]
            ],
            "uptime": "173 days, 3:34:03"
        }
        :param request:
        :return:
        '''
        ip = self.transport.getPeer().host  # 获取客户端IP
        agent_date = json.loads(line)  # 解析json
        log.msg(agent_date)

        try:

            '''
            cpu详细信息入库,表ns_cpu
            '''
            cpu = ac_cpu()
            cpu.hostname = agent_date['hostname']
            cpu.ip = agent_date['ip']
            cpu.capturetime = agent_date['capturetime']
            cpu.user_cpu = '%.1f' % agent_date['cpus_usage']['user_cpu']
            cpu.nice_cpu = '%.1f' % agent_date['cpus_usage']['nice_cpu']
            cpu.system_cpu = '%.1f' % agent_date['cpus_usage']['system_cpu']
            cpu.iowait_cpu = '%.1f' % agent_date['cpus_usage']['iowait_cpu']
            cpu.steal_cpu = '%.1f' % agent_date['cpus_usage']['steal_cpu']
            cpu.idle_cpu = '%.1f' % agent_date['cpus_usage']['idle_cpu']
            cpu.usage_cpu = '%.1f' % agent_date['cpus_usage']['usage_cpu']
            cpu.load_avg = '%.1f' % agent_date['load']
            cpu.save()
            log.msg('cpu详细信息入库成功')
            '''
               内存、虚拟内存使用详情入库ns_mem
    
            '''
            mem = ac_mem()
            mem.hostname = agent_date['hostname']
            mem.ip = agent_date['ip']
            mem.capturetime = agent_date['capturetime']
            mem.mem_total = agent_date['mem']['mem_total']
            mem.mem_used = agent_date['mem']['mem_used']
            mem.mem_free = agent_date['mem']['mem_free']
            mem.swap_total = agent_date['mem']['swap_total']
            mem.swap_used = agent_date['mem']['swap_used']
            mem.swap_free = agent_date['mem']['swap_free']
            mem.mem_percent = agent_date['mem']['mem_percent']
            mem.save()
            log.msg('内存、虚拟内存使用详情入库成功')
            '''
            硬盘使用详情入库ns_disk表
    
            '''
            disk = ac_disk()
            disk.hostname = agent_date['hostname']
            disk.ip = agent_date['ip']
            disk.capturetime = agent_date['capturetime']
            disk.disk = agent_date['disk']
            disk.disk_io = agent_date['disk_rw']  # 硬盘读写
            disk.save()
            log.msg('硬盘使用详情入库成功')
            '''
               网卡信息
            '''
            net = ac_net()

            for row in agent_date['traffic']:
                net.hostname = agent_date['hostname']
                net.ip = agent_date['ip']
                net.capturetime = agent_date['capturetime']

                net.interface = row[0]
                net.traffic_in = row[1]
                net.traffic_out = row[2]
                net.sockets = agent_date['sockets']
                net.save()
            log.msg('网卡信息入库成功')
        except Exception as e:
            log.err("入库失败----->[%s]" % e)
    '''
    def ruku(self, line):
        ip = self.transport.getPeer().host
        # 获取客户端IP
        line = line.split(':::')
        # 使用：：：分割原始数据
        if line[1] in ['cpu', 'mem', 'disk', 'tcp', 'net', 'process_down']:
            # 根据数据包头来确定使用insert还是update，当是tcp包头的时候插入，其余的更新
            if line[1] == 'tcp':
                sql = "insert into MORNITOR_BASICINFO (ipadd,time,tcp) values (\'%s\',\'%s\',\'%s\')" % (
                ip, line[0], line[3])
                print
                sql
                self.cur.execute(sql)

            else:
                line_again = line[3].split('::')
                sql = 'update MORNITOR_BASICINFO set %s=\'%s\',%s=\'%s\' where ipadd=\'%s\' and time=\'%s\'' % (
                line[1], line_again[0], line[2], line_again[1], ip, line[0])
                print
                sql
                self.cur.execute(sql)
    '''
    def connectionMade(self):
        log.msg('Connected!')


    def lineReceived(self, line):

        ip = self.transport.getPeer().host  # 获取客户端IP
        log.msg('接收客户端[%s]消息[%s]'%(ip,line))
        #self.ruku(line)
        # 接受到数据之后执行入库操作!
        self.update(line)


    def connectionLost(self, reason='connectionDone'):
        #self._oracle_conn.close()
        log.msg('The connection is close... ok!')



class Mornitor_Factory(ServerFactory):
    # 还没想好要初始化什么
    def __init__(self, service):
        self.service = service

    protocol = Mornitor_Protocol


class Fish_Service(service.Service):

    def __init__(self):
        pass

    def startService(self):
        service.Service.startService(self)  # 什么都不做，开始服务

    # def stopService(self):
    #     return self._port.stopListening()


# 配置参数
port = 10000
iface = '127.0.0.1'
top_server = service.MultiService()  # 定义服务容器

fish_server = Fish_Service()  # 实例化我们的服务
factory = Mornitor_Factory(Fish_Service)  # 工厂化服务
fish_server.setServiceParent(top_server)  # 把自定义的服务加入到服务容器



tcp_server = internet.TCPServer(port, factory)  # 定义tcp服务
#tcp_server = reactor.listenTCP(port, factory)

tcp_server.setServiceParent(top_server)  # 把tcp服务加入到服务容器
#
application = service.Application('Fish_Service')  # 给应用起个名字
top_server.setServiceParent(application)  # 把服务容器丢到应用中去