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
from django.utils import timezone

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



# Product Model
class Product(models.Model):
    name = models.CharField(max_length=255)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='products')
    unit_type = models.CharField(max_length=100, default='pieces')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='products')
    product_code = models.CharField(max_length=100, blank=True, null=True)  # Allow null and blank
    barcode = models.CharField(max_length=100, unique=True, blank=True, null=True)

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

    def __str__(self):
        return self.name

# ProductInTransaction Model
class ProductInTransaction(models.Model):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    purchase_date = models.DateField(default=timezone.now)
    supplier_invoice_number = models.CharField(max_length=100)
    supplier_date = models.DateField()  # Date provided by the supplier
    remarks = models.TextField(blank=True, null=True)  # Remarks or comments about the transaction

    def save(self, *args, **kwargs):
        super(ProductInTransaction, self).save(*args, **kwargs)
        # Update stock for all products after the transaction is saved
        for detail in self.transaction_details.all():
            product_total_stock, created = TotalStock.objects.get_or_create(product=detail.product)
            product_total_stock.total_quantity += detail.quantity
            product_total_stock.save()

    def __str__(self):
        return f"Transaction {self.id} - {self.supplier.name} on {self.purchase_date}"

# ProductInTransactionDetail Model
class ProductInTransactionDetail(models.Model):
    transaction = models.ForeignKey(ProductInTransaction, on_delete=models.CASCADE, related_name='transaction_details')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    manufacturing_date = models.DateField()
    expiry_date = models.DateField()
    quantity = models.PositiveIntegerField()
    total = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        # We won't update the stock here; it will be done after the entire transaction is saved.
        super(ProductInTransactionDetail, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} - {self.quantity} units"

# TotalStock Model
class TotalStock(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE)
    total_quantity = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.product.name}: {self.total_quantity} units"


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


 

