"""
Django 视图模块，处理用户认证、系统入口和各类型用户功能页面
包含登录、注册、系统门户和不同用户类型的业务逻辑
"""

from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, HttpResponse, redirect
from django.http import JsonResponse
from django.contrib.auth import logout
from django.contrib.auth.models import User
from .models import *
import json

# 登录相关视图
def Login(request):
    """
    登录入口视图
    GET请求：返回登录页面
    POST请求：调用验证函数处理登录逻辑
    """
    if request.method == 'POST':
        # 使用verify函数处理登录逻辑
        result = verify(request)
        return HttpResponse(result)  # 返回验证结果
    else:
        return render(request, 'login.html')

def verify(request):
    """
    登录验证API
    接收JSON格式的登录凭证，返回认证结果和账户类型
    """
    if request.method == 'POST':
        data = json.loads(request.body)  # 解析JSON数据
        username = data.get('username')
        password = data.get('password')

        user = authenticate(username=username, password=password)  # Django内置认证
        if user is not None:
            login(request, user)  # 创建用户会话

            try:
                # 通过Account模型获取账户类型（转为小写）
                account_type = user.account.accounttype.lower()
            except AttributeError:
                return HttpResponse('账户类型错误', status=400)

            return HttpResponse(account_type)  # 返回账户类型（rider/customer/merchant）
        else:
            return HttpResponse('0')  # 0表示认证失败

# 系统门户路由
def system_portal(request):
    """
    系统门户路由
    根据用户类型重定向到对应子系统
    """
    if not request.user.is_authenticated:
        return redirect('/login/')

    try:
        # 从Account模型获取用户类型并重定向
        account_type = request.user.account.accounttype.lower()
        return redirect(f'/system/{account_type}')
    except AttributeError:
        return HttpResponse('账户类型错误')

# 各类型用户子系统视图
@login_required  # 必须登录才能访问
def rider_system(request):
    """
    骑手子系统主页
    显示骑手基本信息
    """
    try:
        # 通过反向关联获取骑手信息（Account -> Rider）
        rider = request.user.account.rider
        context = {
            'rider_id': rider.rid_id,    # 关联的Account主键
            'rider_name': rider.rname,
            'rider_phone': rider.rphone
        }
        return render(request, 'rider.html', context)
    except AttributeError:
        raise PermissionDenied("非骑手账户")  # 权限校验失败


@login_required
def rider_profile_api(request):
    try:
        rider = request.user.account.rider

        if request.method == 'GET':
            # 获取骑手信息
            return JsonResponse({
                'name': rider.rname,
                'phone': rider.rphone
            })

        elif request.method == 'PUT':
            # 更新骑手信息
            data = json.loads(request.body)
            rider.rname = data.get('name', rider.rname)
            rider.rphone = data.get('phone', rider.rphone)
            rider.save()
            return JsonResponse({'status': 'success'})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
def api_orders(request):
    try:
        rider = request.user.account.rider
        order_type = request.GET.get('type', 'pending')

        # 根据类型过滤订单
        if order_type == 'pending':
            orders = Order.objects.filter(status='pending', rid=None)
        elif order_type == 'active':
            orders = Order.objects.filter(status='active', rid=rider)
        elif order_type == 'history':
            orders = Order.objects.filter(rid=rider).exclude(status__in=['pending', 'active'])

        # 序列化订单数据
        data = [{
            'id': order.oid,
            'merchant_address': order.merchant_address,
            'customer_address': order.customer_address,
            'created_at': order.created_at.strftime('%Y-%m-%d %H:%M:%S')
        } for order in orders]

        return JsonResponse(data, safe=False)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

# views.py
@login_required
def accept_order(request, order_id):
    try:
        order = Order.objects.get(oid=order_id)
        if order.status == 'pending' and not order.rid:
            order.rid = request.user.account.rider
            order.status = 'active'
            order.save()
            return JsonResponse({'status': 'success'})
        return JsonResponse({'error': '订单不可接'}, status=400)
    except Order.DoesNotExist:
        return JsonResponse({'error': '订单不存在'}, status=404)

@login_required
def customer_system(request):
    """客户子系统主页（示例模板）"""
    if not request.user.is_authenticated:
        return redirect('/login/')
    return render(request, 'customer.html')

@login_required
def merchant_system(request):
    """商家子系统主页（示例模板）"""
    if not request.user.is_authenticated:
        return redirect('/login/')
    return render(request, 'merchant.html')

# 注册相关视图
def register(request):
    """注册入口页面"""
    return render(request,'takeoutRegistrationPortal.html')

def rider_register(request):
    """
    骑手注册API
    处理骑手注册的完整流程：
    1. 创建Django用户
    2. 创建关联的Account记录
    3. 创建骑手详细信息
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            # 获取注册参数
            username = data.get('username')
            password = data.get('password')
            name = data.get('name')
            phone = data.get('phone')

            # 参数校验
            if not all([username, password, name, phone]):
                return HttpResponse('缺少必要参数', status=400)

            # 用户名唯一性检查
            if User.objects.filter(username=username).exists():
                return HttpResponse('用户名已存在', status=400)

            # 创建用户（自动处理密码哈希）
            user = User.objects.create_user(
                username=username,
                password=password
            )

            # 创建关联账户（设置类型为Rider）
            account = Account.objects.create(
                user=user,
                accounttype="Rider"
            )

            # 创建骑手详细信息（与Account一对一关联）
            Rider.objects.create(
                rid=account,  # 使用Account作为主键
                rname=name,
                rphone=phone
            )

            # 自动登录新注册用户
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                return HttpResponse('注册成功', status=201)

            return HttpResponse('注册成功，请登录', status=201)

        except Exception as e:
            return HttpResponse(f'注册失败: {str(e)}', status=400)

    return render(request, 'riderRegistration.html')

def customer_register(request):
    """客户注册页面（示例）"""
    return render(request, 'customerRegistration.html')

def merchant_register(request):
    """商家注册页面（示例）"""
    return render(request, 'merchantRegistration.html')

def user_logout(request):
    """用户登出功能"""
    logout(request)  # 清除用户会话
    return redirect('/login/')  # 重定向到登录页