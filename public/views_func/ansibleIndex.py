from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
import json, datetime, redis, os, random, string, ast
from myCelery import ansiblePlayBook, ansibleExec, syncAnsibleResult
from tools.config import REDIS_ADDR, REDIS_PORT, REDIS_PD, ansible_result_redis_db
from public.models import *


class AnsibleOpt:
    @staticmethod
    def ansible_playbook(groupName, playbook, user=None, extra_vars={}, **kw):
        tid = "AnsibleApiPlaybook-%s-%s" % (''.join(random.sample(string.ascii_letters + string.digits, 8)),
                                            datetime.datetime.now().strftime("%Y%m%d-%H%M%S"))
        if not extra_vars.get('groupName'):
            extra_vars['groupName'] = groupName
        celeryTask = ansiblePlayBook.apply_async(
            (tid, playbook, extra_vars),
            link=syncAnsibleResult.s(tid=tid)
        )  # 保存 ansible 结果
        at = AnsibleTasks(
            AnsibleID=tid,
            CeleryID=celeryTask.task_id,
            TaskUser=user,
            GroupName=groupName,
            ExtraVars=extra_vars,
            playbook=playbook,
        )
        at.save()
        return {"playbook": playbook,
                "extra_vars": extra_vars,
                "ansible_id": tid,
                "celeryTask": celeryTask.task_id,
                "groupName": groupName,
                "pk": at.pk}

    @staticmethod
    def ansible_opt(groupName, tasks):
        tid = "AnsibleApiOpt-%s" % datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        celeryTask = ansibleExec.delay(tid, groupName, tasks)
        return {'tid': tid, 'celeryTask': celeryTask.task_id, "groupName": groupName}


# playbook 编辑和处理页面
class PlaybookView(LoginRequiredMixin, View):
    def get(self, request):
        ansisble_playbooks = AnsiblePlaybooks.objects.all()
        groups = Groups.objects.all()  # 获取组列表数据
        return render(request,
                      'ansible/playbookIndex.html',
                      {'ansisble_playbooks': ansisble_playbooks, 'groups': groups}  # 将组数据传到模板
                      )

    def post(self, request):
        print(request.POST)
        TaskUser = request.user
        groupName = request.POST.get('groupName', None)
        playbook = request.POST.get('playbook', None)
        extraVars = request.POST.get('extra_vars', '')
        print(extraVars)
        extra_vars = ast.literal_eval(extraVars) if extraVars else {}
        if not playbook:
            return
        data = AnsibleOpt.ansible_playbook(groupName, playbook, TaskUser, extra_vars)
        return redirect('/ansible/get_Ansible_Tasks_Detail/%s/' % data.get('pk'))
