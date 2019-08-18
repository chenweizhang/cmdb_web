import json

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator,PageNotAnInteger,EmptyPage
from django.db import transaction
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render

# Create your views here.
from cmdb import models
from cmdb.models import hostinfo


def validate_logon(request):
    # 登录
    if request.method == "POST":

        user = authenticate(username=request.POST.get("username"),
                            password=request.POST.get("password"))
        if user is not None:

            login(request,user)
            return HttpResponse("ok")

        else:
            return HttpResponse()
    return render(request,'login.html')

def acc_logout(request):
    # 退出登录
    logout(request)
    return HttpResponseRedirect("/login")

@login_required
def index(request):
    return render(request, 'index.html')

def pages(obj,page_value,value):

    paginator = Paginator(obj, value)  # 实例化结果集,每页八条数据

    try:
        # 根据page值返回相应结果
        reuslt_obj = paginator.page(page_value)
    except PageNotAnInteger:  # 不存在的页码，返回第一页
        reuslt_obj = paginator.page(1)
    except EmptyPage:
        reuslt_obj = paginator.page(paginator.num_pages)
    return reuslt_obj
def server_info(request):
    '''
    资产主机详细信息
    :param request:
    :return:
    '''
    if request.method == "GET":
        page = request.GET.get("page")      # 接收网页中page值
        hostname = request.GET.get("hostname")
        if hostname:
            server_info_list = hostinfo.objects.filter(hostname__icontains=hostname)
        else:
            server_info_list = models.hostinfo.objects.all()

        server_info_obj = pages(server_info_list,page,8)
        return render(request,"member-list.html",{"server_info_list":server_info_obj})
def query_server_info(request):

    '''
    搜索，弃用，以合并至server_info
    :param request:
    :return:
    '''
    if request.method == "GET":
        error_msg = ''
        hostname = request.GET.get("hostname")
        page = request.GET.get("page")

        if hostname:
            server_info_list = hostinfo.objects.filter(hostname__icontains=hostname)

        else:
            server_info_list = []
            error_msg = '请输入关键字'
            print(error_msg)
        # return HttpResponse('ok')
        server_info_obj = pages(server_info_list, page, 8)
        return render(request,"member-list.html",{"server_info_list":server_info_obj,
                                            "error_msg":error_msg})

def edit_server_info(request):
    if request.method == 'GET':
        return render(request,"member-edit.html")

def add_server_info(request):

    check_ip_inro = 0  # 检查主机是否存在，0不存在,1存在
    if request.method == 'GET':
        return render(request,"member-add.html")
    if request.method == 'POST':

        ip = request.POST.get('ip')  # 需要安装minion端的ip
        username = request.POST.get('username') # 需要安装minion端的账户
        password = request.POST.get('password') # 需要安装minion端的账户密码

        if len(hostinfo.objects.filter(ip=ip)) > 0:
            check_ip_inro = 1
        else:
            check_ip_list = hostinfo.objects.values_list('ip',flat=True)
            for i in check_ip_list: # 将有多个ip的主机ip分开，自成一个列表供匹配检查主机是否已经存在
                if ',' in i:
                    i_ip_list = i.replace('[','').replace(']','').split(',')
                    if i in i_ip_list:  # 判断输入的ip是否在主机列表中
                        check_ip_inro = 1
                        break
                elif ip == i:
                    check_ip_inro = 1
                    break
            
def del_server_info(request):

    if request.method == "POST":
        r = json.loads(request.body)
        host_id = r.get("hostid")
        if host_id is not None:

            if isinstance(host_id,list):
                host_id = ','.join(host_id)

                try:
                    with transaction.atomic():
                         hostinfo.objects.extra(where=["id IN (%s)" % host_id]).delete()
                    code = 'ok'
                except Exception as e:
                    print(e)
                    code = 'err'
            else:
                try:
                    hostinfo.objects.filter(id=host_id).delete()
                    code = "ok"
                except Exception as e:
                    print(e)
                    code = "err"
        else:
            code = "err"
        return HttpResponse(code)
