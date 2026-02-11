from typing import TYPE_CHECKING, Any
from rest_framework import serializers
from .models import (
    ProductCategory, Product, ProductVariant, Customer,
    Cart, CartItem, Order, OrderItem
)


class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = ['id', 'name', 'description', 'created_at', 'updated_at']


class ProductVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = ['id', 'variant_name', 'variant_type', 'additional_price', 'stock_quantity', 'sku']


class ProductSerializer(serializers.ModelSerializer):
    variants = ProductVariantSerializer(many=True, read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'category', 'category_name', 'base_price', 'image_url', 'is_active', 'variants', 'created_at', 'updated_at']


class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_price = serializers.DecimalField(source='product.base_price', max_digits=10, decimal_places=2, read_only=True)
    variant_name = serializers.CharField(source='variant.variant_name', read_only=True)
    variant_price = serializers.DecimalField(source='variant.additional_price', max_digits=10, decimal_places=2, read_only=True)
    item_total = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_name', 'product_price', 'variant', 'variant_name', 'variant_price', 'quantity', 'item_total']

    def get_item_total(self, obj: CartItem) -> Any:
        return obj.get_item_total()


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total = serializers.SerializerMethodField()
    item_count = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'items', 'total', 'item_count', 'created_at', 'updated_at']

    def get_total(self, obj: Cart) -> Any:
        return obj.get_total()

    def get_item_count(self, obj: Cart) -> int:
        return obj.get_item_count()


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    variant_name = serializers.CharField(source='variant.variant_name', read_only=True)
    item_total = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'variant', 'variant_name', 'quantity', 'price_at_purchase', 'variant_price_at_purchase', 'item_total']

    def get_item_total(self, obj: OrderItem) -> Any:
        return (obj.price_at_purchase + obj.variant_price_at_purchase) * obj.quantity


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'order_number', 'username', 'status', 'total_amount', 'shipping_address', 'shipping_city', 'shipping_state', 'shipping_pincode', 'tracking_number', 'items', 'created_at', 'updated_at']


class CustomerSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = Customer
        fields = ['id', 'username', 'email', 'phone', 'address', 'city', 'state', 'pincode', 'created_at', 'updated_at']
