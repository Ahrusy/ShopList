from django.urls import path, include
from . import views
from . import cart_views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('accounts/', include('django.contrib.auth.urls')), # Встроенные URL-адреса Django для аутентификации
    path('', views.index, name='index'),
    path('category/<str:category_slug>/', views.category_view, name='category'),
    path('product/<int:pk>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('manager/', views.ManagerDashboardView.as_view(), name='manager_dashboard'),
    path('manager/product/add/', views.ProductCreateView.as_view(), name='product_add'),
    path('manager/product/<int:pk>/edit/', views.ProductUpdateView.as_view(), name='product_edit'),
    path('manager/product/<int:pk>/delete/', views.ProductDeleteView.as_view(), name='product_delete'),
    path('manager/shop/add/', views.ShopCreateView.as_view(), name='add_shop'),
    path('manager/shop/<int:pk>/edit/', views.ShopUpdateView.as_view(), name='edit_shop'),
    path('manager/shop/<int:pk>/delete/', views.ShopDeleteView.as_view(), name='delete_shop'),
    
    # Cart URLs
    path('cart/', cart_views.cart_view, name='cart'),
    path('cart/add/<int:product_id>/', cart_views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:item_id>/', cart_views.update_cart_item, name='update_cart_item'),
    path('cart/remove/<int:item_id>/', cart_views.remove_from_cart, name='remove_from_cart'),
    path('cart/clear/', cart_views.clear_cart, name='clear_cart'),
    path('cart/count/', cart_views.cart_count, name='cart_count'),
    
    # Test location URL
    path('test-location/', views.test_location_view, name='test_location'),
    
    # Страницы
    path('pages/', views.page_list_view, name='pages'),
    path('pages/<slug:category_slug>/', views.page_list_view, name='pages_category'),
    path('page/<slug:slug>/', views.page_detail_view, name='page_detail'),
]