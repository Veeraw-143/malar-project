from django.core.management.base import BaseCommand
from spt.models import ProductCategory, Product, ProductVariant
from decimal import Decimal

class Command(BaseCommand):
    help = 'Add sample products with categories and variants'

    def handle(self, *args, **options):
        # Clear existing data
        ProductVariant.objects.all().delete()
        Product.objects.all().delete()
        ProductCategory.objects.all().delete()

        # Create categories
        cement_cat = ProductCategory.objects.create(
            name='Cement',
            description='Quality cement for construction'
        )
        
        bricks_cat = ProductCategory.objects.create(
            name='Bricks',
            description='High quality bricks for building'
        )
        
        tmt_cat = ProductCategory.objects.create(
            name='TMT Iron Rods',
            description='Titanium treated TMT iron rods for reinforcement'
        )

        # Create Cement Products
        cement1 = Product.objects.create(
            name='Portland Cement 50kg',
            description='High quality Portland cement suitable for all construction work',
            category=cement_cat,
            base_price=Decimal('350.00'),
            image_url='https://via.placeholder.com/300?text=Portland+Cement',
            is_active=True
        )

        # Add cement variants
        ProductVariant.objects.create(
            product=cement1,
            variant_name='Grade A',
            variant_type='MATERIAL',
            additional_price=Decimal('0.00'),
            stock_quantity=500,
            sku='CEMENT-50-GA-001'
        )

        ProductVariant.objects.create(
            product=cement1,
            variant_name='Grade B',
            variant_type='MATERIAL',
            additional_price=Decimal('25.00'),
            stock_quantity=300,
            sku='CEMENT-50-GB-001'
        )

        # Bricks Products
        bricks1 = Product.objects.create(
            name='Clay Bricks (Per 1000)',
            description='Standard clay bricks for walls and partitions',
            category=bricks_cat,
            base_price=Decimal('4500.00'),
            image_url='https://via.placeholder.com/300?text=Clay+Bricks',
            is_active=True
        )

        ProductVariant.objects.create(
            product=bricks1,
            variant_name='Standard Red',
            variant_type='COLOR',
            additional_price=Decimal('0.00'),
            stock_quantity=150,
            sku='BRICK-RED-001'
        )

        ProductVariant.objects.create(
            product=bricks1,
            variant_name='Hollow',
            variant_type='MATERIAL',
            additional_price=Decimal('500.00'),
            stock_quantity=100,
            sku='BRICK-HOLLOW-001'
        )

        bricks2 = Product.objects.create(
            name='Fire Bricks',
            description='Heat resistant fire bricks for furnaces',
            category=bricks_cat,
            base_price=Decimal('6000.00'),
            image_url='https://via.placeholder.com/300?text=Fire+Bricks',
            is_active=True
        )

        ProductVariant.objects.create(
            product=bricks2,
            variant_name='Grade A',
            variant_type='MATERIAL',
            additional_price=Decimal('0.00'),
            stock_quantity=80,
            sku='FIRE-BRICK-GA-001'
        )

        # TMT Iron Rods Products
        tmt1 = Product.objects.create(
            name='TMT Iron Rod 8mm',
            description='High strength TMT iron rods for structural reinforcement',
            category=tmt_cat,
            base_price=Decimal('45.00'),
            image_url='https://via.placeholder.com/300?text=TMT+8mm',
            is_active=True
        )

        ProductVariant.objects.create(
            product=tmt1,
            variant_name='8mm Dia',
            variant_type='SIZE',
            additional_price=Decimal('0.00'),
            stock_quantity=1000,
            sku='TMT-8MM-001'
        )

        tmt2 = Product.objects.create(
            name='TMT Iron Rod 10mm',
            description='High strength TMT iron rods for structural reinforcement',
            category=tmt_cat,
            base_price=Decimal('55.00'),
            image_url='https://via.placeholder.com/300?text=TMT+10mm',
            is_active=True
        )

        ProductVariant.objects.create(
            product=tmt2,
            variant_name='10mm Dia',
            variant_type='SIZE',
            additional_price=Decimal('0.00'),
            stock_quantity=800,
            sku='TMT-10MM-001'
        )

        ProductVariant.objects.create(
            product=tmt2,
            variant_name='12mm Dia',
            variant_type='SIZE',
            additional_price=Decimal('8.00'),
            stock_quantity=600,
            sku='TMT-12MM-001'
        )

        tmt3 = Product.objects.create(
            name='TMT Iron Rod 16mm',
            description='Heavy duty TMT iron rods for major structural work',
            category=tmt_cat,
            base_price=Decimal('75.00'),
            image_url='https://via.placeholder.com/300?text=TMT+16mm',
            is_active=True
        )

        ProductVariant.objects.create(
            product=tmt3,
            variant_name='16mm Dia',
            variant_type='SIZE',
            additional_price=Decimal('0.00'),
            stock_quantity=400,
            sku='TMT-16MM-001'
        )

        self.stdout.write(self.style.SUCCESS('Successfully added 8 products with 12 variants'))
