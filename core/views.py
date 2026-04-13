from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .models import Event

# --- 这是你新加的：处理登录的逻辑 ---
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
    # 暂时不管角色，直接拿所有数据，看能不能跑通
    events = Event.objects.all()
    total_events = events.count()
    
    return render(request, 'event_list.html', {
        'events': events,
        'total_events': total_events
    })

