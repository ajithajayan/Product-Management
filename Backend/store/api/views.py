from rest_framework import generics, status
from rest_framework.response import Response
from store.models import (
    Supplier, Category, Brand, Product, Branch,
    ProductInTransaction, ProductOutTransaction,
    PurchaseRequest, DamageProductTransaction
)
from .serializers import (
    SupplierSerializer, CategorySerializer, BrandSerializer, ProductSerializer, BranchSerializer,
    ProductInTransactionSerializer, ProductOutTransactionSerializer,
    PurchaseRequestSerializer, DamageProductTransactionSerializer
)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from store.models import TotalStock

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
    queryset = Product.objects.select_related('brand', 'category', 'supplier').all()
    serializer_class = ProductSerializer

    def perform_create(self, serializer):
        # This method is called when a new product is being created
        serializer.save()
        # Any additional business logic can be added here, if needed

class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def perform_update(self, serializer):
        # Automatically called when an instance is being updated
        serializer.save()
        # If you need to recalculate stocks or perform other actions post-update, do it here

    def perform_destroy(self, instance):
        # Handle any cleanup or stock adjustments before deleting a product
        instance.delete()  # Delete the product
        # Potentially update TotalStock here if needed

# To get the total stock  of the product
class GetTotalStockView(APIView):
    def get(self, request, product_code, format=None):
        try:
            total_stock = TotalStock.objects.get(product_code=product_code)
            return Response({'total_stock': total_stock.total_quantity}, status=status.HTTP_200_OK)
        except TotalStock.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

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

# Product Out Transaction Views
class ProductOutTransactionListCreateView(generics.ListCreateAPIView):
    queryset = ProductOutTransaction.objects.all()
    serializer_class = ProductOutTransactionSerializer

class ProductOutTransactionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ProductOutTransaction.objects.all()
    serializer_class = ProductOutTransactionSerializer

# Purchase Request Views
class PurchaseRequestListCreateView(generics.ListCreateAPIView):
    queryset = PurchaseRequest.objects.all()
    serializer_class = PurchaseRequestSerializer

class PurchaseRequestDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = PurchaseRequest.objects.all()
    serializer_class = PurchaseRequestSerializer

# Damage Product Transaction Views
class DamageProductTransactionListCreateView(generics.ListCreateAPIView):
    queryset = DamageProductTransaction.objects.all()
    serializer_class = DamageProductTransactionSerializer

class DamageProductTransactionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = DamageProductTransaction.objects.all()
    serializer_class = DamageProductTransactionSerializer
