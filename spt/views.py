from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q
from decimal import Decimal
import uuid

from .models import (
    ProductCategory, Product, ProductVariant, Customer,
    Cart, CartItem, Order, OrderItem, Inventory
)
from .serializers import (
    ProductCategorySerializer, ProductSerializer, ProductVariantSerializer,
    CustomerSerializer, CartSerializer, CartItemSerializer, OrderSerializer, OrderItemSerializer
)


class ProductCategoryViewSet(viewsets.ModelViewSet):
    """ViewSet for Product Categories"""
    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategorySerializer
    permission_classes = [AllowAny]
    filterset_fields = ['name']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']


class ProductVariantViewSet(viewsets.ModelViewSet):
    """ViewSet for Product Variants"""
    queryset = ProductVariant.objects.all()
    serializer_class = ProductVariantSerializer
    permission_classes = [AllowAny]
    filterset_fields = ['product', 'variant_type']
    search_fields = ['variant_name', 'sku']


class ProductViewSet(viewsets.ModelViewSet):
    """ViewSet for Products"""
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]
    filterset_fields = ['category', 'is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['base_price', 'created_at', 'name']

    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """Get products by category"""
        category_id = request.query_params.get('category_id')
        if not category_id:
            return Response({'error': 'category_id required'}, status=status.HTTP_400_BAD_REQUEST)

        products = self.queryset.filter(category_id=category_id)
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)


class CartViewSet(viewsets.ViewSet):
    """ViewSet for Shopping Cart"""
    permission_classes = [IsAuthenticated]

    def list(self, request):
        """Get user's cart"""
        cart, created = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    def create(self, request):
        """Clear and recreate cart"""
        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart.items.all().delete()
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def add(self, request):
        """Add item to cart"""
        cart, _ = Cart.objects.get_or_create(user=request.user)
        product_id = request.data.get('product_id')
        variant_id = request.data.get('variant_id')
        quantity = int(request.data.get('quantity', 1))

        if not product_id:
            return Response({'error': 'product_id required'}, status=status.HTTP_400_BAD_REQUEST)

        product = get_object_or_404(Product, id=product_id)
        variant = None
        if variant_id:
            variant = get_object_or_404(ProductVariant, id=variant_id)

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart, product=product, variant=variant,
            defaults={'quantity': quantity}
        )

        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        serializer = CartItemSerializer(cart_item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def remove(self, request):
        """Remove item from cart"""
        cart = get_object_or_404(Cart, user=request.user)
        item_id = request.data.get('item_id')

        if not item_id:
            return Response({'error': 'item_id required'}, status=status.HTTP_400_BAD_REQUEST)

        cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
        cart_item.delete()

        serializer = CartSerializer(cart)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def update_quantity(self, request):
        """Update item quantity"""
        cart = get_object_or_404(Cart, user=request.user)
        item_id = request.data.get('item_id')
        quantity = int(request.data.get('quantity', 1))

        if not item_id:
            return Response({'error': 'item_id required'}, status=status.HTTP_400_BAD_REQUEST)

        cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
        cart_item.quantity = max(1, quantity)
        cart_item.save()

        serializer = CartItemSerializer(cart_item)
        return Response(serializer.data)


class OrderViewSet(viewsets.ViewSet):
    """ViewSet for Orders"""
    permission_classes = [IsAuthenticated]

    def list(self, request):
        """Get user's orders"""
        orders = Order.objects.filter(user=request.user)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """Get specific order"""
        order = get_object_or_404(Order, id=pk, user=request.user)
        serializer = OrderSerializer(order)
        return Response(serializer.data)

    def create(self, request):
        """Create order from cart"""
        cart = get_object_or_404(Cart, user=request.user)

        if not cart.items.exists():
            return Response({'error': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)

        # Check stock availability for all items
        for cart_item in cart.items.all():
            if cart_item.variant:
                if cart_item.variant.stock_quantity < cart_item.quantity:
                    return Response(
                        {'error': f'Not enough stock for {cart_item.product.name} ({cart_item.variant.variant_name}). Available: {cart_item.variant.stock_quantity}'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
            else:
                total_stock = sum(v.stock_quantity for v in cart_item.product.variants.all())
                if total_stock < cart_item.quantity:
                    return Response(
                        {'error': f'Not enough stock for {cart_item.product.name}. Available: {total_stock}'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )

        # Create order
        order_number = f"ORD-{uuid.uuid4().hex[:8].upper()}"
        order = Order.objects.create(
            user=request.user,
            order_number=order_number,
            total_amount=cart.get_total(),
            shipping_address=request.data.get('address'),
            shipping_city=request.data.get('city'),
            shipping_state=request.data.get('state'),
            shipping_pincode=request.data.get('pincode')
        )

        # Add items to order and update stock
        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                variant=cart_item.variant,
                quantity=cart_item.quantity,
                price_at_purchase=cart_item.product.base_price,
                variant_price_at_purchase=cart_item.variant.additional_price if cart_item.variant else Decimal('0.00')
            )
            
            # Decrease stock
            if cart_item.variant:
                cart_item.variant.stock_quantity -= cart_item.quantity
                cart_item.variant.save()

        # Clear cart
        cart.items.all().delete()

        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'])
    def track(self, request, pk=None):
        """Track order status"""
        order = get_object_or_404(Order, id=pk, user=request.user)
        serializer = OrderSerializer(order)
        return Response(serializer.data)


class CustomerViewSet(viewsets.ViewSet):
    """ViewSet for Customer Profiles"""
    permission_classes = [IsAuthenticated]

    def list(self, request):
        """Get customer profile"""
        customer, created = Customer.objects.get_or_create(user=request.user)
        serializer = CustomerSerializer(customer)
        return Response(serializer.data)

    def create(self, request):
        """Create/Update customer profile"""
        customer, _ = Customer.objects.get_or_create(user=request.user)
        customer.phone = request.data.get('phone', customer.phone)
        customer.address = request.data.get('address', customer.address)
        customer.city = request.data.get('city', customer.city)
        customer.state = request.data.get('state', customer.state)
        customer.pincode = request.data.get('pincode', customer.pincode)
        customer.save()

        serializer = CustomerSerializer(customer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
