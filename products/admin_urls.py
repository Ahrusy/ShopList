"""
Admin URLs for enhanced category management
"""
from django.urls import path
from . import admin_views

app_name = 'products_admin'

urlpatterns = [
    path('category-preview/<int:category_id>/', admin_views.category_preview, name='category_preview'),
    path('api/category-tree/', admin_views.category_tree_data, name='category_tree_data'),
    path('api/category-statistics/', admin_views.category_statistics, name='category_statistics'),
    path('api/bulk-create-subcategories/', admin_views.bulk_create_subcategories, name='bulk_create_subcategories'),
    path('api/update-category-counts/', admin_views.update_category_counts, name='update_category_counts'),
]