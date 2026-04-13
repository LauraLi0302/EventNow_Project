"""
URL configuration for eventnow project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from core.views import event_list  # 导入你刚才写的函数
from core.views import login_view
from core import views # 确保导入了 views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', event_list, name='event_list'), # 设置首页直接显示活动列表
    path('login/', login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]
