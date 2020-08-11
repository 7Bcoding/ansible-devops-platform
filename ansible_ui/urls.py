# url 配置入口 ansible_ui/urls.py，内容可直接覆盖

from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import RedirectView
from public.views_func.account import myLogin, myLogout

urlpatterns = [
    # 所有 admin 开头的请求，交给 admin.site.urls 处理，django 自带系统，无需修改
    path('admin/', admin.site.urls),
    # 我们将所有以 /ansible/ 开头的 uri 交给 public.urls 处理，对应了 public/urls.py 文件
    path('ansible/', include('public.urls'),),
    # 添加登陆相关映射
    path('account/login', myLogin),
    path('account/logout', myLogout),

    # 将首页请求跳转到 /ansible/
    path('', RedirectView.as_view(url='/ansible/')),
]