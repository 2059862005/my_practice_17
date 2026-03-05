# Django REST Framework JWT

基于 Django REST Framework 和 JWT 的用户认证系统

## 功能特点

- 用户注册/登录
- 邮箱验证码验证
- JWT Token 认证
- 三级用户权限管理（普通用户、VIP、管理员）
- RESTful API

## 技术栈

- Django 4.2+
- Django REST Framework
- Django REST Framework Simple JWT
- MySQL

## 快速开始

### 1. 克隆项目
```bash
git clone https://github.com/2059862005/my_practice_17.git
cd my_practice_17
```

### 2. 创建虚拟环境
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### 3. 安装依赖
```bash
pip install django djangorestframework djangorestframework-simplejwt djoser Pillow
```

### 4. 配置数据库
修改 `myproject/settings.py` 中的数据库配置

### 5. 运行迁移
```bash
python manage.py migrate
```

### 6. 启动服务
```bash
python manage.py runserver
```

## API 端点

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/auth/login/ | 邮箱密码登录 |
| POST | /api/auth/login_with_code/ | 验证码登录 |
| POST | /api/auth/register/ | 用户注册 |
| POST | /api/auth/send_code/ | 发送验证码 |
| POST | /api/auth/refresh/ | 刷新 Token |
| GET | /api/users/me/ | 当前用户信息 |

## License

MIT
