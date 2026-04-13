from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Event, Session, Subscription, Registration


class CustomUserAdmin(UserAdmin):
    # 在后台的用户编辑页面增加 Role 和 is_archived 字段
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('role', 'is_archived')}),
    )
    # 在用户列表页直接显示 Role
    list_display = ['username', 'email', 'role', 'is_staff']

# 注册所有模型，在 /admin 页面就能看到了
admin.site.register(User)
admin.site.register(Event)
admin.site.register(Session)
admin.site.register(Subscription)
admin.site.register(Registration)