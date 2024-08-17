from django.utils import timezone
from rest_framework import generics, status
from rest_framework.response import Response
from store.models import (
    Supplier, Category, Brand, Product, Branch,
    ProductInTransaction, ProductInTransactionDetail, TotalStock, ProductOutTransaction, ExpiredProduct, DefectiveProduct
)
from .serializers import (
    ExpiredProductSerializer, SupplierSerializer, CategorySerializer, BrandSerializer, ProductSerializer, BranchSerializer,
    ProductInTransactionSerializer, InventorySerializer, ProductOutTransactionSerializer, DefectiveProductSerializer
)
from rest_framework.views import APIView
from rest_framework import generics
from django.db.models import F, Value, Case, When, IntegerField
from django.db import transaction

# Supplier Views
class SupplierListCreateView(generics.ListCreateAPIView):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer

class SupplierDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer

# Category Views
class CategoryListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

# Brand Views
class BrandListCreateView(generics.ListCreateAPIView):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer

class BrandDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer

# Product Views
class ProductListCreateView(generics.ListCreateAPIView):
    queryset = Product.objects.select_related('brand', 'category').all()
    serializer_class = ProductSerializer

class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def perform_destroy(self, instance):
        # Decrease stock from TotalStock when a product is deleted, if necessary
        try:
            total_stock = TotalStock.objects.get(product=instance)
            total_stock.total_quantity = 0
            total_stock.save()
        except TotalStock.DoesNotExist:
            pass
        
        instance.delete()

# Get total stock of a product
class GetTotalStockView(APIView):
    def get(self, request, product_code, format=None):
        try:
            product = Product.objects.get(product_code=product_code)
            total_stock = TotalStock.objects.get(product=product)
            return Response({'total_stock': total_stock.total_quantity}, status=status.HTTP_200_OK)
        except (Product.DoesNotExist, TotalStock.DoesNotExist):
            return Response({'error': 'Product not found or stock not available'}, status=status.HTTP_404_NOT_FOUND)

# Search product codes
class ProductCodeSearchView(APIView):
    def get(self, request, format=None):
        query = request.GET.get('query', '')
        if query:
            products = Product.objects.filter(product_code__icontains=query)[:10]
            product_codes = products.values('product_code')
            return Response(product_codes, status=status.HTTP_200_OK)
        return Response({'error': 'No query provided'}, status=status.HTTP_400_BAD_REQUEST)

# Branch Views
class BranchListCreateView(generics.ListCreateAPIView):
    queryset = Branch.objects.all()
    serializer_class = BranchSerializer

class BranchDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Branch.objects.all()
    serializer_class = BranchSerializer
    lookup_field = 'branch_code'

# Product In Transaction Views
class ProductInTransactionListCreateView(generics.ListCreateAPIView):
    queryset = ProductInTransaction.objects.all()
    serializer_class = ProductInTransactionSerializer

class ProductInTransactionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ProductInTransaction.objects.all()
    serializer_class = ProductInTransactionSerializer

    def perform_destroy(self, instance):
        # Decrease stock from TotalStock when a transaction is deleted
        for detail in instance.transaction_details.all():
            product_total_stock = TotalStock.objects.get(product=detail.product)
            product_total_stock.total_quantity -= detail.quantity
            product_total_stock.save()
        
        instance.delete()



class InventoryListView(generics.ListAPIView):
    serializer_class = InventorySerializer

    def get_queryset(self):
        # Get the current date
        current_date = timezone.now().date()

        # Check if the expired filter is active
        expired = self.request.query_params.get('expired')

        queryset = ProductInTransactionDetail.objects.select_related(
            'product', 'product__category', 'product__brand',
            'transaction', 'transaction__supplier',
        ).annotate(
            product_code=F('product__product_code'),
            name=F('product__name'),
            barcode=F('product__barcode'),
            category_name=F('product__category__name'),
            brand_name=F('product__brand__name'),
            supplier_name=F('transaction__supplier__name'),
            purchase_date=F('transaction__purchase_date'),
            stock_quantity=F('quantity'),  # Change 'quantity' to 'stock_quantity'
        )

        if expired == "true":
            queryset = queryset.filter(expiry_date__lt=current_date)

        return queryset
    

# Product Transaction Out format
class ProductOutTransactionListCreateView(generics.ListCreateAPIView):
    queryset = ProductOutTransaction.objects.all()
    serializer_class = ProductOutTransactionSerializer




# View to remove expired products and track them
class RemoveExpiredProductView(APIView):
    def post(self, request, *args, **kwargs):
        product_id = request.data.get('product_id')
        qty_to_remove = request.data.get('qty_to_remove', None)
        remarks = request.data.get('remarks', '')

        if not product_id or qty_to_remove is None:
            return Response({"error": "Product ID and quantity to remove are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                in_transaction_details = ProductInTransactionDetail.objects.filter(product_id=product_id, expiry_date__lt=date.today()).order_by('expiry_date')

                remaining_qty_needed = qty_to_remove

                for detail in in_transaction_details:
                    if remaining_qty_needed <= 0:
                        break

                    if detail.remaining_quantity >= remaining_qty_needed:
                        ExpiredProduct.objects.create(
                            product_id=product_id,
                            qty_expired=remaining_qty_needed,
                            expiry_date=detail.expiry_date,
                            remarks=remarks
                        )

                        detail.remaining_quantity -= remaining_qty_needed
                        detail.save()
                        remaining_qty_needed = 0
                    else:
                        ExpiredProduct.objects.create(
                            product_id=product_id,
                            qty_expired=detail.remaining_quantity,
                            expiry_date=detail.expiry_date,
                            remarks=remarks
                        )

                        remaining_qty_needed -= detail.remaining_quantity
                        detail.remaining_quantity = 0
                        detail.save()

                # Update total stock after removal
                total_stock = TotalStock.objects.get(product_id=product_id)
                total_stock.total_quantity -= qty_to_remove
                total_stock.save()

            return Response({"success": "Expired product removed from inventory and details tracked."}, status=status.HTTP_200_OK)
        except ProductInTransactionDetail.DoesNotExist:
            return Response({"error": "Product not found or already removed."}, status=status.HTTP_404_NOT_FOUND)
        except TotalStock.DoesNotExist:
            return Response({"error": "Total stock not found for this product."}, status=status.HTTP_404_NOT_FOUND)

# View to remove defective products and track them
class RemoveDefectiveProductView(APIView):
    def post(self, request, *args, **kwargs):
        product_id = request.data.get('product_id')
        qty_to_remove = request.data.get('qty_to_remove', None)
        remarks = request.data.get('remarks', '')

        if not product_id or qty_to_remove is None:
            return Response({"error": "Product ID and quantity to remove are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                in_transaction_details = ProductInTransactionDetail.objects.filter(product_id=product_id).order_by('expiry_date')

                remaining_qty_needed = qty_to_remove

                for detail in in_transaction_details:
                    if remaining_qty_needed <= 0:
                        break

                    if detail.remaining_quantity >= remaining_qty_needed:
                        DefectiveProduct.objects.create(
                            product_id=product_id,
                            qty_defective=remaining_qty_needed,
                            remarks=remarks
                        )

                        detail.remaining_quantity -= remaining_qty_needed
                        detail.save()
                        remaining_qty_needed = 0
                    else:
                        DefectiveProduct.objects.create(
                            product_id=product_id,
                            qty_defective=detail.remaining_quantity,
                            remarks=remarks
                        )

                        remaining_qty_needed -= detail.remaining_quantity
                        detail.remaining_quantity = 0
                        detail.save()

                # Update total stock after removal
                total_stock = TotalStock.objects.get(product_id=product_id)
                total_stock.total_quantity -= qty_to_remove
                total_stock.save()

            return Response({"success": "Defective product removed from inventory and details tracked."}, status=status.HTTP_200_OK)
        except ProductInTransactionDetail.DoesNotExist:
            return Response({"error": "Product not found or already removed."}, status=status.HTTP_404_NOT_FOUND)
        except TotalStock.DoesNotExist:
            return Response({"error": "Total stock not found for this product."}, status=status.HTTP_404_NOT_FOUND)


# List view to display all tracked expired products
class TrackedExpiredProductListView(generics.ListAPIView):
    queryset = ExpiredProduct.objects.select_related('product').all()
    serializer_class = ExpiredProductSerializer

# List view to display expired products that are still in stock
from django.db import transaction
from datetime import date

# View to list expired products that have not been removed yet
class ExpiredProductListView(generics.ListAPIView):
    serializer_class = InventorySerializer

    def get_queryset(self):
        current_date = timezone.now().date()
        return ProductInTransactionDetail.objects.select_related(
            'product', 'product__category', 'product__brand', 'transaction', 'transaction__supplier'
        ).filter(
            expiry_date__lt=current_date,
            remaining_quantity__gt=0  # Ensures only products with remaining stock are shown
        )

# View to remove expired products and mark them as removed
class RemoveExpiredProductView(APIView):
    def post(self, request, *args, **kwargs):
        product_id = request.data.get('product_id')
        qty_to_remove = request.data.get('qty_to_remove', None)
        remarks = request.data.get('remarks', '')

        if not product_id or qty_to_remove is None:
            return Response({"error": "Product ID and quantity to remove are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                in_transaction_details = ProductInTransactionDetail.objects.filter(
                    product_id=product_id, 
                    expiry_date__lt=date.today(),
                    remaining_quantity__gt=0  # Only handle products with remaining stock
                ).order_by('expiry_date')

                remaining_qty_needed = qty_to_remove

                for detail in in_transaction_details:
                    if remaining_qty_needed <= 0:
                        break

                    if detail.remaining_quantity >= remaining_qty_needed:
                        ExpiredProduct.objects.create(
                            product_id=product_id,
                            qty_expired=remaining_qty_needed,
                            expiry_date=detail.expiry_date,
                            remarks=remarks
                        )

                        detail.remaining_quantity -= remaining_qty_needed
                        detail.save()
                        remaining_qty_needed = 0
                    else:
                        ExpiredProduct.objects.create(
                            product_id=product_id,
                            qty_expired=detail.remaining_quantity,
                            expiry_date=detail.expiry_date,
                            remarks=remarks
                        )

                        remaining_qty_needed -= detail.remaining_quantity
                        detail.remaining_quantity = 0
                        detail.save()

                # Update total stock after removal
                total_stock = TotalStock.objects.get(product_id=product_id)
                total_stock.total_quantity -= qty_to_remove
                total_stock.save()

            return Response({"success": "Expired product removed from inventory and details tracked."}, status=status.HTTP_200_OK)
        except ProductInTransactionDetail.DoesNotExist:
            return Response({"error": "Product not found or already removed."}, status=status.HTTP_404_NOT_FOUND)
        except TotalStock.DoesNotExist:
            return Response({"error": "Total stock not found for this product."}, status=status.HTTP_404_NOT_FOUND)