from rest_framework import serializers
from store.models import (
    Supplier, Category, Brand, Product, Branch,
    ProductInTransaction, ProductInTransactionDetail,
    ProductOutTransaction, ProductOutTransactionDetail,
    PurchaseRequest, PurchaseRequestDetail,
    DamageProductTransaction, DamageProductTransactionDetail
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

# Product Serializer
class ProductSerializer(serializers.ModelSerializer):
    # Add fields to get the name of the related objects
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    brand_name = serializers.CharField(source='brand.name', read_only=True)

    class Meta:
        model = Product
        fields = '__all__'
        extra_kwargs = {
            'barcode': {'read_only': True},
            'product_code': {'required': False, 'allow_blank': True},
            'supplier': {'write_only': True},  # Keep supplier ID write-only
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
    class Meta:
        model = ProductInTransactionDetail
        fields = '__all__'

# Product In Transaction Serializer
class ProductInTransactionSerializer(serializers.ModelSerializer):
    details = ProductInTransactionDetailSerializer(many=True)

    class Meta:
        model = ProductInTransaction
        fields = '__all__'

    def create(self, validated_data):
        details_data = validated_data.pop('details')
        transaction = ProductInTransaction.objects.create(**validated_data)
        for detail_data in details_data:
            ProductInTransactionDetail.objects.create(transaction=transaction, **detail_data)
        return transaction

# Product Out Transaction Detail Serializer
class ProductOutTransactionDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductOutTransactionDetail
        fields = '__all__'

# Product Out Transaction Serializer
class ProductOutTransactionSerializer(serializers.ModelSerializer):
    details = ProductOutTransactionDetailSerializer(many=True)

    class Meta:
        model = ProductOutTransaction
        fields = '__all__'

    def create(self, validated_data):
        details_data = validated_data.pop('details')
        transaction = ProductOutTransaction.objects.create(**validated_data)
        for detail_data in details_data:
            ProductOutTransactionDetail.objects.create(transaction=transaction, **detail_data)
        return transaction

# Purchase Request Detail Serializer
class PurchaseRequestDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseRequestDetail
        fields = '__all__'

# Purchase Request Serializer
class PurchaseRequestSerializer(serializers.ModelSerializer):
    details = PurchaseRequestDetailSerializer(many=True)

    class Meta:
        model = PurchaseRequest
        fields = '__all__'

    def create(self, validated_data):
        details_data = validated_data.pop('details')
        request = PurchaseRequest.objects.create(**validated_data)
        for detail_data in details_data:
            PurchaseRequestDetail.objects.create(request=request, **detail_data)
        return request

# Damage Product Transaction Detail Serializer
class DamageProductTransactionDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = DamageProductTransactionDetail
        fields = '__all__'

# Damage Product Transaction Serializer
class DamageProductTransactionSerializer(serializers.ModelSerializer):
    details = DamageProductTransactionDetailSerializer(many=True)

    class Meta:
        model = DamageProductTransaction
        fields = '__all__'

    def create(self, validated_data):
        details_data = validated_data.pop('details')
        transaction = DamageProductTransaction.objects.create(**validated_data)
        for detail_data in details_data:
            DamageProductTransactionDetail.objects.create(transaction=transaction, **detail_data)
        return transaction
