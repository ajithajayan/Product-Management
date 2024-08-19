from rest_framework import serializers
from django.db.models import Sum

from store.models import (
    Supplier, Category, Brand, Product, Branch,
    ProductInTransaction, ProductInTransactionDetail, TotalStock, ProductOutTransaction, ProductOutTransactionDetail, ExpiredProduct, DefectiveProduct
)
from django.utils.crypto import get_random_string
from django.db import transaction

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
        extra_kwargs = {
            'transaction': {'required': False},
            'total': {'required': True},
            'product': {'required': True},
            'purchased_quantity': {'read_only': True},
            'remaining_quantity': {'read_only': True},
        }


    def create(self, validated_data):
        validated_data['purchased_quantity'] = validated_data['quantity']
        validated_data['remaining_quantity'] = validated_data['quantity']
        return super().create(validated_data)
         

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
            # Check if a similar product with the same manufacturing and expiry date exists
            existing_detail = ProductInTransactionDetail.objects.filter(
                product=detail_data['product'],
                manufacturing_date=detail_data['manufacturing_date'],
                expiry_date=detail_data['expiry_date'],
                transaction__supplier=transaction.supplier  # Match the supplier as well
            ).first()

            if existing_detail:
                # Update the existing detail's purchased_quantity and total
                existing_detail.quantity += detail_data['quantity']
                existing_detail.total += detail_data['total']
                existing_detail.purchased_quantity += detail_data['quantity']
                existing_detail.remaining_quantity += detail_data['quantity']  # Update remaining_quantity
                existing_detail.save()
            else:
                # Create a new detail entry
                ProductInTransactionDetail.objects.create(
                    transaction=transaction,
                    purchased_quantity=detail_data['quantity'],
                    remaining_quantity=detail_data['quantity'],  # Set remaining_quantity
                    **detail_data
                )

            # Update total stock for each product in the transaction
            product_total_stock, created = TotalStock.objects.get_or_create(product=detail_data['product'])
            product_total_stock.total_quantity += detail_data['quantity']
            product_total_stock.remaining_quantity += detail_data['quantity']  # Update remaining_quantity in TotalStock
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
                detail_instance.remaining_quantity += detail_data['quantity']  # Update remaining_quantity
                detail_instance.save()
            else:
                # Check if a similar product with the same manufacturing and expiry date exists
                existing_detail = ProductInTransactionDetail.objects.filter(
                    transaction=instance,
                    product=detail_data['product'],
                    manufacturing_date=detail_data['manufacturing_date'],
                    expiry_date=detail_data['expiry_date']
                ).first()

                if existing_detail:
                    # Update the existing detail's quantity and total
                    existing_detail.quantity += detail_data['quantity']
                    existing_detail.total += detail_data['total']
                    existing_detail.remaining_quantity += detail_data['quantity']  # Update remaining_quantity
                    existing_detail.save()
                else:
                    # Create a new detail entry
                    ProductInTransactionDetail.objects.create(
                        transaction=instance,
                        purchased_quantity=detail_data['quantity'],
                        remaining_quantity=detail_data['quantity'],  # Set remaining_quantity
                        **detail_data
                    )

                # Update stock for the new details
                product_total_stock, created = TotalStock.objects.get_or_create(product=detail_data['product'])
                product_total_stock.total_quantity += detail_data['quantity']
                product_total_stock.remaining_quantity += detail_data['quantity']  # Update remaining_quantity in TotalStock
                product_total_stock.save()

        return instance





# Inventory Serializer
class InventorySerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(source='product.id', read_only=True)
    product_code = serializers.CharField(source='product.product_code', read_only=True)
    name = serializers.CharField(source='product.name', read_only=True)
    barcode = serializers.CharField(source='product.barcode', read_only=True)
    category_name = serializers.CharField(source='product.category.name', read_only=True)
    brand_name = serializers.CharField(source='product.brand.name', read_only=True)
    supplier_name = serializers.CharField(source='transaction.supplier.name', read_only=True)
    purchase_date = serializers.DateField(source='transaction.purchase_date', read_only=True)
    purchased_quantity = serializers.IntegerField(source='quantity', read_only=True)
    remaining_quantity = serializers.IntegerField(read_only=True)
    manufacturing_date = serializers.DateField(read_only=True)
    expiry_date = serializers.DateField(read_only=True)

    class Meta:
        model = ProductInTransactionDetail
        fields = [
            'product_id', 'product_code', 'name', 'barcode', 'category_name', 'brand_name', 
            'supplier_name', 'purchase_date', 'purchased_quantity', 'remaining_quantity', 
            'manufacturing_date', 'expiry_date'
        ]


class ProductOutTransactionDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductOutTransactionDetail
        fields = ['product', 'qty_requested']

    def create(self, validated_data):
        product = validated_data['product']
        qty_requested = validated_data['qty_requested']

        # Fetch the total stock and update remaining quantity in ProductInTransactionDetail
        with transaction.atomic():
            in_transaction_details = ProductInTransactionDetail.objects.filter(product=product).order_by('expiry_date')

            remaining_qty_needed = qty_requested

            for detail in in_transaction_details:
                if detail.remaining_quantity >= remaining_qty_needed:
                    detail.remaining_quantity -= remaining_qty_needed
                    detail.save()
                    break
                else:
                    remaining_qty_needed -= detail.remaining_quantity
                    detail.remaining_quantity = 0
                    detail.save()

            # Update the total stock in TotalStock
            product_total_stock = TotalStock.objects.get(product=product)
            if product_total_stock.total_quantity >= qty_requested:
                product_total_stock.total_quantity -= qty_requested
                product_total_stock.save()
            else:
                raise serializers.ValidationError("Not enough stock to fulfill the request.")

        return super().create(validated_data)


class ProductOutTransactionSerializer(serializers.ModelSerializer):
    transaction_details = ProductOutTransactionDetailSerializer(many=True)

    class Meta:
        model = ProductOutTransaction
        fields = ['date', 'branch', 'transfer_invoice_number', 'branch_in_charge', 'transaction_details', 'remarks']

    def create(self, validated_data):
        transaction_details_data = validated_data.pop('transaction_details')
        transaction = ProductOutTransaction.objects.create(**validated_data)

        for detail_data in transaction_details_data:
            ProductOutTransactionDetail.objects.create(transaction=transaction, **detail_data)

        return transaction




class ExpiredProductSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(source='product.id', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_code = serializers.CharField(source='product.product_code', read_only=True)
    brand_name = serializers.CharField(source='product.brand.name', read_only=True)
    category_name = serializers.CharField(source='product.category.name', read_only=True)

    class Meta:
        model = ExpiredProduct
        fields = ['id', 'product_id', 'product_name', 'product_code', 'brand_name', 'category_name', 'qty_expired', 'expiry_date', 'remarks']


class DefectiveProductSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(source='product.id', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_code = serializers.CharField(source='product.product_code', read_only=True)
    brand_name = serializers.CharField(source='product.brand.name', read_only=True)
    category_name = serializers.CharField(source='product.category.name', read_only=True)

    class Meta:
        model = DefectiveProduct
        fields = ['id', 'product_id', 'product_name', 'product_code', 'brand_name', 'category_name', 'qty_defective', 'remarks']




#  **************************** Reports serializer ****************************************


class InwardQtyReportSerializer(serializers.ModelSerializer):
    supplier_name = serializers.CharField(source='transaction.supplier.name', read_only=True)
    product_detail = serializers.CharField(source='product.name', read_only=True)
    date = serializers.DateField(source='transaction.purchase_date', read_only=True)
    invoice_number = serializers.CharField(source='transaction.supplier_invoice_number', read_only=True)

    class Meta:
        model = ProductInTransactionDetail
        fields = ['date', 'invoice_number', 'supplier_name', 'product_detail', 'quantity']


class OutwardQtyReportSerializer(serializers.ModelSerializer):
    branch_name = serializers.CharField(source='transaction.branch.name', read_only=True)
    branch_code = serializers.CharField(source='transaction.branch.branch_code', read_only=True)
    product_detail = serializers.CharField(source='product.name', read_only=True)
    date = serializers.DateField(source='transaction.date', read_only=True)
    transfer_invoice_number = serializers.CharField(source='transaction.transfer_invoice_number', read_only=True)

    class Meta:
        model = ProductOutTransactionDetail
        fields = ['date', 'transfer_invoice_number', 'branch_name', 'branch_code', 'product_detail', 'qty_requested']


class BranchWiseReportSerializer(serializers.ModelSerializer):
    branch_name = serializers.CharField(source='transaction.branch.name', read_only=True)
    branch_code = serializers.CharField(source='transaction.branch.branch_code', read_only=True)
    product_detail = serializers.CharField(source='product.name', read_only=True)
    date = serializers.DateField(source='transaction.date', read_only=True)
    transfer_invoice_number = serializers.CharField(source='transaction.transfer_invoice_number', read_only=True)

    class Meta:
        model = ProductOutTransactionDetail
        fields = ['date', 'transfer_invoice_number', 'branch_name', 'branch_code', 'product_detail', 'qty_requested']



class ExpiredProductReportSerializer(serializers.ModelSerializer):
    product_detail = serializers.CharField(source='product.name', read_only=True)
    supplier_name = serializers.CharField(source='product.productintransactiondetail.transaction.supplier.name', read_only=True)
    supplier_invoice_number = serializers.CharField(source='product.productintransactiondetail.transaction.supplier_invoice_number', read_only=True)

    class Meta:
        model = ExpiredProduct
        fields = ['removal_date', 'supplier_invoice_number', 'supplier_name', 'product_detail', 'qty_expired', 'expiry_date']

class SupplierWiseReportSerializer(serializers.ModelSerializer):
    supplier_name = serializers.CharField(source='transaction.supplier.name', read_only=True)
    product_detail = serializers.CharField(source='product.name', read_only=True)
    date = serializers.DateField(source='transaction.purchase_date', read_only=True)
    supplier_invoice_number = serializers.CharField(source='transaction.supplier_invoice_number', read_only=True)

    class Meta:
        model = ProductInTransactionDetail
        fields = ['date', 'supplier_invoice_number', 'supplier_name', 'product_detail', 'quantity', 'expiry_date']

class ProductDetailsReportSerializer(serializers.ModelSerializer):
    outward_qty = serializers.SerializerMethodField()
    date = serializers.DateField(source='transaction.purchase_date')
    supplier_invoice_number = serializers.CharField(source='transaction.supplier_invoice_number')
    supplier_name = serializers.CharField(source='transaction.supplier.name')
    product_detail = serializers.CharField(source='product.name')

    class Meta:
        model = ProductInTransactionDetail
        fields = [
            'date',
            'supplier_invoice_number',  # Valid field path
            'supplier_name',  # Valid field path
            'product_detail',  # Valid field path
            'manufacturing_date',
            'expiry_date',
            'quantity',
            'purchased_quantity',
            'remaining_quantity',
            'outward_qty',
        ]

    def get_outward_qty(self, obj):
        outward_qty = ProductOutTransactionDetail.objects.filter(product=obj.product).aggregate(total_out=Sum('qty_requested'))['total_out']
        return outward_qty if outward_qty else 0

