from django.shortcuts import render
from django.contrib.auth.decorators import login_required


def index(request):
    """Home page"""
    return render(request, 'index.html')


def products(request):
    """Products listing page"""
    return render(request, 'products.html')


@login_required
def cart(request):
    """Cart page"""
    return render(request, 'cart.html')


@login_required
def checkout(request):
    """Checkout page"""
    return render(request, 'checkout.html')


@login_required
def order_tracking(request, order_id):
    """Order tracking page"""
    return render(request, 'order_tracking.html', {'order_id': order_id})


@login_required
def customer_account(request):
    """Customer account page"""
    return render(request, 'customer_account.html')
