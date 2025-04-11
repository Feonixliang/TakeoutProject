"""
Django 视图模块，处理用户认证、系统入口和各类型用户功能页面
包含登录、注册、系统门户和不同用户类型的业务逻辑
"""
from django.views.decorators.http import require_http_methods
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, HttpResponse, redirect
from django.http import JsonResponse
from django.db import IntegrityError, transaction
from django.contrib.auth import logout
from django.contrib.auth.models import User
from .models import *
import json
from django.db.models import Q


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
        return render(request, 'logintest.html')


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
            'rider_id': rider.rid_id,  # 关联的Account主键
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
        order_type = request.GET.get("type", "pending")
        if order_type not in ["pending", "active", "history"]:
            return JsonResponse({"error": "无效的订单类型"}, status=400, ensure_ascii=False)

        # 基础查询集
        orders = Order.objects.select_related(
            'cid',  # 客户信息
            'mid'  # 商家信息
        ).prefetch_related(
            'orderdishes_set__did'  # 预载订单菜品
        )

        # 根据类型过滤
        if order_type == "pending":
            orders = orders.filter(status="pending", rid__isnull=True)
        elif order_type == "active":
            rider = request.user.account.rider
            orders = orders.filter(status="active", rid=rider)
        elif order_type == "history":
            rider = request.user.account.rider
            orders = orders.filter(rid=rider).exclude(status__in=["pending", "active"])

        data = []
        for order in orders:
            # 商家信息（mid是必填字段）
            merchant_info = {
                "maddress": order.mid.maddress,
                "mname": order.mid.mname
            } if order.mid else {
                "maddress": "未知商家",
                "mname": "未知商家"
            }

            # 客户信息（cid有默认值-1需要处理）
            try:
                customer_info = {
                    "cname": order.cid.cname,
                    "cphone": order.cid.cphone,
                    "caddress": order.cid.caddress
                } if order.cid else {
                    "cname": "未知客户",
                    "cphone": "",
                    "caddress": ""
                }
            except Customer.DoesNotExist:
                customer_info = {
                    "cname": "无效客户",
                    "cphone": "",
                    "caddress": ""
                }

            # 订单菜品详情
            items = []
            for order_dish in order.orderdishes_set.all():
                dish = order_dish.did
                items.append({
                    "name": dish.dname,
                    "quantity": order_dish.quantity,
                    "unit_price": float(dish.dprice),
                    "subtotal": float(dish.dprice * order_dish.quantity)
                })

            # 构造订单数据
            order_data = {
                "id": order.oid,
                "merchant": merchant_info,
                "customer": customer_info,
                "items": items,
                "total_price": float(order.totalprice),
                "status": order.get_status_display()  # 显示中文状态
            }
            data.append(order_data)

        return JsonResponse(data, safe=False, ensure_ascii=False)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400, ensure_ascii=False)


@login_required
def accept_order(request, order_id):
    try:
        order = Order.objects.get(oid=order_id)
        # 筛选未接取 & 骑手未接订单
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
    """客户子系统主页"""
    try:
        # 获取当前用户的客户信息
        customer = request.user.account.customer
        context = {
            'customer_name': customer.cname
        }
        return render(request, 'customer.html', context)
    except AttributeError:
        raise PermissionDenied("非客户账户")


@login_required
def merchant_system(request):
    """
    商家子系统主页
    显示商家基本信息
    """
    try:
        # 通过反向关联获取商家信息（Account -> Rider）
        merchant = request.user.account.merchant
        context = {
            'merchant_id': merchant.mid_id,  # 关联的Account主键
            'merchant_name': merchant.mname,
            'merchant_phone': merchant.mphone,
            'merchant_address': merchant.maddress,
            'merchant_balance': merchant.mbalance
        }
        return render(request, 'merchant.html', context)
    except AttributeError:
        raise PermissionDenied("非商家账户")  # 权限校验失败


@login_required
@require_http_methods(["POST"])
def change_password_api(request):
    try:
        data = json.loads(request.body)
        user = request.user

        # 验证数据完整性
        if not all([data.get('old_password'), data.get('new_password')]):
            return JsonResponse({'error': '所有字段必须填写'}, status=400)

        # 验证旧密码
        if not user.check_password(data['old_password']):
            return JsonResponse({'error': '旧密码不正确'}, status=400)

        # 更新密码
        user.set_password(data['new_password'])
        user.save()

        # 重新登录保持会话
        update_session_auth_hash(request, user)

        return JsonResponse({'status': 'success'})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# 注册相关视图
def register(request):
    """注册入口页面"""
    return render(request, 'takeoutRegistrationPortal.html')


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
            username = data.get('account')
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
                accounttype="rider"
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
    """
    客户注册API
    处理客户注册的完整流程：
    1. 创建Django用户
    2. 创建关联的Account记录
    3. 创建客户详细信息
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            # 获取注册参数
            name = data.get('name')
            username = data.get('username')
            password = data.get('password')
            phone = data.get('phone')
            address = data.get('address')

            # 参数校验
            if not all([name, username, password, phone, address]):
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
                accounttype="customer"
            )

            # 创建骑手详细信息（与Account一对一关联）
            Customer.objects.create(
                cid=account,  # 使用Account作为主键
                cname=name,
                cphone=phone,
                caddress=address,
                cbalance=0.0
            )

            # 自动登录新注册用户
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                return HttpResponse('注册成功', status=201)

            return HttpResponse('注册成功，请登录', status=201)

        except Exception as e:
            return HttpResponse(f'注册失败: {str(e)}', status=400)

    return render(request, 'customerRegistration.html')


def merchant_register(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            # 获取注册参数
            name = data.get('name')  # username是Django的账户
            username = data.get('username')
            password = data.get('password')
            phone = data.get('phone')
            address = data.get('address')
            balance = 0.0

            # 参数校验
            if not all([name, username, password, phone, address]):
                return HttpResponse('缺少必要参数', status=400)

            # 用户名唯一性检查
            if User.objects.filter(username=username).exists():
                return HttpResponse('账户已存在', status=400)

            # 创建用户（自动处理密码哈希）
            user = User.objects.create_user(
                username=username,
                password=password
            )

            # 创建关联账户（设置类型为merchant）
            account = Account.objects.create(
                user=user,
                accounttype="merchant"
            )

            # 创建商家详细信息（与Account一对一关联）
            Merchant.objects.create(
                mid=account,  # 使用Account作为主键
                mname=name,
                mphone=phone,
                maddress=address,
                mbalance=balance
            )

            # 自动登录新注册用户
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                return HttpResponse('注册成功', status=201)

            return HttpResponse('注册成功，请登录', status=201)

        except Exception as e:
            return HttpResponse(f'注册失败: {str(e)}', status=400)

    return render(request, 'merchantRegistration.html')


def user_logout(request):
    """用户登出功能"""
    logout(request)  # 清除用户会话
    return redirect('/login/')  # 重定向到登录页


from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
@login_required
@require_http_methods(["GET", "POST", "DELETE"])  # 保持POST方法
def dish_api(request, dish_id=None):
    try:
        # 获取当前登录用户的关联商家信息。
        merchant = request.user.account.merchant

        # 如果请求方法是 GET，则获取当前商家的所有菜品信息。
        if request.method == 'GET':
            dishes = Dishes.objects.filter(merchantdishes__mid=merchant)  # 查询数据库中属于当前商家的所有菜品。
            data = [{
                "id": dish.did,  # 菜品ID
                "name": dish.dname,  # 菜品名称
                "price": float(dish.dprice),  # 转换菜品价格为浮点数格式
                "category": dish.dcategory  # 菜品类别
            } for dish in dishes]  # 遍历查询到的每个菜品对象，并构建字典。

            print(data)
            return JsonResponse(data, safe=False)

        # 修改菜品
        if request.method == 'POST' and dish_id:  # 修改逻辑
            # 验证菜品归属
            dish = Dishes.objects.get(did=dish_id)
            Merchantdishes.objects.get(did=dish, mid=merchant)

            data = json.loads(request.body)

            # 更新字段
            update_fields = []
            if 'name' in data:
                dish.dname = data['name']
                update_fields.append('dname')
            if 'price' in data:
                dish.dprice = data['price']
                update_fields.append('dprice')
            if 'category' in data:
                dish.dcategory = data['category']
                update_fields.append('dcategory')

            if update_fields:
                dish.save(update_fields=update_fields)

            return JsonResponse({
                "id": dish.did,
                "name": dish.dname,
                "price": float(dish.dprice),
                "category": dish.dcategory
            })

        # 如果请求方法是 POST，则创建一个新的菜品并将其关联到当前商家。
        if request.method == 'POST' and not dish_id:
            data = json.loads(request.body)  # 解析请求体中的 JSON 数据。

            dish = Dishes.objects.create(  # 在数据库中创建新的菜品记录。
                dname=data['name'],
                dprice=data['price'],
                dcategory=data.get('category', '')
            )

            # 创建 Merchantdishes 记录来关联新菜品和商家。
            Merchantdishes.objects.create(did=dish, mid=merchant)

            return JsonResponse({  # 向客户端返回包含新创建菜品信息的 JSON 响应
                "id": dish.did,
                "name": dish.dname,
                "price": float(dish.dprice),
                "category": dish.dcategory
            }, status=201)

        # 如果请求方法是 DELETE，则删除指定 ID 的菜品。
        if request.method == 'DELETE':
            try:
                dish = Dishes.objects.get(did=dish_id)  # 从数据库中获取要删除的菜品。
                Merchantdishes.objects.get(did=dish, mid=merchant).delete()  # 删除该菜品与商家之间的关联。
                dish.delete()  # 从数据库中彻底移除该菜品。
                return JsonResponse({"status": "success"})
            except Exception as e:
                return JsonResponse({"error": str(e)}, status=404)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


# 修改views.py中的search_dishes视图
# views.py 修改搜索视图
@csrf_exempt
@login_required
@require_http_methods(["GET"])
def search_dishes(request):
    try:
        merchant = request.user.account.merchant
        keyword = request.GET.get('keyword', '')
        category = request.GET.get('category', 'all')

        # 构建基础查询
        query = Q(merchantdishes__mid=merchant)

        # 关键词过滤
        if keyword:
            query &= Q(dname__icontains=keyword)

        # 分类过滤
        if category != 'all':
            query &= Q(dcategory=category)

        # 执行查询
        dishes = Dishes.objects.filter(query).distinct()

        # 序列化数据
        data = [{
            "id": dish.did,
            "name": dish.dname,
            "price": float(dish.dprice),
            "category": dish.dcategory or ""
        } for dish in dishes]

        return JsonResponse(data, safe=False)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@login_required
@require_http_methods(["GET", "POST"])
def merchant_settings_api(request):
    try:
        # 安全获取商家对象（自动处理404）
        merchant = request.user.account.merchant

        # GET请求处理：返回当前设置
        if request.method == 'GET':
            return JsonResponse({
                'name': merchant.mname,  # 商家名称
                'phone': merchant.mphone,  # 联系电话
                'address': merchant.maddress  # 店铺地址
            })

        # POST请求处理：更新设置
        if request.method == 'POST':
            data = json.loads(request.body)

            # 数据完整性校验
            if not all([data.get('name'), data.get('phone'), data.get('address')]):
                return JsonResponse({'error': '所有字段必须填写'}, status=400)

            # 逐步更新字段
            merchant.mname = data['name']
            merchant.mphone = data['phone']
            merchant.maddress = data['address']
            merchant.save()

            return JsonResponse({'status': 'success'})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@require_http_methods(["GET", "POST"])
@login_required
@login_required
def merchant_list_api(request):
    try:
        merchants = Merchant.objects.all()
        # for merchant in merchants:
        #     print("id:", merchant.mid_id,  # 注意这里遍历每个merchant对象
        #           "name:", merchant.mname,
        #           "address:", merchant.maddress,
        #           "phone:", merchant.mphone)
        data = [{
            "id": merchant.mid_id,
            "name": merchant.mname,
            "address": merchant.maddress,
            "phone": merchant.mphone
        } for merchant in merchants]
        return JsonResponse(data, safe=False)
    except Exception as e:
        print(f"Error fetching merchants: {str(e)}")  # 添加日志输出
        return JsonResponse({"error": str(e)}, status=400)


# views.py 新增
@login_required
def merchant_menu_api(request, merchant_id):
    """获取商家菜单"""
    try:
        # 获取商家对象
        merchant = Merchant.objects.get(mid_id=merchant_id)
        dishes = Dishes.objects.filter(
            merchantdishes__mid=merchant
        )

        # 按分类组织数据
        categories = {}
        for dish in dishes:
            category = dish.dcategory or '未分类'
            if category not in categories:
                categories[category] = []
            categories[category].append({
                'id': dish.did,
                'name': dish.dname,
                'price': float(dish.dprice)
            })

        return JsonResponse({
            'merchant': {
                'id': merchant.mid_id,
                'name': merchant.mname,
                'address': merchant.maddress
            },
            'categories': list(categories.keys()),  # 新增分类列表
            'menu': categories
        })

    except Merchant.DoesNotExist:
        return JsonResponse({'error': '商家不存在'}, status=404)


# views.py
@login_required
def merchant_orders_api(request):
    """获取商家订单数据（修复Orderdishes查询问题）"""
    try:
        merchant = request.user.account.merchant
        orders = Order.objects.filter(mid=merchant).select_related('cid', 'rid')

        orders_data = []
        for order in orders:
            # 使用values()直接获取需要字段，避免模型id问题
            dishes = Orderdishes.objects.filter(oid=order).values(
                'did__dname',  # 菜品名称
                'quantity',  # 数量
                'did__dprice'  # 单价
            )

            dishes_data = [{
                "name": item['did__dname'],
                "quantity": item['quantity'],
                "price": float(item['did__dprice']),
                "subtotal": float(item['did__dprice'] * item['quantity'])
            } for item in dishes]

            order_data = {
                "oid": order.oid,
                "status": order.get_status_display(),
                "total_price": float(order.totalprice),
                "customer_info": {
                    "name": order.cid.cname,
                    "phone": order.cid.cphone,
                    "address": order.cid.caddress
                },
                "dishes": dishes_data,
                "rider_info": {
                    "name": order.rid.rname if order.rid else None,
                    "phone": order.rid.rphone if order.rid else None
                } if order.rid else None
            }
            orders_data.append(order_data)

        return JsonResponse(orders_data, safe=False)

    except Exception as e:
        print(f"Error fetching orders: {str(e)}")
        return JsonResponse({"error": "服务器内部错误"}, status=500)


@login_required
def merchant_detail_api(request, merchant_id):
    """获取商家详情"""
    try:
        merchant = Merchant.objects.get(mid_id=merchant_id)
        return JsonResponse({
            'id': merchant.mid_id,
            'name': merchant.mname,
            'address': merchant.maddress,
            'phone': merchant.mphone,
            'rating': 4.8,  # 示例数据，需根据实际业务添加评分逻辑
            'monthly_sales': 1000
        })
    except Merchant.DoesNotExist:
        return JsonResponse({'error': '商家不存在'}, status=404)


# 在views.py的create_order视图中进行如下修改
@csrf_exempt
@login_required
def create_order(request):
    """创建订单"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        customer = request.user.account.customer
        data = json.loads(request.body)

        # 验证数据格式
        required_fields = ['merchant_id', 'items']
        if not all(field in data for field in required_fields):
            return JsonResponse({'error': '缺少必要字段'}, status=400)

        # 获取商家
        merchant = Merchant.objects.get(mid=data['merchant_id'])

        # 创建订单
        with transaction.atomic():
            # 创建主订单（不包含地址字段）
            order = Order.objects.create(
                cid=customer,
                mid=merchant,
                totalprice=0.00,
                status='pending'
            )
            # 计算总价并创建订单菜品
            total = 0
            for item in data['items']:
                dish = Dishes.objects.get(did=item['dish_id'])
                quantity = item['quantity']

                # 数据验证
                if quantity <= 0:
                    raise ValueError("商品数量必须大于0")

                # 验证菜品是否属于该商家
                if not Merchantdishes.objects.filter(did=dish, mid=merchant).exists():
                    raise PermissionDenied("商家没有该菜品")

                Orderdishes.objects.create(
                    oid=order,
                    did=dish,
                    quantity=quantity
                )

                total += float(dish.dprice) * quantity

            # 更新订单总价
            order.totalprice = total
            order.save()

            return JsonResponse({
                'order_id': order.oid,
                'status': order.status,
                'total_price': order.totalprice,
                # 通过外键获取地址
                'merchant_address': merchant.maddress,  # 直接取商家地址
                'customer_address': customer.caddress  # 直接取客户地址
            })

    except Merchant.DoesNotExist:
        return JsonResponse({'error': '商家不存在'}, status=404)
    except Dishes.DoesNotExist:
        return JsonResponse({'error': '菜品不存在'}, status=404)
    except KeyError as e:
        return JsonResponse({'error': f'缺少必要参数: {str(e)}'}, status=400)
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)
    except PermissionDenied as e:
        return JsonResponse({'error': str(e)}, status=403)
    except Exception as e:
        return JsonResponse({'error': f'服务器错误: {str(e)}'}, status=500)


# 在 views.py 中添加以下视图函数
@login_required
def order_list_api(request):
    """骑手订单列表API（解决 /api/orders/ 404 问题）"""
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

        # 增强订单数据序列化（匹配前端需求）
        data = []
        for order in orders:
            customer = order.cid
            data.append({
                'id': order.oid,
                'status': order.status,
                'total': float(order.totalprice),
                'customer': {
                    'name': customer.cname,
                    'phone': customer.cphone,
                    'address': customer.caddress
                },
                'items': [{
                    'name': item.did.dname,
                    'quantity': item.quantity,
                    'subtotal': float(item.did.dprice * item.quantity)
                } for item in order.orderdishes_set.all()],
                'created_at': order.created_at.strftime('%Y-%m-%d %H:%M:%S')
            })
        return JsonResponse(data, safe=False)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


# 新增订单状态更新视图函数
@login_required
@login_required
@login_required
def update_order_status(request, order_id):
    """更新订单状态（添加严格权限校验）"""
    try:
        order = Order.objects.get(oid=order_id)
        rider = request.user.account.rider

        # 新增：校验当前骑手是否为订单接单人
        if order.rid != rider:
            return JsonResponse({'error': '无权操作此订单'}, status=403)

        data = json.loads(request.body)
        new_status = data.get('status')

        if new_status not in ['completed', 'canceled']:
            return JsonResponse({'error': '无效状态'}, status=400)

        order.status = new_status
        order.save()
        return JsonResponse({'status': 'success'})

    except Order.DoesNotExist:
        return JsonResponse({'error': '订单不存在'}, status=404)
