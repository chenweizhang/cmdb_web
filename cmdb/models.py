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

class hostInstallog(models.Model):

    ip = models.CharField(u'部署IP',max_length=50,primary_key=True)
    username = models.CharField(u'登录账户',max_length=255)
    results = models.CharField(u'结果',max_length=20)
    create_date = models.DateField(u'部署时间',auto_now_add=True)
    class Meta:
        db_table = 't_host_install_log'


class ac_base(models.Model):
    hostname = models.CharField(u'主机名',max_length=255)
    ip = models.CharField(u'ip地址',max_length=100)
    capturetime = models.DateTimeField('u当前时间')
    cpu = models.TextField()
    men = models.CharField(u'内存',max_length=100)
    swap = models.CharField(max_length=20)
    osname = models.TextField(u'系统版本信息')
    kernel = models.CharField(u'内核版本信息',max_length=255)
    uptime = models.CharField(u'运行时间',max_length=255)

    class Meta:
        db_table = 'ac_base'


class ac_cpu(models.Model):
    hostname = models.CharField(u'主机名', max_length=255)
    ip = models.CharField(u'ip地址', max_length=100)
    capturetime = models.DateTimeField('u当前时间')
    user_cpu = models.FloatField('CPU处在用户模式下的时间百分比')
    nice_cpu = models.FloatField('CPU处在带NICE值的用户模式下的时间百分比')
    system_cpu = models.FloatField('CPU处在系统模式下的时间百分比')
    iowait_cpu = models.FloatField('CPU等待输入输出完成时间的百分比')
    steal_cpu = models.FloatField('管理程序维护另一个虚拟处理器时，虚拟CPU的无意识等待时间百分比')
    idle_cpu = models.FloatField('CPU空闲时间百分比')
    usage_cpu = models.FloatField('CPU工作时间百分比')
    load_avg = models.FloatField('系统负载')
    class Meta:
        db_table = 'ac_cpu'

class ac_mem(models.Model):
    hostname = models.CharField(u'主机名', max_length=255)
    ip = models.CharField(u'ip地址', max_length=100)
    capturetime = models.DateTimeField('u当前时间')
    mem_total = models.IntegerField('内存总数')
    mem_used = models.IntegerField('已使用内存')
    mem_free = models.IntegerField('剩余内存')
    swap_total = models.IntegerField()
    swap_used = models.IntegerField()
    swap_free = models.IntegerField()
    mem_percent = models.FloatField('使用率')
    class Meta:
        db_table = 'ac_mem'

class ac_disk(models.Model):
    hostname = models.CharField(u'主机名', max_length=255)
    ip = models.CharField(u'ip地址', max_length=100)
    capturetime = models.DateTimeField('u当前时间')
    disk = models.TextField('磁盘使用情况')
    disk_io = models.TextField('磁盘IO')
    class Meta:
        db_table = 'ac_disk'

class ac_net(models.Model):
    hostname = models.CharField(u'主机名', max_length=255)
    ip = models.CharField(u'ip地址', max_length=100)
    capturetime = models.DateTimeField('u当前时间')
    interface = models.TextField('网卡信息')
    traffic_in = models.IntegerField('接收')
    traffic_out = models.IntegerField('发送')
    sockets = models.TextField('sockets连接信息')
    class Meta:
        db_table = 'ac_net'
