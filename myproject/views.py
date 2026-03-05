from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from project.models import User, EmailVerificationCode
from rest_framework_simplejwt.tokens import RefreshToken
import json
import re


def home(request):
    return render(request, 'html/index.html')


def hello(request):
    from django.http import HttpResponse
    return HttpResponse('<h1>你好，Django！</h1><p><a href="/">返回首页</a></p>')


def login_page(request):
    return render(request, 'html/login.html')


def register_page(request):
    return render(request, 'html/register.html')


def profile_page(request):
    return render(request, 'html/profile.html')


@csrf_exempt
@require_http_methods(["POST"])
def api_login(request):
    try:
        data = json.loads(request.body)
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return JsonResponse({'error': '邮箱和密码不能为空'}, status=400)
        
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            login(request, user)
            refresh = RefreshToken.for_user(user)
            
            return JsonResponse({
                'message': '登录成功',
                'token': str(refresh.access_token),
                'refresh': str(refresh),
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'role': user.role
                }
            })
        else:
            return JsonResponse({'error': '邮箱或密码错误'}, status=401)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def api_register(request):
    try:
        data = json.loads(request.body)
        username = data.get('username')
        email = data.get('email')
        code = data.get('code')
        password = data.get('password')
        password_confirm = data.get('password_confirm')
        
        if not all([username, email, code, password, password_confirm]):
            return JsonResponse({'error': '所有字段都是必填的'}, status=400)
        
        verification = EmailVerificationCode.objects.filter(
            email=email,
            code=code,
            type='register',
            is_used=False
        ).order_by('-created_at').first()
        
        if not verification:
            return JsonResponse({'error': '验证码错误或已过期'}, status=400)
        
        if not verification.is_valid():
            return JsonResponse({'error': '验证码已过期，请重新获取'}, status=400)
        
        verification.is_used = True
        verification.save()
        
        if len(username) < 3:
            return JsonResponse({'error': '用户名至少需要3个字符'}, status=400)
        
        if len(password) < 8:
            return JsonResponse({'error': '密码至少需要8个字符'}, status=400)
        
        if password != password_confirm:
            return JsonResponse({'error': '两次密码不一致'}, status=400)
        
        if User.objects.filter(email=email).exists():
            return JsonResponse({'error': '邮箱已被注册'}, status=400)
        
        if User.objects.filter(username=username).exists():
            return JsonResponse({'error': '用户名已被使用'}, status=400)
        
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        
        return JsonResponse({
            'message': '注册成功',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            }
        }, status=201)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def api_logout(request):
    logout(request)
    return JsonResponse({'message': '登出成功'})


@csrf_exempt
@require_http_methods(["POST"])
def api_refresh_token(request):
    try:
        data = json.loads(request.body)
        refresh_token = data.get('refresh')
        
        if not refresh_token:
            return JsonResponse({'error': '请提供refresh token'}, status=400)
        
        refresh = RefreshToken(refresh_token)
        access_token = str(refresh.access_token)
        
        return JsonResponse({
            'token': access_token,
            'refresh': str(refresh)
        })
    except Exception as e:
        return JsonResponse({'error': f'Token无效或已过期: {str(e)}'}, status=401)


def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


@csrf_exempt
@require_http_methods(["POST"])
def send_verification_code(request):
    try:
        data = json.loads(request.body)
        email = data.get('email')
        code_type = data.get('type', 'login')
        
        if not email:
            return JsonResponse({'error': '请提供邮箱地址'}, status=400)
        
        if not is_valid_email(email):
            return JsonResponse({'error': '邮箱格式不正确'}, status=400)
        
        if code_type == 'register':
            if User.objects.filter(email=email).exists():
                return JsonResponse({'error': '该邮箱已被注册'}, status=400)
        elif code_type == 'login':
            if not User.objects.filter(email=email).exists():
                return JsonResponse({'error': '该邮箱未注册'}, status=400)
        elif code_type == 'reset_password':
            if not User.objects.filter(email=email).exists():
                return JsonResponse({'error': '该邮箱未注册'}, status=400)
        
        last_code = EmailVerificationCode.objects.filter(
            email=email, 
            type=code_type,
            created_at__gte=timezone.now() - timedelta(minutes=1)
        ).first()
        
        if last_code:
            return JsonResponse({'error': '验证码已发送，请1分钟后再试'}, status=400)
        
        code = EmailVerificationCode.generate_code()
        expires_at = timezone.now() + timedelta(minutes=5)
        
        EmailVerificationCode.objects.create(
            email=email,
            code=code,
            type=code_type,
            expires_at=expires_at
        )
        
        from django.conf import settings
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            send_mail(
                subject='验证码',
                message=f'您的验证码是：{code}，5分钟内有效。',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
            return JsonResponse({'message': '验证码已发送到您的邮箱'})
        except Exception as e:
            logger.error(f"Email sending failed: {str(e)}")
            if settings.DEBUG:
                return JsonResponse({'message': '验证码（调试模式）', 'code': code})
            return JsonResponse({'error': '邮件发送失败'}, status=500)
        
        return JsonResponse({'message': '验证码已发送到您的邮箱'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def login_with_code(request):
    try:
        data = json.loads(request.body)
        email = data.get('email')
        code = data.get('code')
        
        if not email or not code:
            return JsonResponse({'error': '邮箱和验证码不能为空'}, status=400)
        
        verification = EmailVerificationCode.objects.filter(
            email=email,
            code=code,
            type='login',
            is_used=False
        ).order_by('-created_at').first()
        
        if not verification:
            return JsonResponse({'error': '验证码错误或已过期'}, status=400)
        
        if not verification.is_valid():
            return JsonResponse({'error': '验证码已过期'}, status=400)
        
        verification.is_used = True
        verification.save()
        
        user = User.objects.get(email=email)
        login(request, user)
        refresh = RefreshToken.for_user(user)
        
        return JsonResponse({
            'message': '登录成功',
            'token': str(refresh.access_token),
            'refresh': str(refresh),
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role
            }
        })
    except User.DoesNotExist:
        return JsonResponse({'error': '用户不存在'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
