"""
URL маршруты для API мега меню
"""
from django.urls import path
from . import api_views

app_name = 'products_api'

urlpatterns = [
    # API для мега меню
    path('categories/', api_views.mega_menu_categories, name='mega_menu_categories'),
    path('categories/<int:category_id>/subcategories/', api_views.category_subcategories, name='category_subcategories'),
    path('categories/<int:category_id>/level3/', api_views.category_subcategories, name='category_level3'),
    path('categories/search/', api_views.search_categories, name='search_categories'),
    path('categories/<int:category_id>/featured-products/', api_views.category_featured_products, name='category_featured_products'),
    path('categories/stats/', api_views.category_stats, name='category_stats'),
]