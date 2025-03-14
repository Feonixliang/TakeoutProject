from django.shortcuts import render, HttpResponse

# Create your views here.
def login(request):
    return render(request, 'login.html')

def rider_system(request):
    return render(request, 'rider.html')

def customer_system(request):
    return render(request, 'customer.html')

def merchant_system(request):
    return render(request, 'merchant.html')

def register(request):
    return render(request,'takeoutRegistrationPortal.html')

def rider_register(request):
    return render(request, 'riderRegistration.html')

def customer_register(request):
    return render(request, 'customerRegistration.html')

def merchant_register(request):
    return render(request, 'merchantRegistration.html')