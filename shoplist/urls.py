"""
URL configuration for shoplist project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns # Для мультиязычности
from django.views.i18n import set_language # Для смены языка
from products.views import index, category_view, checkout_view, order_detail_view, order_list_view, register_view, login_view, logout_view, test_location_view, page_list_view, page_detail_view, product_detail
from products.api import urls as products_api_urls
from rest_framework import routers
from products.api.views import ProductViewSet, CategoryViewSet, OrderViewSet, CartViewSet, UserViewSet, ShopViewSet, TagViewSet, LocationViewSet, UserLocationViewSet
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
# from two_factor.urls import urlpatterns as tf_urls # Для 2FA - отключено
from django.contrib.auth import views as auth_views # Для сброса пароля

router = routers.DefaultRouter()
router.register('products', ProductViewSet)
router.register('categories', CategoryViewSet)
router.register('orders', OrderViewSet)
router.register('carts', CartViewSet)
router.register('users', UserViewSet)
router.register('shops', ShopViewSet)
router.register('tags', TagViewSet)
router.register('locations', LocationViewSet)
router.register('userlocations', UserLocationViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('i18n/', set_language, name='set_language'), # URL для смены языка
    path('api/', include(router.urls)),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path('api/products/', include(products_api_urls)), # Включаем URL-адреса API для продуктов
    # path('account/', include(tf_urls)), # Для 2FA - отключено
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]

urlpatterns += i18n_patterns(
    path('', index, name='index'),
    path('product/<int:product_id>/', product_detail, name='product_detail'),
    path('categories/<slug:category_slug>/', category_view, name='category_view'),
    path('category/<str:category_slug>/', category_view, name='category'),
    path('cart/', checkout_view, name='cart'),
    path('checkout/', checkout_view, name='checkout_view'),
    path('orders/', order_list_view, name='order_list'),
    path('orders/<int:order_id>/', order_detail_view, name='order_detail'),
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('test_location/', test_location_view, name='test_location'),
    path('pages/', page_list_view, name='pages'),
    path('pages/<str:slug>/', page_detail_view, name='page_detail'),
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
