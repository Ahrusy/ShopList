from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, CategoryViewSet, ShopViewSet, TagViewSet, UserViewSet, LocationViewSet, UserLocationViewSet, OrderViewSet, CartViewSet, CatalogViewSet

router = DefaultRouter()
router.register('products', ProductViewSet)
router.register('categories', CategoryViewSet)
router.register('shops', ShopViewSet)
router.register('tags', TagViewSet)
router.register('users', UserViewSet)
router.register('locations', LocationViewSet)
router.register('user-locations', UserLocationViewSet)
router.register('orders', OrderViewSet)
router.register('cart', CartViewSet)
router.register('catalog', CatalogViewSet, basename='catalog')

urlpatterns = router.urls