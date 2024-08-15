from rest_framework import serializers
from store.models import (
    Supplier, Category, Brand, Product, Branch,
    ProductInTransaction, ProductInTransactionDetail,TotalStock,ProductOutTransaction, ProductOutTransactionDetail
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
    category_name = serializers.CharField(source='category.name', read_only=True)
    brand_name = serializers.CharField(source='brand.name', read_only=True)
    total_stock = serializers.SerializerMethodField()
    latest_transaction_detail = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'product_code', 'barcode', 'category_name', 'brand_name',
            'total_stock', 'latest_transaction_detail',
        ]
        extra_kwargs = {
            'barcode': {'read_only': True},
            'product_code': {'required': False, 'allow_blank': True},
            'category': {'write_only': True},
            'brand': {'write_only': True},
        }

    def get_total_stock(self, obj):
        try:
            stock = TotalStock.objects.get(product=obj)
            return stock.total_quantity
        except TotalStock.DoesNotExist:
            return 0

    def get_latest_transaction_detail(self, obj):
        detail = ProductInTransactionDetail.objects.filter(product=obj).order_by('-id').first()
        if detail:
            return {
                "manufacturing_date": detail.manufacturing_date,
                "expiry_date": detail.expiry_date,
                "supplier_name": detail.transaction.supplier.name,
                "quantity": detail.quantity,
            }
        return None

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
        extra_kwargs = {
            'transaction': {'required': False},  # transaction will be set in the parent serializer
            'total': {'required': True},  # total is required and should be included in the request
            'product': {'required': True}  # product should be the primary key (id)
        }

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
    


class InventorySerializer(serializers.ModelSerializer):
    product_code = serializers.CharField(source='product.product_code')
    name = serializers.CharField(source='product.name')
    barcode = serializers.CharField(source='product.barcode')
    category_name = serializers.CharField(source='product.category.name')
    brand_name = serializers.CharField(source='product.brand.name')
    supplier_name = serializers.CharField(source='transaction.supplier.name')
    purchase_date = serializers.DateField(source='transaction.purchase_date')
    stock_quantity = serializers.IntegerField(source='quantity')  # Changed to stock_quantity

    class Meta:
        model = ProductInTransactionDetail
        fields = [
            'product_code', 'name', 'barcode', 'category_name', 'brand_name',
            'supplier_name', 'purchase_date', 'stock_quantity', 'manufacturing_date',
            'expiry_date'
        ]


class ProductOutTransactionDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductOutTransactionDetail
        fields = '__all__'

class ProductOutTransactionSerializer(serializers.ModelSerializer):
    transaction_details = ProductOutTransactionDetailSerializer(many=True)

    class Meta:
        model = ProductOutTransaction
        fields = '__all__'

    def create(self, validated_data):
        transaction_details_data = validated_data.pop('transaction_details')
        transaction = ProductOutTransaction.objects.create(**validated_data)

        for detail_data in transaction_details_data:
            # This will call the create method in ProductOutTransactionDetailSerializer, which handles the stock deduction
            ProductOutTransactionDetail.objects.create(transaction=transaction, **detail_data)

        return transaction