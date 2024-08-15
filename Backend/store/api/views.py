from django.utils import timezone
from rest_framework import generics, status
from rest_framework.response import Response
from store.models import (
    Supplier, Category, Brand, Product, Branch,
    ProductInTransaction, ProductInTransactionDetail, TotalStock
)
from .serializers import (
    SupplierSerializer, CategorySerializer, BrandSerializer, ProductSerializer, BranchSerializer,
    ProductInTransactionSerializer, InventorySerializer
)
from rest_framework.views import APIView
from rest_framework import generics
from django.db.models import F, Value, Case, When, IntegerField

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