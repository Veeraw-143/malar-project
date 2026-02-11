from django.contrib import admin
from .models import (
    ProductCategory, Product, ProductVariant, Customer,
    Cart, CartItem, Order, OrderItem, Inventory
)


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'base_price', 'is_active', 'created_at']
    list_filter = ['category', 'is_active', 'created_at']
    search_fields = ['name', 'description']


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ['product', 'variant_name', 'variant_type', 'sku', 'stock_quantity']
    list_filter = ['variant_type', 'product']
    search_fields = ['variant_name', 'sku']


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'city', 'created_at']
    search_fields = ['user__username', 'phone', 'city']


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['user', 'created_at']
    search_fields = ['user__username']


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['cart', 'product', 'variant', 'quantity']
    search_fields = ['product__name']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'user', 'status', 'total_amount', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['order_number', 'user__username']


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'quantity', 'price_at_purchase']
    search_fields = ['order__order_number', 'product__name']


@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ['variant', 'total_stock', 'available_stock', 'reorder_level']
    search_fields = ['variant__product__name']

