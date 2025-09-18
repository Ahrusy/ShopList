from django.urls import path, include
from products import views
from products import cart_views, review_views, notification_views, analytics_views, promo_views, api_views

urlpatterns = [
    path('accounts/', include('django.contrib.auth.urls')), # Встроенные URL-адреса Django для аутентификации
    path('', views.index, name='index'),
    path('load-more-products/', views.load_more_products, name='load_more_products'),
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
    
    # Favorites URLs
    path('favorites/', include('products.urls.favorite_urls')),
    
    # Test location URL
    path('test-location/', views.test_location_view, name='test_location'),
    
    # Страницы
    path('pages/', views.page_list_view, name='pages'),
    path('pages/<slug:category_slug>/', views.page_list_view, name='pages_category'),
    path('page/<slug:slug>/', views.page_detail_view, name='page_detail'),
    
    # Заказы
    path('checkout/', views.checkout_view, name='checkout'),
    path('orders/', views.order_list_view, name='order_list'),
    path('order/<int:order_id>/', views.order_detail_view, name='order_detail'),
    path('order/<int:order_id>/tracking/', views.order_tracking_view, name='order_tracking'),
    
    # Отзывы
    path('product/<int:product_id>/review/', review_views.add_review, name='add_review'),
    path('review/<int:review_id>/edit/', review_views.edit_review, name='edit_review'),
    path('review/<int:review_id>/delete/', review_views.delete_review, name='delete_review'),
    path('product/<int:product_id>/reviews/', review_views.product_reviews, name='product_reviews'),
    path('my-reviews/', review_views.my_reviews, name='my_reviews'),
    path('review/<int:review_id>/like/', review_views.like_review, name='like_review'),
    path('admin/reviews/moderate/', review_views.moderate_reviews, name='moderate_reviews'),
    path('admin/review/<int:review_id>/approve/', review_views.approve_review, name='approve_review'),
    path('admin/review/<int:review_id>/reject/', review_views.reject_review, name='reject_review'),
    
    # Уведомления
    path('notifications/', notification_views.notification_list, name='notification_list'),
    path('notification/<int:notification_id>/', notification_views.notification_detail, name='notification_detail'),
    path('notification/<int:notification_id>/read/', notification_views.mark_as_read, name='mark_notification_read'),
    path('notifications/mark-all-read/', notification_views.mark_all_as_read, name='mark_all_notifications_read'),
    path('notification/<int:notification_id>/delete/', notification_views.delete_notification, name='delete_notification'),
    path('notifications/unread-count/', notification_views.unread_count, name='unread_notifications_count'),
    path('notifications/settings/', notification_views.notification_settings, name='notification_settings'),
    
    # Аналитика
    path('analytics/', analytics_views.SellerAnalyticsView.as_view(), name='analytics_dashboard'),
    path('analytics/data/', analytics_views.analytics_data, name='analytics_data'),
    path('analytics/export/', analytics_views.export_analytics, name='export_analytics'),
    
    # Промокоды
    path('admin/promo-codes/', promo_views.PromoCodeListView.as_view(), name='promo_list'),
    path('admin/promo-code/create/', promo_views.PromoCodeCreateView.as_view(), name='promo_create'),
    path('admin/promo-code/<int:pk>/edit/', promo_views.PromoCodeUpdateView.as_view(), name='promo_update'),
    path('admin/promo-code/<int:pk>/delete/', promo_views.PromoCodeDeleteView.as_view(), name='promo_delete'),
    path('promo-codes/apply/', promo_views.apply_promo_code, name='apply_promo_code'),
    path('promo-codes/remove/', promo_views.remove_promo_code, name='remove_promo_code'),
    path('promo-codes/check/<str:code>/', promo_views.check_promo_code, name='check_promo_code'),
    path('promo-codes/available/', promo_views.promo_codes_available, name='available_promo_codes'),
    path('admin/promo-codes/stats/', promo_views.promo_code_stats, name='promo_stats'),
    
    # Управление товарными баннерами
    path('admin/product-banners/', views.product_banners_management, name='product_banners_management'),
    
    # API для товарных баннеров
    path('api/product-banners/', api_views.product_banners_list, name='api_product_banners_list'),
    path('api/product-banners/<int:banner_id>/', api_views.product_banner_detail, name='api_product_banner_detail'),
    path('api/product-banners/create/', api_views.product_banner_create, name='api_product_banner_create'),
    path('api/product-banners/<int:banner_id>/update/', api_views.product_banner_update, name='api_product_banner_update'),
    path('api/product-banners/<int:banner_id>/delete/', api_views.product_banner_delete, name='api_product_banner_delete'),
    path('api/product-banners/<int:banner_id>/toggle/', api_views.product_banner_toggle_active, name='api_product_banner_toggle'),
    path('api/product-banners/reorder/', api_views.product_banner_reorder, name='api_product_banner_reorder'),
    
    # API для каталога
    path('api/catalog/categories/<int:category_id>/subcategories/', api_views.category_subcategories, name='api_category_subcategories'),
]