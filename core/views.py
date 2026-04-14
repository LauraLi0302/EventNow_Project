from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .models import Event
from django.contrib.auth import logout


# 登录
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('event_list') # 登录成功后跳转到你的 Dashboard
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


@login_required
def event_list(request):
    user = request.user
    
    # 分权限逻辑
    if user.is_superuser or (hasattr(user, 'role') and user.role == 'admin'):
        events = Event.objects.all()
    elif hasattr(user, 'role') and user.role == 'organiser':
        # 只看自己名下的活动
        events = Event.objects.filter(organiser=user)
    else:
        events = Event.objects.all() 

    total_events = events.count()
    
    return render(request, 'event_list.html', {
        'events': events,
        'total_events': total_events,
        'username': user.username  # 把名字也传过去
    })

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def profile_settings(request):
    user = request.user
    # 这里我们直接把 user 对象传给前端展示信息
    return render(request, 'profile_settings.html', {
        'user': user
    })

@login_required
def user_management(request):
    # 权限检查：只有超级管理员能进
    if not request.user.is_superuser:
        return redirect('event_list')

    # 获取筛选参数：role (all, organiser, attendee)
    role_filter = request.GET.get('role', 'all')
    
    # 基础查询：按注册时间顺序排列 (date_joined)
    users = User.objects.all().order_by('date_joined')

    # 筛选逻辑 (假设你在 User Model 或 Profile 里有 role 字段)
    if role_filter == 'organiser':
        users = users.filter(role='organiser')
    elif role_filter == 'attendee':
        users = users.filter(role='attendee')

    return render(request, 'user_management.html', {
        'users': users,
        'role_filter': role_filter
    })

