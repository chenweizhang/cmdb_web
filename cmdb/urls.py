#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File  : urls.py
# Author: chenweizhang
# Date  : 2019/8/9
from django.urls import path
from cmdb.views import server_info, del_server_info, edit_server_info, add_server_info, approve

urlpatterns = [
    path('server_info/',server_info,name='server_info'),
    path('server_info/edit',edit_server_info,name='edit'),
    path('add_server_info/',add_server_info,name='add'),
    path('del_server_info/',del_server_info,name='del_server_info'),
    path('approve_server',approve,name='approve')
    # path('query_server_info/',query_server_info,name='query_server_info'),
]