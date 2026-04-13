from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

# 1. 用户表 (已存在的)
class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Administrator'),
        ('organiser', 'Organiser'),
        ('attendee', 'Attendee'),
    )
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='attendee')
    is_archived = models.BooleanField(default=False)

    def __str__(self):
        return self.username

# 2. SaaS 订阅表 (2.3 归档功能核心)
class Subscription(models.Model):
    organiser = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    status = models.CharField(max_length=50, default='active')
    is_archived = models.BooleanField(default=False)
    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField(null=True, blank=True)

# 3. 活动表 (支持 AI 标记和无障碍设计)
class Event(models.Model):
    organiser = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='events')
    title = models.CharField(max_length=255)
    description = models.TextField()
    image_url = models.CharField(max_length=255, blank=True)
    image_alt_text = models.CharField(max_length=255, blank=True) # Accessibility
    location = models.CharField(max_length=255)
    date = models.DateField()
    is_archived = models.BooleanField(default=False)
    is_ai_assisted = models.BooleanField(default=False) # AI 声明
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

# 4. 场次表 (3.1 多场次调度)
class Session(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='sessions')
    title = models.CharField(max_length=255)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    capacity = models.IntegerField() # 3.3 容量追踪
    is_archived = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.event.title} - {self.title}"

# 5. 报名表 (3.3 实时计算)
class Registration(models.Model):
    attendee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='registrations')
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='registrations')
    status = models.CharField(max_length=50, default='active')
    registered_at = models.DateTimeField(auto_now_add=True)