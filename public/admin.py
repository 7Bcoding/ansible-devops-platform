from django.contrib import admin
from public.models import *
# inventory 对应文件
from tools.config import inventory


@admin.register(AnsiblePlaybooks)
class AnsiblePlaybooksAdmin(admin.ModelAdmin):
    list_display = ['nickName', 'playbook']


@admin.register(AnsibleTasks)  #
class AnsibleTasksAdmin(admin.ModelAdmin):
    list_display = [
        'AnsibleID',
        'CeleryID',
        'GroupName',
        'playbook',
        'ExtraVars',
        'AnsibleResult',
        'CeleryResult',
        'CreateTime'
    ]


# 主机列表修改内容
@admin.register(Hosts)
class HostsAdmin(admin.ModelAdmin):
    list_display = ['hostname', 'hostip']


# 组列表相关内容
@admin.register(Groups)
class GroupsAdmin(admin.ModelAdmin):
    list_display = ['groupName']
    filter_horizontal = ('hostList',)

    # 重写 save_related 函数
    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        # 在 admin 平台保存完对应关系之后，获取所有对应关系，保存到主机清单中
        if change:
            data = "\n"
            gs = Groups.objects.all()
            for g in gs:
                data += '[%s]\n' % g.groupName
                data += '\n'.join([i[0] for i in g.hostList.values_list('hostip')])
            with open(inventory, 'w') as f:
                f.write(data)
