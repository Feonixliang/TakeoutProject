"""
URL configuration for TakeoutProject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# from django.contrib import admin
from django.urls import path
from app01 import views

urlpatterns = [
    #    path('admin/', admin.site.urls),

    # 用户访问www.xxxx.com/login    -> 执行函数
    path('login/', views.Login, name='login'),
    path('logout/', views.user_logout, name='logout'),  # 新增退出路由

    path('system/', views.system_portal),  # 新增系统入口
    path('system/rider', views.rider_system),
    path('system/customer', views.customer_system),
    path('system/merchant', views.merchant_system),



    path('register/choose', views.register),

    path('register/rider', views.rider_register, name='rider_register'),
    path('register/customer', views.customer_register, name='customer_register'),
    path('register/merchant', views.merchant_register, name='merchant_register'),
    path('api/merchant/settings/', views.merchant_settings_api),
    path('api/merchants/', views.merchant_list_api, name='merchant_list'),
    path('api/merchant/change-password/', views.change_password_api, name='change-password'),

    path('api/merchant/orders/', views.merchant_orders_api, name='merchant-orders'),

    path('api/merchants/<int:merchant_id>/', views.merchant_detail_api, name='merchant-detail'),
    path('api/merchants/<int:merchant_id>/menu/', views.merchant_menu_api, name='merchant-menu'),

    path('api/customer/orders/', views.customer_orders_api, name='customer-orders'),

    path('api/orders/<int:order_id>/status/', views.update_order_status, name='update-order-status'),

    path('api/orders/create/', views.create_order, name='create-order'),

    path('api/rider/profile/', views.rider_profile_api, name='rider-profile-api'),

    path('api/orders/<int:order_id>/accept/', views.accept_order, name='accept-order'),

    path('api/dishes/', views.dish_api, name='dish_api'),
    path('api/dishes/<int:dish_id>/', views.dish_api, name='dish_detail'),
    path('api/dishes/search/', views.search_dishes, name='search-dishes'),

    path('api/address/', views.address_api, name='address_api'),

    path('api/orders/', views.api_orders, name='order-list'),

    path('api/orders/<int:order_id>/status/', views.update_order_status, name='update-order-status'),

]
