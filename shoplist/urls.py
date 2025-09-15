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
from django.conf.urls.i18n import i18n_patterns
from rest_framework import routers
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

# Импортируем URL-ы API из приложения products
from products.api import urls as products_api_urls

# Создаем роутер для API
router = routers.DefaultRouter()
router.registry.extend(products_api_urls.router.registry)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')), # Базовые URL-ы аутентификации
    # path('accounts/', include('two_factor.urls')), # URL-ы для 2FA (временно отключено)
    path('api/v1/', include(router.urls)), # URL-ы для REST API
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

# URL-ы, которые должны быть мультиязычными
urlpatterns += i18n_patterns(
    path('', include('products.urls')), # Добавляем URL-адреса из приложения products
    prefix_default_language=False # Не добавлять префикс для языка по умолчанию
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # В режиме отладки статические файлы обслуживаются Django, STATIC_ROOT используется для продакшена
    # urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
