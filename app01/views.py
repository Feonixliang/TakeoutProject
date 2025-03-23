from django.contrib.auth import authenticate,login
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth import logout
from django.contrib.auth.models import User
from .models import *
import json

# Create your views here.
def Login(request):
    if request.method == 'POST':
        # 使用verify函数处理登录逻辑
        result = verify(request)
        return HttpResponse(result)  # 将字符串包装为HttpResponse
    else:
        return render(request, 'login.html')

# views.py
def verify(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')

        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)

            # 获取账户类型
            try:
                account_type = user.account.accounttype.lower()  # 获取关联的Account类型
            except AttributeError:
                return HttpResponse('账户类型错误', status=400)

            return HttpResponse(account_type)  # 返回类型字符串如"rider"
        else:
            return HttpResponse('0')  # 登录失败


def system_portal(request):
    if not request.user.is_authenticated:
        return redirect('/login/')

    try:
        account_type = request.user.account.accounttype.lower()
        print(account_type)
        return redirect(f'/system/{account_type}')
    except AttributeError:
        return HttpResponse('账户类型错误')

@login_required
def rider_system(request):
    if not request.user.is_authenticated:
        return redirect('/login/')
    return render(request, 'rider.html')

@login_required
def customer_system(request):
    if not request.user.is_authenticated:
        return redirect('/login/')
    return render(request, 'customer.html')

@login_required
def merchant_system(request):
    if not request.user.is_authenticated:
        return redirect('/login/')
    return render(request, 'merchant.html')


def register(request):
    return render(request,'takeoutRegistrationPortal.html')


# views.py

def rider_register(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
            name = data.get('name')
            phone = data.get('phone')

            # 验证必要参数
            if not all([username, password, name, phone]):
                return HttpResponse('缺少必要参数', status=400)

            # 检查用户名是否已存在
            if User.objects.filter(username=username).exists():
                return HttpResponse('用户名已存在', status=400)

            # 创建Django用户（密码自动加密）
            user = User.objects.create_user(
                username=username,
                password=password  # 自动处理密码哈希
            )

            # 创建Account记录（与User一对一关联）
            account = Account.objects.create(
                user=user,          # 关联新建的User
                accounttype="Rider"
            )

            # 创建骑手记录
            Rider.objects.create(
                rid=account,  # 关联Account（rid是主键）
                rname=name,
                rphone=phone
            )

            # 自动登录
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                return HttpResponse('注册成功', status=201)

            return HttpResponse('注册成功，请登录', status=201)

        except Exception as e:
            return HttpResponse(f'注册失败: {str(e)}', status=400)

    return render(request, 'riderRegistration.html')


def customer_register(request):
    return render(request, 'customerRegistration.html')

def merchant_register(request):
    return render(request, 'merchantRegistration.html')

def user_logout(request):
    logout(request)  # 清除用户会话
    return redirect('/login/')  # 重定向到登录页