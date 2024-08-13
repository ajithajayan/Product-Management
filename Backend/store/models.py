from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
import os
import barcode
from barcode.writer import ImageWriter
from django.db import models
from django.core.validators import MinValueValidator
from django.utils.crypto import get_random_string
from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save
from django.utils.crypto import get_random_string
import barcode
from barcode.writer import ImageWriter
from io import BytesIO

# Supplier model
class Supplier(models.Model):
    name = models.CharField(max_length=255)
    mobile_number = models.CharField(max_length=15)
    email = models.EmailField(unique=True)
    location = models.CharField(max_length=255)

    def __str__(self):
        return self.name

# Category model
class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

# Brand model
class Brand(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name



class Product(models.Model):
    name = models.CharField(max_length=255)
    purchase_date = models.DateField()
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='products')
    unit_type = models.CharField(max_length=100, default='pieces')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='products')
    expiry_date = models.DateField()
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(0)])
    manufacturing_date = models.DateField()
    product_code = models.CharField(max_length=100, blank=True, null=True)  # Allow null and blank
    barcode = models.CharField(max_length=100, unique=True, blank=True, null=True)
    opening_stock = models.PositiveIntegerField(default=0)

    def save(self, *args, **kwargs):
        # Generate a product code if not provided
        if not self.product_code:
            last_product = Product.objects.filter(product_code__startswith='P').order_by('-id').first()
            if last_product and last_product.product_code:
                last_code = int(last_product.product_code[1:])  # Strip the 'P' and convert to int
                self.product_code = f'P{last_code + 1}'
            else:
                self.product_code = 'P5001'  # Start from P5001 if no products exist

        # Generate barcode if not provided
        if not self.barcode:
            self.barcode = self.generate_unique_barcode()
        
        super().save(*args, **kwargs)

    def generate_unique_barcode(self):
        while True:
            barcode_number = get_random_string(12, allowed_chars='0123456789')
            if not Product.objects.filter(barcode=barcode_number).exists():
                return barcode_number


class TotalStock(models.Model):
    product_code = models.CharField(max_length=100, unique=True)
    total_quantity = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.product_code}: {self.total_quantity}"

@receiver(pre_save, sender=Product)
def set_opening_stock(sender, instance, **kwargs):
    if not instance._state.adding and instance.product_code:
        existing_total = TotalStock.objects.filter(product_code=instance.product_code).first()
        if existing_total:
            instance.opening_stock = existing_total.total_quantity

@receiver(post_save, sender=Product)
def update_total_stock(sender, instance, created, **kwargs):
    total_stock, _ = TotalStock.objects.get_or_create(product_code=instance.product_code)
    if created:
        total_stock.total_quantity += instance.quantity
    else:
        # Recalculate total stock to handle manual edits to quantity
        total_stock.total_quantity = Product.objects.filter(product_code=instance.product_code).aggregate(total=models.Sum('quantity'))['total'] or 0
    total_stock.save()


# Branch model
class Branch(models.Model):
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    branch_code = models.CharField(max_length=10, primary_key=True, unique=True, blank=True)
    contact_details = models.CharField(max_length=15)

    def save(self, *args, **kwargs):
        if not self.branch_code:
            last_branch = Branch.objects.order_by('-branch_code').first()
            if last_branch and last_branch.branch_code.startswith("BR"):
                last_code = int(last_branch.branch_code[2:])
                new_code = last_code + 1
            else:
                new_code = 121211
            self.branch_code = f'BR{new_code}'

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

# Inventory Transaction models
class ProductInTransaction(models.Model):
    date = models.DateField()
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='in_transactions')
    supplier_invoice_number = models.CharField(max_length=100, unique=True)
    total_qty_amount = models.PositiveIntegerField(validators=[MinValueValidator(1)])

class ProductInTransactionDetail(models.Model):
    transaction = models.ForeignKey(ProductInTransaction, on_delete=models.CASCADE, related_name='details')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='in_transaction_details')
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    total = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    remarks = models.TextField(blank=True, null=True)

class ProductOutTransaction(models.Model):
    date = models.DateField()
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='out_transactions')
    branch_incharge = models.CharField(max_length=255)
    supplier_invoice_number = models.CharField(max_length=100, unique=True)
    total_qty_amount = models.PositiveIntegerField(validators=[MinValueValidator(1)])

class ProductOutTransactionDetail(models.Model):
    transaction = models.ForeignKey(ProductOutTransaction, on_delete=models.CASCADE, related_name='details')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='out_transaction_details')
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    total = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    remarks = models.TextField(blank=True, null=True)

class PurchaseRequest(models.Model):
    date = models.DateField()
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='purchase_requests')
    order_form_number = models.CharField(max_length=100, unique=True)
    branch_incharge = models.CharField(max_length=255)
    total_qty_amount = models.PositiveIntegerField(validators=[MinValueValidator(1)])

class PurchaseRequestDetail(models.Model):
    request = models.ForeignKey(PurchaseRequest, on_delete=models.CASCADE, related_name='details')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='purchase_request_details')
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    total = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    remarks = models.TextField(blank=True, null=True)

class DamageProductTransaction(models.Model):
    date = models.DateField()
    damage_transfer_number = models.CharField(max_length=100, unique=True)
    total_qty_amount = models.PositiveIntegerField(validators=[MinValueValidator(1)])

class DamageProductTransactionDetail(models.Model):
    transaction = models.ForeignKey(DamageProductTransaction, on_delete=models.CASCADE, related_name='details')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='damage_transaction_details')
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    total = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    remarks = models.TextField(blank=True, null=True)
 

