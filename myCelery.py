#!/usr/bin/env python
# coding: utf8
"Celery 异步操作Ansible 服务端"
import json
import time
from celery import Celery
from ansibleApi import *
from tools.config import BACKEND, BROKER, REDIS_ADDR, REDIS_PORT, REDIS_PD, ansible_result_redis_db
from celery.app.task import Task
from celery.utils.log import get_task_logger
from celery.result import AsyncResult
import os, sys
import django
from public.models import *

path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, path)
os.environ['DJANGO_SETTINGS_MODULE'] = 'ansible_ui.settings'
django.setup()

if os.environ.get("PYTHONOPTIMIZE", ""):
    print("开始启动")
else:
    print("\33[31m环境变量问题，Celery Client启动后无法正常执行Ansible任务，\n请设置export PYTHONOPTIMIZE=1；\n\33[32mDjango环境请忽略\33[0m")

celery_logger = get_task_logger(__name__)
# 创建Celery应用
appCelery = Celery("tasks", broker=BROKER, backend=BACKEND, )
sources = "scripts/inventory"


class MyTask(Task):  # 回调父类 on_success 和 on_failure 方法
    def on_success(self, retval, task_id, args, kwargs):
        print("执行成功 notice from on_success")
        return super(MyTask, self).on_success(retval, task_id, args, kwargs)

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        r = redis.Redis(host=REDIS_ADDR, password=REDIS_PD, port=REDIS_PORT, db=ansible_result_redis_db)
        a = redis.Redis(host=REDIS_ADDR, password=REDIS_PD, port=REDIS_PORT, db=4)
        tid = args[0]
        # Redis的lrange操作取出任务id对应Celery结果
        rlist = r.lrange(tid, 0, -1)
        try:
            # 任务结果从Redis中获取，并存储至MySQL
            at = AnsibleTasks.objects.filter(AnsibleID=tid)[0]
            at.AnsibleResult = json.dumps([json.loads(i.decode()) for i in rlist])
            ct = a.get('celery-task-meta-%s' % at.CeleryID).decode()
            at.CeleryResult = ct
            at.save()
        except:
            pass
        return super(MyTask, self).on_failure(exc, task_id, args, kwargs, einfo)


@appCelery.task
def ansibleExec(tid, groupname, tasks=[], extra_vars={}):
    # 调用重写的Ansbile-Api
    AnsibleApi(tid, groupname, tasks, sources, extra_vars)
    return 'success'


@appCelery.task(bind=True, base=MyTask)  # 继承至MyTask，为Celery任务函数之一，处理Playbook的执行
def ansiblePlayBook(self, tid, playbook, extra_vars, **kw):
    psources = kw.get('sources') or extra_vars.get('sources') or sources
    # 调用重写的PlaybookApi
    AnsiblePlaybookApi(tid, ["playbooks/%s" % playbook], psources, extra_vars)
    return 'success'


@appCelery.task(bind=True)
def syncAnsibleResult(self, ret, *a, **kw):  # 执行结束，结果同步至db
    c = AsyncResult(self.request.get('parent_id'))
    celery_logger.info(c.result)
    tid = kw.get('tid', None)
    if tid:
        r = redis.Redis(host=REDIS_ADDR, password=REDIS_PD, port=REDIS_PORT, db=ansible_result_redis_db)
        a = redis.Redis(host=REDIS_ADDR, password=REDIS_PD, port=REDIS_PORT, db=4)
        rlist = r.lrange(tid, 0, -1)
        at = AnsibleTasks.objects.filter(AnsibleID=tid)[0]
        at.AnsibleResult = json.dumps([json.loads(i.decode()) for i in rlist])
        ct = a.get('celery-task-meta-%s' % at.CeleryID).decode()
        at.CeleryResult = ct
        at.save()
        print("同步结果至db: syncAnsibleResult !!!!!: parent_id: %s" % self.request.get('parent_id'), a, kw)
    else:
        pass


if __name__ == "__main__":
    appCelery.worker_main()
