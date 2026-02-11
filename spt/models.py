from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal

class ProductCategory(models.Model):
    """Product Category Model"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Product Categories"
        ordering = ['name']

    def __str__(self):
        return self.name


class Product(models.Model):
    """Product Model"""
    name = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE, related_name='products')
    base_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    image_url = models.URLField(blank=True, null=True)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def get_image_url(self):
        """Get image URL - prefer uploaded image, fallback to image_url"""
        if self.image:
            return self.image.url
        return self.image_url or '/static/images/default.jpg'

    def get_total_stock(self):
        """Get total stock across all variants"""
        return sum(v.stock_quantity for v in self.variants.all())


class ProductVariant(models.Model):
    """Product Variant Model (size, color, etc.)"""
    VARIANT_TYPES = [
        ('SIZE', 'Size'),
        ('COLOR', 'Color'),
        ('MATERIAL', 'Material'),
        ('FINISH', 'Finish'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    variant_name = models.CharField(max_length=100)  # e.g., "10mm", "Red", "Steel"
    variant_type = models.CharField(max_length=20, choices=VARIANT_TYPES)
    additional_price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), validators=[MinValueValidator(0)])
    stock_quantity = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    sku = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['variant_type', 'variant_name']
        unique_together = ['product', 'variant_name', 'variant_type']

    def __str__(self):
        return f"{self.product.name} - {self.variant_name}"


class Customer(models.Model):
    """Customer Profile Model"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile')
    phone = models.CharField(max_length=20)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.phone}"


class Cart(models.Model):
    """Shopping Cart Model"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart of {self.user.username}"

    def get_total(self):
        """Calculate cart total"""
        total = sum((item.get_item_total() for item in self.items.all()), Decimal('0.00'))
        return total

    def get_item_count(self):
        """Get total items in cart"""
        return sum((item.quantity for item in self.items.all()), 0)


class CartItem(models.Model):
    """Cart Item Model"""
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['cart', 'product', 'variant']

    def __str__(self):
        return f"{self.product.name} x{self.quantity}"

    def get_item_total(self):
        """Calculate total price for this item"""
        price = Decimal(str(self.product.base_price))
        if self.variant:
            price += Decimal(str(self.variant.additional_price))
        return price * Decimal(str(self.quantity))


class Order(models.Model):
    """Order Model"""
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('PROCESSING', 'Processing'),
        ('SHIPPED', 'Shipped'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    order_number = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_address = models.TextField()
    shipping_city = models.CharField(max_length=100)
    shipping_state = models.CharField(max_length=100)
    shipping_pincode = models.CharField(max_length=10)
    tracking_number = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order {self.order_number}"


class OrderItem(models.Model):
    """Order Item Model"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2)
    variant_price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))

    def __str__(self):
        return f"{self.product.name} in Order {self.order.order_number}"


class Inventory(models.Model):
    """Inventory Tracking Model"""
    variant = models.OneToOneField(ProductVariant, on_delete=models.CASCADE, related_name='inventory')
    total_stock = models.IntegerField(default=0)
    reserved_stock = models.IntegerField(default=0)
    available_stock = models.IntegerField(default=0)
    reorder_level = models.IntegerField(default=10)
    last_restocked = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Inventory"

    def __str__(self):
        return f"Inventory: {self.variant.product.name} - {self.variant.variant_name}"

