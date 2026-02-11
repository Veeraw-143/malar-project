from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProductCategoryViewSet, ProductViewSet, ProductVariantViewSet,
    CartViewSet, OrderViewSet, CustomerViewSet
)
from .admin_views import admin_dashboard, admin_orders, admin_products

router = DefaultRouter()
router.register(r'categories', ProductCategoryViewSet, basename='category')
router.register(r'products', ProductViewSet, basename='product')
router.register(r'variants', ProductVariantViewSet, basename='variant')
router.register(r'cart', CartViewSet, basename='cart')
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'customer', CustomerViewSet, basename='customer')

urlpatterns = [
    path('', include(router.urls)),
    # Admin Dashboard URLs
    path('admin-dashboard/', admin_dashboard, name='admin_dashboard'),
    path('admin-orders/', admin_orders, name='admin_orders'),
    path('admin-products/', admin_products, name='admin_products'),
]
