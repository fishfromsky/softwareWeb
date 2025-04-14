from . import views
from django.urls import re_path as url

urlpatterns = [
    url('login', views.login),  # 登录
    url('register', views.register),  # 注册
    url('getuserrecord', views.getUserAllRecord),  # 获取用户软著生成记录
    url('deleterecord', views.deleteUserRecord),  # 删除用户软著记录
    url('getthreadstatus', views.check_thread_pool_available),  # 获取线程池状态

    url('pdfdownload', views.pdfDownload),  # 获取PDF文件
    url('txtdownload', views.txtDownload),  # 获取txt文件
    url('worddownload', views.wordDownload),  # 获取word文档
    url('docxdownload', views.registerDownloadDocx),  # 获取软著注册表
    url('generateRegistration', views.generateRegistration),  # 生成软著注册表

    url('getmenu', views.getMenuConfig),   # 获取侧边栏
    url('getname', views.getNameConfig),   # 获取平台名称
    url('getpageinfo', views.getPageInfo),   # 获取页面详细代码信息
    url('getpagemain', views.getPageMain),  # 获取登录界面信息
    url('getpagevice', views.getPageVice),  # 获取注册页面信息
    url('runprogram', views.startProgram),  # 开始运行程序

    url('getuserinfo', views.getuserinfo),  # 获取用户个人信息
    url('edituserinfo', views.editUserInfo)   # 修改用户个人信息
]

