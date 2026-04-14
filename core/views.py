from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .models import Event
from django.contrib.auth import logout
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import User, Event, Registration

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
    # 1. 严格权限检查：只有角色为 admin 的用户可以进入
    if request.user.role != 'admin':
        return redirect('event_list')

    # 2. 获取筛选参数
    role_filter = request.GET.get('role', 'all')
    # 从 URL 获取 archived 参数，1 代表看归档，0 代表看活跃
    show_archived = request.GET.get('archived', '0') == '1'

    # 3. 核心查询：根据归档状态过滤，并按加入时间排序,排除管理员
    users = User.objects.filter(is_archived=show_archived).exclude(id=request.user.id).order_by('date_joined')

    # 4. 身份筛选逻辑
    if role_filter == 'organiser':
        users = users.filter(role='organiser')
    elif role_filter == 'attendee':
        users = users.filter(role='attendee')

    # 5. 返回渲染，确保变量名无误
    return render(request, 'user_management.html', {
        'users': users,
        'role_filter': role_filter,
        'show_archived': show_archived  # 用于前端切换“查看活跃/查看归档”
    })

# 归档功能：不删除数据，只是把标志位设为 True
@login_required
def archive_user(request, user_id):
    if request.user.role == 'admin':
        target_user = get_object_or_404(User, id=user_id)
        # 记录下操作前的状态，用于决定跳回哪里
        was_archived = target_user.is_archived
        
        # 执行翻转逻辑
        target_user.is_archived = not was_archived
        target_user.is_active = was_archived  # 恢复后设为 active，归档后设为非 active
        target_user.save()
        
        # 核心修改：如果你是在回收站点击的“恢复”，就跳回回收站 (archived=1)
        # 如果你是在活跃列表点击的“归档”，就跳回活跃列表 (archived=0)
        if was_archived:
            return redirect('/users/?archived=1')
        else:
            return redirect('/users/?archived=0')
    return redirect('user_management')

# 查看历史活动
@login_required
def user_history(request, user_id):
    if request.user.role != 'admin':
        return redirect('event_list')
        
    target_user = get_object_or_404(User, id=user_id)
    
    if target_user.role == 'organiser':
        # 组织者：看他创建的 Events
        history_data = Event.objects.filter(organiser=target_user)
    else:
        # 参与者：通过 Registration -> Session -> Event 找到他参加的活动
        # 使用 select_related 优化查询
        history_data = Registration.objects.filter(attendee=target_user).select_related('session__event')

    return render(request, 'user_history.html', {
        'target_user': target_user,
        'history_data': history_data
    })