from django.db import models
from django.db import models
from django.contrib.auth.models import User


# 存储 playbook 的名称和文件路径
class AnsiblePlaybooks(models.Model):
    nickName = models.CharField(max_length=80,null=True,blank=True)
    playbook = models.CharField(max_length=80,unique=True, null=True,blank=False)

    def __str__(self):
        return self.playbook


# Ansible任务类
class AnsibleTasks(models.Model):
    AnsibleID = models.CharField(max_length=80,unique=True, null=True,blank=True)
    CeleryID = models.CharField(max_length=80,unique=True, null=True,blank=True)
    TaskUser = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    GroupName = models.CharField(max_length=80, null=True,blank=True)
    playbook = models.CharField(max_length=80, null=True,blank=True)
    ExtraVars = models.TextField(blank=True, null=True)
    AnsibleResult = models.TextField(blank=True)
    CeleryResult = models.TextField(blank=True)
    CreateTime = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.AnsibleID


# 主机类
class Hosts(models.Model):
    hostname = models.CharField(max_length=80,null=True,blank=True)
    hostip = models.CharField(max_length=80,unique=True)

    def __str__(self):
        return self.hostip


# 主机组类
class Groups(models.Model):
    groupName = models.CharField(max_length=80,unique=True)
    hostList = models.ManyToManyField(Hosts)

    def __str__(self):
        return self.groupName