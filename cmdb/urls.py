#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File  : urls.py
# Author: chenweizhang
# Date  : 2019/8/9
from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from cmdb.views import server_info

urlpatterns = [
    path('server_info/',server_info,name='server_info'),

]