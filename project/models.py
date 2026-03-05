from django.db import models
from django.contrib.auth.models import AbstractUser
import random
import string


class User(AbstractUser):
    ROLE_CHOICES = [
        ('normal', '普通用户'),
        ('vip', 'VIP用户'),
        ('admin', '管理员'),
    ]
    
    email = models.EmailField(unique=True, verbose_name='邮箱')
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True, verbose_name='头像')
    bio = models.TextField(max_length=500, null=True, blank=True, verbose_name='个人简介')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='normal', verbose_name='用户角色')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    USERNAME_FIELD = 'email' 
    REQUIRED_FIELDS = ['username']

    class Meta:
        db_table = 'user'
        verbose_name = '用户'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.email
    
    @property
    def is_admin(self):
        return self.role == 'admin' or self.is_superuser
    
    @property
    def is_vip(self):
        return self.role == 'vip' or self.is_admin


class EmailVerificationCode(models.Model):
    TYPE_CHOICES = [
        ('login', '登录'),
        ('register', '注册'),
        ('reset_password', '重置密码'),
    ]
    
    email = models.EmailField(verbose_name='邮箱')
    code = models.CharField(max_length=6, verbose_name='验证码')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, verbose_name='验证码类型')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    expires_at = models.DateTimeField(verbose_name='过期时间')
    is_used = models.BooleanField(default=False, verbose_name='是否已使用')
    
    class Meta:
        db_table = 'email_verification_code'
        verbose_name = '邮箱验证码'
        verbose_name_plural = verbose_name
    
    def __str__(self):
        return f"{self.email} - {self.code}"
    
    @staticmethod
    def generate_code():
        return ''.join(random.choices(string.digits, k=6))
    
    def is_valid(self):
        from django.utils import timezone
        return not self.is_used and self.expires_at > timezone.now()
