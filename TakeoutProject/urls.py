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

    #用户访问www.xxxx.com/login    -> 执行函数
    path('login/', views.login),
    path('system/rider', views.rider_system),
    path('system/customer', views.customer_system),
    path('system/merchant', views.merchant_system),

    path('register/choose', views.register),

    path('register/rider', views.rider_register),
    path('register/customer', views.customer_register),
    path('register/merchant', views.merchant_register),


]
