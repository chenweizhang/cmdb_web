#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File  : urls.py
# Author: chenweizhang
# Date  : 2019/8/9
from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from cmdb.views import server_info, del_server_info, query_server_info

urlpatterns = [
    path('server_info/',server_info,name='server_info'),
    path('del_server_info/',del_server_info,name='del_server_info'),
    path('query_server_info/',query_server_info,name='query_server_info'),
]