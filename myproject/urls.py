from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from project.views import UserViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('hello/', views.hello, name='hello'),
    path('login/', views.login_page, name='login'),
    path('register/', views.register_page, name='register'),
    path('profile/', views.profile_page, name='profile'),
    path('api/auth/login/', views.api_login, name='api_login'),
    path('api/auth/register/', views.api_register, name='api_register'),
    path('api/auth/logout/', views.api_logout, name='api_logout'),
    path('api/auth/refresh/', views.api_refresh_token, name='api_refresh_token'),
    path('api/auth/send_code/', views.send_verification_code, name='send_verification_code'),
    path('api/auth/login_with_code/', views.login_with_code, name='login_with_code'),
    path('api/', include(router.urls)),
]
