from django.contrib.auth.models import User
from django.db import models

# Create your models here.


class userinfo(models.Model):
    # 用户表

    user = models.OneToOneField(User,unique=True,on_delete=models.CASCADE,verbose_name=('用户'))
    phone = models.CharField(u"手机",max_length=20)
    user_role = models.CharField(u'角色',max_length=40)

    class Meta:
        db_table = "t_user_info"

class cabinet(models.Model):
    name = models.CharField(u'名称',max_length=30)
    power =  models.CharField(u'权限',max_length=20)
    class Meta:
        db_table = "t_cabinet"

class hostinfo(models.Model):
    # 主机信息表

    hostname = models.CharField(u'主机名', max_length=255)
    ip = models.CharField(u'IP地址', max_length=50)
    mem = models.IntegerField(u'内存')
    cpu = models.CharField(u'cpu', max_length=255)
    cpus = models.IntegerField(u'cpus')
    os = models.CharField(u'os', max_length=255)
    virtual1 = models.CharField(u'virtual', max_length=255)
    status = models.CharField(u'状态', max_length=50)

    def __str__(self):
        return self.hostname
    class Meta:
        db_table = "t_host_info"

class product(models.Model):
    #应用表
    service_name = models.CharField(u'服务名称',max_length=20)
    pid = models.IntegerField(u'pid')
    module_letter = models.CharField(max_length=10)
    class Meta:
        db_table = "product"

class monitorMemory(models.Model):
    hostid = models.IntegerField(u'监控主机ID')
    avai = models.CharField(u'空闲内存',max_length=20)
    total = models.CharField(u'总内存',max_length=20)
    ratio = models.CharField(u'使用率',max_length=20)
    time = models.DateTimeField(u'时间',auto_now_add=True)