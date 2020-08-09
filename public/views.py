# 导入必须的模块
from django.http import HttpResponse
import redis

html = '''<!DOCTYPE html>
<html lang="zh-CN">
  <head><link href="https://cdn.jsdelivr.net/npm/bootstrap@3.3.7/dist/css/bootstrap.min.css" rel="stylesheet"></head>
  <div class="col-md-3"></div><div class="col-md-6">%s</div><div class="col-md-3"></div>
'''

def redis_info(request):
    r = redis.Redis(host="127.0.0.1", port=6379)
    data = r.info()
    msg = ""
    for i,j in data.items():
        msg += '<tr><td >%s</td><td>%s</td></tr>' % (i, j)
    table ='<div><table class="table table-bordered">%s</table></div>' % msg
    return HttpResponse(html % table)

from django.shortcuts import render
from django.http import JsonResponse

# 函数 index 至少需要传入一个参数， 返回时 render 需要传入三个参数，第一个为函数传入值，第二个为 html 模板文件，第三个为字典数据，会在模板中使用
def index(request):
    return render(request, 'public_base.html', {})
# JsonResponse 会返回一个 json 字符串
def jsdata(request):
    return JsonResponse({'msg': 'this is a JsonResponse return'})

from django.views.generic import ListView
from django.views.generic import DetailView
from public.models import AnsibleTasks
# 我们继承 ListView 类，指定 model 为 AnsibleTasks (models 文件中的 class 数据对象)，这个会查询 AnsibleTasks 所有数据，并将数据与模板文件 templates/public/ansibletasks_list.html 匹配返回 http 请求
class AnsibleTaskList(ListView):
    model = AnsibleTasks
# 继承 DetailView 类，指定 model 为 AnsibleTasks
class AnsibleTaskDetail(DetailView):
    model = AnsibleTasks

# 调用 django 的权限管理函数，会在模板目录下 403.html 作为模板返回
from django.core.exceptions import PermissionDenied
# 导入日志相关模块
import logging
logger = logging.getLogger('ansible.ui')
def dashboard(request):
    # 记录日志
    logger.warning('%s 访问 dashboard 页面，权限拒绝' % request.user)
    # 返回一个 403 页面
    raise PermissionDenied