from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator,PageNotAnInteger,EmptyPage
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.shortcuts import render

# Create your views here.
from cmdb import models


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

def server_info(request):
    '''
    资产主机详细信息
    :param request:
    :return:
    '''
    if request.method == "GET":
        server_info_list = models.hostinfo.objects.all()
        paginator = Paginator(server_info_list,8)       # 实例化结果集,每页八条数据
        page = request.GET.get("page")      # 接收网页中page值
        try:
            # 根据page值返回相应结果
            server_info_obj = paginator.page(page)
        except PageNotAnInteger:    # 不存在的页码，返回第一页
            server_info_obj = paginator.page(1)
        except EmptyPage:
            server_info_obj = paginator.page(paginator.num_pages)
        return render(request,"member-list.html",{"server_info_list":server_info_obj})

