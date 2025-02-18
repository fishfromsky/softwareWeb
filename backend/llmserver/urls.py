from . import views
from django.urls import re_path as url

urlpatterns = [
    url('getmenu', views.getMenuConfig),   # 获取侧边栏
    url('getname', views.getNameConfig),   # 获取平台名称
    url('getpageinfo', views.getPageInfo),   # 获取页面详细代码信息
]

