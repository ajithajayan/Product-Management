from rest_framework import serializers
from store.models import (
    Supplier, Category, Brand, Product, Branch,
    ProductInTransaction, ProductInTransactionDetail,TotalStock
)
from django.utils.crypto import get_random_string

# Supplier Serializer
class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = '__all__'

# Category Serializer
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

# Brand Serializer
class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    # Add fields to get the name of the related objects
    category_name = serializers.CharField(source='category.name', read_only=True)
    brand_name = serializers.CharField(source='brand.name', read_only=True)

    class Meta:
        model = Product
        fields = '__all__'
        extra_kwargs = {
            'barcode': {'read_only': True},  # Barcode is read-only since it's generated automatically
            'product_code': {'required': False, 'allow_blank': True},  # Product code is optional
            'category': {'write_only': True},  # Keep category ID write-only
            'brand': {'write_only': True},     # Keep brand ID write-only
        }

    def create(self, validated_data):
        if not validated_data.get('product_code'):
            last_product = Product.objects.filter(product_code__startswith='P').order_by('-id').first()
            if last_product and last_product.product_code:
                last_code = int(last_product.product_code[1:])  # Strip the 'P' and convert to int
                validated_data['product_code'] = f'P{last_code + 1}'
            else:
                validated_data['product_code'] = 'P5001'  # Start from P5001 if no products exist
        return super().create(validated_data)
    
# Branch Serializer
class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields = '__all__'

# Product In Transaction Detail Serializer
class ProductInTransactionDetailSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = ProductInTransactionDetail
        fields = '__all__'

# Product In Transaction Serializer
class ProductInTransactionSerializer(serializers.ModelSerializer):
    transaction_details = ProductInTransactionDetailSerializer(many=True, write_only=True)

    class Meta:
        model = ProductInTransaction
        fields = '__all__'

    def create(self, validated_data):
        details_data = validated_data.pop('transaction_details')
        transaction = ProductInTransaction.objects.create(**validated_data)
        
        for detail_data in details_data:
            ProductInTransactionDetail.objects.create(transaction=transaction, **detail_data)
            # Update total stock for each product in the transaction
            product_total_stock, created = TotalStock.objects.get_or_create(product=detail_data['product'])
            product_total_stock.total_quantity += detail_data['quantity']
            product_total_stock.save()

        return transaction

    def update(self, instance, validated_data):
        details_data = validated_data.pop('transaction_details')
        instance.supplier = validated_data.get('supplier', instance.supplier)
        instance.purchase_date = validated_data.get('purchase_date', instance.purchase_date)
        instance.supplier_invoice_number = validated_data.get('supplier_invoice_number', instance.supplier_invoice_number)
        instance.supplier_date = validated_data.get('supplier_date', instance.supplier_date)
        instance.remarks = validated_data.get('remarks', instance.remarks)
        instance.save()

        # Handle updating transaction details
        for detail_data in details_data:
            detail_id = detail_data.get('id')
            if detail_id:
                detail_instance = ProductInTransactionDetail.objects.get(id=detail_id, transaction=instance)
                detail_instance.product = detail_data.get('product', detail_instance.product)
                detail_instance.manufacturing_date = detail_data.get('manufacturing_date', detail_instance.manufacturing_date)
                detail_instance.expiry_date = detail_data.get('expiry_date', detail_instance.expiry_date)
                detail_instance.quantity = detail_data.get('quantity', detail_instance.quantity)
                detail_instance.total = detail_data.get('total', detail_instance.total)
                detail_instance.save()
            else:
                ProductInTransactionDetail.objects.create(transaction=instance, **detail_data)
                # Update stock for the new details
                product_total_stock, created = TotalStock.objects.get_or_create(product=detail_data['product'])
                product_total_stock.total_quantity += detail_data['quantity']
                product_total_stock.save()

        return instance
