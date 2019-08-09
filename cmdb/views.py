from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.shortcuts import render

# Create your views here.

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
    return render(request,"member-list.html")