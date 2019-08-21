import json
import subprocess
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator,PageNotAnInteger,EmptyPage
from django.db import transaction
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render

# Create your views here.

from cmdb.models import hostinfo, hostInstallog
from salt.salt_api import SaltAPI


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

def get_server_info():
    '''
    资产信息入库
    '''
    salt = SaltAPI(url='https://47.98.195.152:8001', user="saltapi", password="saltapi2019")
    # minions, minions_pre = salt.list_all_key()
    hostinfo_list = salt.access_to_asset_information()
    hostname_db_list = hostinfo.objects.all().values_list('hostname',flat=True)  #一次性获取数据库所有主机名
    min_dict = hostinfo_list[0]
    hostname_diff = list(set(hostname_db_list) ^ set(list(min_dict.keys())))
    hostinfo_list_to_insert = list()
    flag = 0       # 1 需要入库资产信息,0 不需要入库

    if len(hostname_diff) == 0:
        print("主机均已入库,不在重复采集资产信息")
    else:
        for hostname in hostname_diff:
            print(hostname)
           # hostname_lsit = list(min_info.keys())
           # print(hostname_lsit)
           # hostname_diff = list(set(hostname_db_list)^set(hostname_lsit))
           # print(hostname_diff)
           # hostname = list(min_info.keys())[0]
            flag = 1
            host_info = min_dict.get(hostname)
            ip = host_info['fqdn_ip4']
            if len(ip) == 1:
                ip = host_info['fqdn_ip4'][0]
            mem = int(host_info['mem_total']) // 1024 + 1
            cpu = host_info['cpu_model']
            cpus = host_info['num_cpus']
            os = host_info['oscodename']
            virtual1 = host_info['virtual']
            status = '在线'
            hostinfo_list_to_insert.append(hostinfo(hostname=hostname, ip=ip, mem=mem, cpu=cpu, cpus=cpus, os=os,
                                                    virtual1=virtual1, status=status))
    if flag == 1:
        try:
            with transaction.atomic():
                hostinfo.objects.bulk_create(hostinfo_list_to_insert)
        except Exception as e:
            print("数据库写入失败,错误信息：%s" % e)


@login_required
def server_info(request):
    '''
    资产主机详细信息
    :param request:
    :return:
    '''
    get_server_info()
    if request.method == "GET":
        page = request.GET.get("page")      # 接收网页中page值
        hostname = request.GET.get("hostname")
        if hostname:
            server_info_list = hostinfo.objects.filter(hostname__icontains=hostname)
        else:
            server_info_list = hostinfo.objects.all()

        server_info_obj = pages(server_info_list,page,8)
        return render(request,"member-list.html",{"server_info":server_info_obj})
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
        return render(request,"member-list.html",{"server_info":server_info_obj,
                                            "error_msg":error_msg})

def edit_server_info(request):
    if request.method == 'GET':
        return render(request,"member-edit.html")
@login_required
def add_server_info(request):
    '''
    添加资产后台逻辑
    :param request:
    :return:
    '''

    check_ip_inro = 0  # 检查主机是否存在，0不存在,1存在,2存在但是失败
    if request.method == 'GET':
        return render(request,"member-add.html")
    if request.method == 'POST':

        ip = request.POST.get('ip')  # 需要安装minion端的ip
        username = request.POST.get('username') # 需要安装minion端的账户
        password = request.POST.get('password') # 需要安装minion端的账户密码

        check_ip = hostInstallog.objects.filter(ip=ip).filter(results='ok')
        if check_ip.exists():
            check_ip_inro = 1
        check_ip = hostInstallog.objects.filter(ip=ip).filter(results='err')
        if check_ip.exists():
            check_ip_inro = 2
        '''
        check_ip_list = hostinfo.objects.values_list('ip',flat=True)
        for i in check_ip_list: # 将有多个ip的主机ip分开，自成一个列表供匹配检查主机是否已经存在
            if ',' in i:
                i_ip_list = i.replace('[','').replace(']','').split(',')
                if i in i_ip_list:  # 判断输入的ip是否在主机列表中
                    check_ip_inro = 1
                    break
        '''
        if check_ip_inro == 0 or check_ip_inro == 2:
      #  if ip not in check_ip_list and check_ip_inro == 0:
            try:
                roster = "echo '{ip}:' >> /etc/salt/roster &&" \
                    "echo '  host: {host}' >> /etc/salt/roster &&" \
                    "echo '  user: {username}' >> /etc/salt/roster &&" \
                    "echo '  passwd: {password}' >> /etc/salt/roster &&" \
                    "echo '  port: 22' >> /etc/salt/roster &&" \
                    "echo '  timeout: 10' >> /etc/salt/roster".format(ip=ip,
                                                                       host=ip,
                                                                       username=username,
                                                                       password=password)

                subprocess.run(roster, shell=True)  # 写入roster配置文件
                # 获取hostname
                resultgethostname = subprocess.run("salt-ssh -ir {ip} hostname".format(ip=ip),shell=True,
                                                   stdout=subprocess.PIPE,check=True,timeout=5)
                resultgethostname = resultgethostname.stdout.decode('utf8').split()[-1]
                
                subprocess.run("salt-ssh -ir {ip} 'echo {ip} {hostname} >> /etc/hosts'".format(ip=ip,hostname=resultgethostname),
                               shell=True)
                result = subprocess.run("salt-ssh -i {ip} state.sls minions.install".format(ip=ip),
                               shell=True,stdout=subprocess.PIPE,check=True)
                result = result.stdout.decode('utf8')
                re = 'ok'
            except Exception as e:
                subprocess.run("sed -i '/{ip}:/,+5d' /etc/salt/roster".format(ip=ip), shell=True)  # 回滚roster配置文件
                result = '''注意：无法连接至该主机，请检查ip账户密码是否错误!
                         具体信息：{ex}'''.format(ex=e)
                re = 'err'
            if check_ip_inro == 2:
                hl = hostInstallog.objects.get(ip=ip)
                hl.results = re
                hl.save()
            else:
                hostInstallog.objects.create(ip=ip, username=username, results=re)
        else:
            result = "提示：该主机已存在！"

        return render(request,"member-add.html",{"result":result})
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



