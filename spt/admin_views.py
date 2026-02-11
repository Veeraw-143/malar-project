"""
Admin dashboard views for data visualization and analytics
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from .models import Order, OrderItem, Product, ProductVariant, Customer, Cart
import json


def is_admin(user):
    """Check if user is admin"""
    return user.is_staff or user.is_superuser


@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    """
    Main admin dashboard with key metrics and visualizations
    """
    # Get date range (last 30 days by default)
    today = timezone.now().date()
    last_30_days = today - timedelta(days=30)
    
    # Calculate key metrics
    total_orders = Order.objects.count()
    total_revenue = Order.objects.aggregate(
        total=Sum('total_amount')
    )['total'] or Decimal('0.00')
    
    completed_orders = Order.objects.filter(status='completed').count()
    pending_orders = Order.objects.filter(status='pending').count()
    
    total_customers = Customer.objects.count()
    total_products = Product.objects.count()
    
    # Recent 30 days metrics
    orders_last_30 = Order.objects.filter(
        created_at__date__gte=last_30_days
    ).count()
    revenue_last_30 = Order.objects.filter(
        created_at__date__gte=last_30_days
    ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
    
    # Top products by sales
    top_products = OrderItem.objects.values(
        'product__name',
        'product__id'
    ).annotate(
        total_sold=Sum('quantity'),
        total_revenue=Sum('price')
    ).order_by('-total_sold')[:5]
    
    # Orders by status
    orders_by_status = Order.objects.values('status').annotate(
        count=Count('id')
    ).order_by('status')
    
    # Daily sales last 30 days
    daily_sales = Order.objects.filter(
        created_at__date__gte=last_30_days
    ).extra(
        select={'date': 'DATE(created_at)'}
    ).values('date').annotate(
        revenue=Sum('total_amount'),
        orders=Count('id')
    ).order_by('date')
    
    # Prepare chart data for daily sales
    daily_dates = []
    daily_revenues = []
    daily_orders = []
    
    for sale in daily_sales:
        daily_dates.append(str(sale['date']))
        daily_revenues.append(float(sale['revenue'] or 0))
        daily_orders.append(sale['orders'])
    
    # Prepare status data
    status_labels = []
    status_counts = []
    status_colors = {
        'pending': '#f59e0b',
        'processing': '#3b82f6',
        'completed': '#10b981',
        'cancelled': '#ef4444'
    }
    
    for status in orders_by_status:
        status_labels.append(status['status'].capitalize())
        status_counts.append(status['count'])
    
    # Top products data
    product_names = [p['product__name'] for p in top_products]
    product_quantities = [int(p['total_sold'] or 0) for p in top_products]
    product_ids = [p['product__id'] for p in top_products]
    
    # Stock levels - Low stock alert (less than 50 units)
    low_stock_items = ProductVariant.objects.filter(
        stock_quantity__lt=50
    ).select_related('product').order_by('stock_quantity')[:10]
    
    # Customer growth
    new_customers_last_30 = Customer.objects.filter(
        created_at__date__gte=last_30_days
    ).count()
    
    context = {
        'total_orders': total_orders,
        'total_revenue': f"{total_revenue:.2f}",
        'completed_orders': completed_orders,
        'pending_orders': pending_orders,
        'total_customers': total_customers,
        'total_products': total_products,
        'orders_last_30': orders_last_30,
        'revenue_last_30': f"{revenue_last_30:.2f}",
        'new_customers_last_30': new_customers_last_30,
        'top_products': list(top_products),
        'low_stock_items': low_stock_items,
        'daily_chart_data': {
            'labels': daily_dates,
            'revenues': daily_revenues,
            'orders': daily_orders
        },
        'status_chart_data': {
            'labels': status_labels,
            'data': status_counts,
            'colors': [status_colors.get(s['status'], '#6b7280') for s in orders_by_status]
        },
        'product_chart_data': {
            'labels': product_names,
            'data': product_quantities,
        }
    }
    
    return render(request, 'admin_dashboard.html', context)


@login_required
@user_passes_test(is_admin)
def admin_orders(request):
    """
    Admin panel for order management
    """
    # Get all orders with filtering
    orders = Order.objects.select_related('customer').prefetch_related('items').order_by('-created_at')
    
    # Filter by status if provided
    status_filter = request.GET.get('status')
    if status_filter:
        orders = orders.filter(status=status_filter)
    
    # Get unique statuses for filter dropdown
    statuses = Order.objects.values_list('status', flat=True).distinct()
    
    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(orders, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'orders': page_obj.object_list,
        'statuses': statuses,
        'current_status': status_filter,
    }
    
    return render(request, 'admin_orders.html', context)


@login_required
@user_passes_test(is_admin)
def admin_products(request):
    """
    Admin panel for product management and inventory
    """
    # Get all products with variant info
    products = Product.objects.prefetch_related('variants').annotate(
        total_stock=Sum('variants__stock_quantity'),
        total_variants=Count('variants')
    ).order_by('-created_at')
    
    # Calculate inventory metrics
    total_stock = ProductVariant.objects.aggregate(
        total=Sum('stock_quantity')
    )['total'] or 0
    
    low_stock = ProductVariant.objects.filter(
        stock_quantity__lt=50
    ).count()
    
    out_of_stock = ProductVariant.objects.filter(
        stock_quantity=0
    ).count()
    
    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(products, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'products': page_obj.object_list,
        'total_stock': total_stock,
        'low_stock_count': low_stock,
        'out_of_stock_count': out_of_stock,
    }
    
    return render(request, 'admin_products.html', context)
