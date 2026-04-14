from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .models import Event
from django.contrib.auth import logout
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import User, Event, Registration, Session
from django.core.paginator import Paginator
from .forms import EventForm, SessionForm
from datetime import datetime
from django.db.models import Count, Q
from django.http import JsonResponse
import time



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

# --- 项目管理 (管理员 & 组织者) ---
@login_required
def event_management(request):
    user = request.user
    
    # 权限隔离逻辑
    if user.role == 'admin':
        # 管理员看全部
        event_list = Event.objects.all().order_by('-created_at')
    elif user.role == 'organiser':
        # 组织者只看自己创建的
        event_list = Event.objects.filter(organiser=user).order_by('-created_at')
    else:
        # 参与者无权访问管理端
        return redirect('event_display')

    # 分页：每页展示 10 个项目
    paginator = Paginator(event_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'event_management.html', {'page_obj': page_obj})

# --- 活动展示 (所有登录用户) ---
@login_required
def event_display(request):
    # 基础筛选：只展示未归档的活动
    event_list = Event.objects.filter(is_archived=False).order_by('date')

    # 时间筛选逻辑
    selected_date = request.GET.get('date')
    if selected_date:
        event_list = event_list.filter(date=selected_date)

    # 分页：每页展示 6 个（网格展示通常数量少点好看）
    paginator = Paginator(event_list, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'event_display.html', {
        'page_obj': page_obj,
        'selected_date': selected_date
    })

@login_required
def event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    # 获取该活动下的所有场次 (Session)
    sessions = event.sessions.filter(is_archived=False)
    return render(request, 'event_detail.html', {'event': event, 'sessions': sessions
    })

@login_required
def create_event(request):
    if request.user.role not in ['admin', 'organiser']:
        return redirect('event_display')
    
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.organiser = request.user  # 绑定当前用户
            event.save()
            # 创建成功后，跳转到添加时间的页面，带上 event_id
            return redirect('add_sessions', event_id=event.id)
    else:
        form = EventForm()
    return render(request, 'create_event.html', {'form': form})

@login_required
def add_sessions(request, event_id):
    # 1. 获取当前正在为其添加场次的活动对象
    event = get_object_or_404(Event, id=event_id)
    
    if request.method == 'POST':
        form = SessionForm(request.POST)
        if form.is_valid():
            session = form.save(commit=False)
            session.event = event
            
            # 2. 核心修改：获取该活动在第一步设置的日期 (YYYY-MM-DD)
            event_date = event.date  
            
            # 3. 获取表单传来的时间字符串 (HH:MM)
            start_t = request.POST.get('start_time')
            end_t = request.POST.get('end_time')
            
            # 4. 将“活动日期”和“选择的时间”合成为完整的 datetime 对象存入数据库
            try:
                session.start_time = datetime.combine(event_date, datetime.strptime(start_t, '%H:%M').time())
                session.end_time = datetime.combine(event_date, datetime.strptime(end_t, '%H:%M').time())
                session.save()
            except ValueError:
                # 防止时间格式抓取失败的容错处理
                return render(request, 'add_sessions.html', {'form': form, 'event': event, 'error': 'Invalid time format'})
            
            if 'another' in request.POST:
                return redirect('add_sessions', event_id=event.id)
            return redirect('event_management')
    else:
        form = SessionForm()
    
    return render(request, 'add_sessions.html', {'form': form, 'event': event})

def event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    
    # 获取该活动的所有场次，并预计算每个场次已有的 'active' 状态报名人数
    # 使用 annotate 可以直接在数据库层面计算，效率更高
    sessions = event.sessions.annotate(
        current_registrations=Count(
            'registrations', 
            filter=Q(registrations__status='active')
        )
    ).order_by('start_time')
    
    # 为每个 session 对象动态添加剩余名额属性
    for session in sessions:
        session.remaining_slots = session.capacity - session.current_registrations

    context = {
        'event': event,
        'sessions': sessions,
    }
    return render(request, 'event_detail.html', context)

@login_required
def ai_assistant(request):
    return render(request, 'ai_assistant.html')

