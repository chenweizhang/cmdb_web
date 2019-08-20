#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File  : salt_api.py
# Author: chenweizhang
# Date  : 2019/8/20
import json
import ssl
import urllib
from urllib import request, parse

ssl._create_default_https_context = ssl._create_unverified_context
class SaltAPI(object):
    __token_id = ''

    def __init__(self,url,user,password):
        self.__url = url
        self.__user = user
        self.__password = password

    def token_id(self):
        '''
        用户登陆和获取token
        :return:
        '''
        params = {'eauth':'pam','username':self.__user,'password':self.__password}
        encode = parse.urlencode(params)
        obj = parse.unquote(encode).encode('utf8')
        content = self.postRequest(obj,prefix='/login')
        try:
            self.__token_id = content['return'][0]['token']
        except KeyError:
            raise KeyError

    def postRequest(self,obj,prefix='/'):

        url = self.__url + prefix
        headers = {"X-Auth-Token":self.__token_id}
        reqp = request.Request(url,obj,headers)
        opener = request.urlopen(reqp)
        content = json.loads(opener.read().decode('utf8'))
        return content

    def list_all_key(self):
        '''
        获取认证、未认证salt主机
        '''
        params = {'client':'wheel','fun':'key.list_all'}
        obj = parse.urlencode(params).encode('utf8')
        self.token_id()
        content = self.postRequest(obj)
        minions = content['return'][0]['data']['return']['minions']
        minions_pre = content['return'][0]['data']['return']['minions_pre']
        return minions,minions_pre

    def delete_key(self,node_name):
        '''
        拒绝salt主机
        '''
        params = {'client':'wheel','fun':'key.delete','match':node_name}
        obj = parse.urlencode(params).encode('utf8')
        self.token_id()
        content = self.postRequest(obj)
        re = content['return'][0]['data']['success']
        return re

    def accept_key(self, node_name):
        '''
            接受salt主机
        '''

        params = {'client': 'wheel', 'fun': 'key.accept', 'match': node_name}
        obj = urllib.parse.urlencode(params).encode('utf-8')
        self.token_id()
        content = self.postRequest(obj)
        ret = content['return'][0]['data']['success']
        return ret

    def salt_get_jid_ret(self, jid):
        """
        通过jid获取执行结果
        :param jid: jobid
        :return: 结果
        """
        params = {'client': 'runner', 'fun': 'jobs.lookup_jid', 'jid': jid}
        obj = urllib.parse.urlencode(params).encode('utf-8')
        self.token_id()
        content = self.postRequest(obj)
        ret = content['return'][0]
        return ret

    def salt_running_jobs(self):
        """
            获取运行中的任务
        :return: 任务结果
        """
        params = {'client': 'runner', 'fun': 'jobs.active'}
        obj = urllib.parse.urlencode(params).encode('utf-8')
        self.token_id()
        content = self.postRequest(obj)
        ret = content['return'][0]
        return ret

    def remote_noarg_execution_sigle(self, tgt, fun):
        """
            单台minin执行命令没有参数
        :param tgt: 目标主机
        :param fun:  执行模块
        :return: 执行结果
        """
        params = {'client': 'local', 'tgt': tgt, 'fun': fun}
        obj = urllib.parse.urlencode(params).encode('utf-8')
        self.token_id()
        content = self.postRequest(obj)
        # print(content)
        # {'return': [{'salt-master': True}]}
        ret = content['return'][0]
        return ret

    def remote_execution_single(self, tgt, fun, arg):
        """
            单台minion远程执行，有参数
        :param tgt: minion
        :param fun: 模块
        :param arg: 参数
        :return: 执行结果
        """
        params = {'client': 'local', 'tgt': tgt, 'fun': fun, 'arg': arg}
        obj = urllib.parse.urlencode(params).encode('utf-8')
        self.token_id()
        content = self.postRequest(obj)
        # print(content)
        # {'return': [{'salt-master': 'root'}]}
        ret = content['return']
        return ret

    def remote_async_execution_module(self, tgt, fun, arg):
        """
            远程异步执行模块，有参数
        :param tgt: minion list
        :param fun: 模块
        :param arg: 参数
        :return: jobid
        """
        params = {'client': 'local_async', 'tgt': tgt, 'fun': fun, 'arg': arg, 'expr_form': 'list'}
        obj = urllib.parse.urlencode(params).encode('utf-8')
        self.token_id()
        content = self.postRequest(obj)
        # print(content)
        # {'return': [{'jid': '20180131173846594347', 'minions': ['salt-master', 'salt-minion']}]}
        jid = content['return'][0]['jid']
        return jid

    def remote_execution_module(self, tgt, fun, arg):
        """
            远程执行模块，有参数
        :param tgt: minion list
        :param fun: 模块
        :param arg: 参数
        :return: dict, {'minion1': 'ret', 'minion2': 'ret'}
        """
        params = {'client': 'local', 'tgt': tgt, 'fun': fun, 'arg': arg, 'expr_form': 'list'}
        obj = urllib.parse.urlencode(params).encode('utf-8')
        self.token_id()
        content = self.postRequest(obj)
        # print(content)
        # {'return': [{'salt-master': 'root', 'salt-minion': 'root'}]}
        ret = content['return'][0]
        return ret

    def salt_state(self, tgt, arg, expr_form):
        '''
        sls文件
        '''
        params = {'client': 'local', 'tgt': tgt, 'fun': 'state.sls', 'arg': arg, 'expr_form': expr_form}
        obj = urllib.parse.urlencode(params).encode('utf-8')
        self.token_id()
        content = self.postRequest(obj)
        ret = content['return'][0]
        return ret

    def salt_alive(self, tgt):
        '''
        salt主机存活检测
        '''
        params = {'client': 'local', 'tgt': tgt, 'fun': 'test.ping'}
        obj = urllib.parse.urlencode(params).encode('utf-8')
        self.token_id()
        content = self.postRequest(obj)
        ret = content['return'][0]
        return ret

    def access_to_asset_information(self):
        '''
        salt主机服务器信息
        '''
        params = None
        self.token_id()
        content = self.postRequest(params,prefix='/minions')
        ret = content['return']
        return ret

if __name__ == "__main__":

    salt = SaltAPI(url='https://47.98.195.152:8001',user="saltapi",password="saltapi2019")

    ret = salt.remote_execution_module('*','cmd.run','df -h')
    print(ret)
    ret = salt.access_to_asset_information()
    print(ret)