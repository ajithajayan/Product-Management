from django.urls import path
from .views import (
    InventoryListView, ProductOutTransactionListCreateView, SupplierListCreateView, SupplierDetailView,
    CategoryListCreateView, CategoryDetailView,
    BrandListCreateView, BrandDetailView,
    ProductListCreateView, ProductDetailView, GetTotalStockView, ProductCodeSearchView,
    BranchListCreateView, BranchDetailView,
    ProductInTransactionListCreateView, ProductInTransactionDetailView,
)

urlpatterns = [
    # Supplier URLs
    path('suppliers/', SupplierListCreateView.as_view(), name='supplier-list-create'),
    path('suppliers/<int:pk>/', SupplierDetailView.as_view(), name='supplier-detail'),

    # Category URLs
    path('categories/', CategoryListCreateView.as_view(), name='category-list-create'),
    path('categories/<int:pk>/', CategoryDetailView.as_view(), name='category-detail'),

    # Brand URLs
    path('brands/', BrandListCreateView.as_view(), name='brand-list-create'),
    path('brands/<int:pk>/', BrandDetailView.as_view(), name='brand-detail'),

    # Product URLs
    path('products/', ProductListCreateView.as_view(), name='product-list-create'),
    path('products/<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
    path('products/<str:product_code>/total_stock/', GetTotalStockView.as_view(), name='get_total_stock'),
    path('products/search_codes/', ProductCodeSearchView.as_view(), name='search_product_codes'),

    # Branch URLs
    path('branches/', BranchListCreateView.as_view(), name='branch-list-create'),
    path('branches/<str:branch_code>/', BranchDetailView.as_view(), name='branch-detail'),

    # Product In Transaction URLs
    path('product-in-transactions/', ProductInTransactionListCreateView.as_view(), name='product-in-transaction-list-create'),
    path('product-in-transactions/<int:pk>/', ProductInTransactionDetailView.as_view(), name='product-in-transaction-detail'),

    # Inventory
    path('inventory/', InventoryListView.as_view(), name='inventory-list'),


    # Product Out Transaction URLs

    path('product-out-transactions/', ProductOutTransactionListCreateView.as_view(), name='product-out-transaction-list-create'),
]
