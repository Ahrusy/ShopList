from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, CategoryViewSet, ShopViewSet, TagViewSet, UserViewSet, LocationViewSet, UserLocationViewSet

router = DefaultRouter()
router.register('products', ProductViewSet)
router.register('categories', CategoryViewSet)
router.register('shops', ShopViewSet)
router.register('tags', TagViewSet)
router.register('users', UserViewSet)
router.register('locations', LocationViewSet)
router.register('user-locations', UserLocationViewSet)

urlpatterns = router.urls