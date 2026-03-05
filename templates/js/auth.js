const Auth = {
    tokenKey: 'auth_token',
    userKey: 'auth_user',
    refreshKey: 'auth_refresh',
    
    getToken() {
        return localStorage.getItem(this.tokenKey);
    },
    
    setToken(token) {
        localStorage.setItem(this.tokenKey, token);
    },
    
    getRefresh() {
        return localStorage.getItem(this.refreshKey);
    },
    
    setRefresh(refresh) {
        localStorage.setItem(this.refreshKey, refresh);
    },
    
    removeToken() {
        localStorage.removeItem(this.tokenKey);
        localStorage.removeItem(this.refreshKey);
    },
    
    getUser() {
        const user = localStorage.getItem(this.userKey);
        return user ? JSON.parse(user) : null;
    },
    
    setUser(user) {
        localStorage.setItem(this.userKey, JSON.stringify(user));
    },
    
    removeUser() {
        localStorage.removeItem(this.userKey);
    },
    
    isLoggedIn() {
        return !!this.getToken();
    },
    
    logout() {
        this.removeToken();
        this.removeUser();
        window.location.href = '/';
    }
};

function getCSRFToken() {
    const name = 'csrftoken';
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function showError(message) {
    const errorDiv = document.getElementById('error');
    if (errorDiv) {
        errorDiv.textContent = message;
        errorDiv.style.display = 'block';
        setTimeout(() => {
            errorDiv.style.display = 'none';
        }, 5000);
    }
}

function showSuccess(message) {
    const successDiv = document.getElementById('success');
    if (successDiv) {
        successDiv.textContent = message;
        successDiv.style.display = 'block';
        setTimeout(() => {
            successDiv.style.display = 'none';
        }, 3000);
    }
}

function setLoading(button, loading) {
    const btn = button;
    if (loading) {
        btn.disabled = true;
        btn.dataset.originalText = btn.textContent;
        btn.textContent = '请稍候...';
    } else {
        btn.disabled = false;
        btn.textContent = btn.dataset.originalText || '提 交';
    }
}

function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

function validatePassword(password) {
    return password.length >= 8;
}

function togglePasswordVisibility(inputId, button) {
    const input = document.getElementById(inputId);
    if (input.type === 'password') {
        input.type = 'text';
        button.textContent = '隐藏';
    } else {
        input.type = 'password';
        button.textContent = '显示';
    }
}

async function handleLogin(event) {
    event.preventDefault();
    
    const form = event.target;
    const email = document.getElementById('email').value.trim();
    const password = document.getElementById('password').value;
    const remember = document.getElementById('remember')?.checked || false;
    const submitBtn = form.querySelector('button[type="submit"]');
    
    if (!email || !password) {
        showError('请填写邮箱和密码');
        return;
    }
    
    if (!validateEmail(email)) {
        showError('请输入有效的邮箱地址');
        return;
    }
    
    setLoading(submitBtn, true);
    
    try {
        const response = await fetch('/api/auth/login/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify({ email, password, remember })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            if (data.token) {
                Auth.setToken(data.token);
            }
            if (data.refresh) {
                Auth.setRefresh(data.refresh);
            }
            if (data.user) {
                Auth.setUser(data.user);
            }
            showSuccess('登录成功！正在跳转...');
            
            setTimeout(() => {
                window.location.href = data.redirect || '/';
            }, 1000);
        } else {
            showError(data.error || '登录失败，请检查邮箱和密码');
        }
    } catch (error) {
        console.error('Login error:', error);
        showError('网络错误，请检查网络连接后重试');
    } finally {
        setLoading(submitBtn, false);
    }
}

async function handleRegister(event) {
    event.preventDefault();
    
    const form = event.target;
    const username = document.getElementById('username').value.trim();
    const email = document.getElementById('email').value.trim();
    const password = document.getElementById('password').value;
    const password_confirm = document.getElementById('password_confirm').value;
    const submitBtn = form.querySelector('button[type="submit"]');
    
    if (!username || !email || !password || !password_confirm) {
        showError('请填写所有必填字段');
        return;
    }
    
    if (username.length < 3) {
        showError('用户名至少需要3个字符');
        return;
    }
    
    if (!validateEmail(email)) {
        showError('请输入有效的邮箱地址');
        return;
    }
    
    if (!validatePassword(password)) {
        showError('密码至少需要8个字符');
        return;
    }
    
    if (password !== password_confirm) {
        showError('两次输入的密码不一致');
        return;
    }
    
    setLoading(submitBtn, true);
    
    try {
        const response = await fetch('/api/auth/register/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify({ username, email, password, password_confirm })
        });
        
        const data = await response.json();
        
        if (response.ok || response.status === 201) {
            showSuccess('注册成功！正在跳转到登录页...');
            
            setTimeout(() => {
                window.location.href = '/login/';
            }, 1500);
        } else {
            showError(data.error || data.detail || '注册失败，请重试');
        }
    } catch (error) {
        console.error('Register error:', error);
        showError('网络错误，请检查网络连接后重试');
    } finally {
        setLoading(submitBtn, false);
    }
}

async function handleLogout() {
    try {
        await fetch('/api/auth/logout/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCSRFToken()
            }
        });
    } catch (error) {
        console.error('Logout error:', error);
    } finally {
        Auth.logout();
    }
}

function checkLoginStatus() {
    const user = Auth.getUser();
    if (user) {
        updateUIForLoggedInUser(user);
    }
}

function updateUIForLoggedInUser(user) {
    const loginLink = document.getElementById('login-link');
    const registerLink = document.getElementById('register-link');
    const userInfo = document.getElementById('user-info');
    
    if (loginLink) loginLink.style.display = 'none';
    if (registerLink) registerLink.style.display = 'none';
    
    if (userInfo) {
        userInfo.style.display = 'flex';
        const usernameEl = userInfo.querySelector('.username');
        if (usernameEl) usernameEl.textContent = user.username || user.email;
    }
}

if (document.getElementById('loginForm')) {
    document.getElementById('loginForm').addEventListener('submit', handleLogin);
    
    document.getElementById('email').addEventListener('input', function() {
        this.value = this.value.trim();
    });
    
    const passwordInput = document.getElementById('password');
    if (passwordInput) {
        passwordInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                handleLogin(e);
            }
        });
    }
}

if (document.getElementById('registerForm')) {
    document.getElementById('registerForm').addEventListener('submit', handleRegister);
    
    document.getElementById('username').addEventListener('input', function() {
        this.value = this.value.replace(/[^a-zA-Z0-9_]/g, '');
    });
    
    document.getElementById('email').addEventListener('input', function() {
        this.value = this.value.trim();
    });
}

document.addEventListener('DOMContentLoaded', function() {
    checkLoginStatus();
    
    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', function(e) {
            e.preventDefault();
            handleLogout();
        });
    }
});
