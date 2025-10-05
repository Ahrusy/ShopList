from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny, IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import F
# PostgreSQL search imports (conditionally imported where needed)
# from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from django_ratelimit.decorators import ratelimit
from django_ratelimit.exceptions import Ratelimited
from ..models import Product, Category, Shop, Tag, User, Location, UserLocation, Order, OrderItem, Cart, CartItem
from .serializers import ProductSerializer, CategorySerializer, ShopSerializer, TagSerializer, UserSerializer, LocationSerializer, UserLocationSerializer, OrderSerializer, OrderItemSerializer, CartSerializer, CartItemSerializer
from .permissions import IsManagerOrAdmin, IsOwnerOrAdmin

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser] # Только администраторы могут управлять пользователями

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def toggle_favorite(self, request, pk=None):
        product = self.get_object() # Здесь self.get_object() вернет User, а не Product
        # Нужно получить продукт по pk из URL
        product_obj = Product.objects.get(pk=pk) # Это неверно, pk здесь - это pk пользователя
        # Правильно:
        # product_id = request.data.get('product_id')
        # product_obj = get_object_or_404(Product, pk=product_id)
        # if request.user.favorites.filter(pk=product_obj.pk).exists():
        #     request.user.favorites.remove(product_obj)
        #     message = "Товар удален из избранного."
        # else:
        #     request.user.favorites.add(product_obj)
        #     message = "Товар добавлен в избранное."
        # return Response({'message': message}, status=status.HTTP_200_OK)
        return Response({'detail': 'Метод не реализован корректно. Используйте ProductViewSet для избранного.'}, status=status.HTTP_400_BAD_REQUEST)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminUser] # Только администраторы могут управлять категориями
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['translations__name', 'translations__description']
    ordering_fields = ['translations__name', 'created_at']
    
    @method_decorator(cache_page(60 * 60))  # Кэшируем на 1 час
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @method_decorator(cache_page(60 * 60))  # Кэшируем на 1 час
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAdminUser()]

class ShopViewSet(viewsets.ModelViewSet):
    queryset = Shop.objects.all()
    serializer_class = ShopSerializer
    permission_classes = [IsAdminUser] # Только администраторы могут управлять магазинами
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['translations__name', 'translations__city', 'translations__address']
    ordering_fields = ['translations__name', 'translations__city', 'created_at']

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAdminUser()]

class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAdminUser] # Только администраторы могут управлять тегами
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['translations__name']
    ordering_fields = ['translations__name']

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAdminUser()]

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().select_related('category', 'seller').prefetch_related('images', 'shops', 'tags', 'characteristics')
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['category', 'shops', 'tags', 'price', 'discount_price', 'currency']
    search_fields = ['translations__name', 'translations__description', 'category__translations__name', 'shops__translations__name', 'tags__translations__name']
    ordering_fields = ['name', 'price', 'created_at', 'views_count']
    
    @method_decorator(ratelimit(key='ip', rate='100/h', method='GET'))
    @method_decorator(cache_page(60 * 15))  # Кэшируем на 15 минут
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @method_decorator(ratelimit(key='ip', rate='200/h', method='GET'))
    @method_decorator(cache_page(60 * 30))  # Кэшируем на 30 минут
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @method_decorator(ratelimit(key='user', rate='10/h', method='POST'))
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @method_decorator(ratelimit(key='user', rate='20/h', method='PUT'))
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    @method_decorator(ratelimit(key='user', rate='20/h', method='PATCH'))
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)
    
    @method_decorator(ratelimit(key='user', rate='5/h', method='DELETE'))
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        elif self.action in ['create']:
            return [IsManagerOrAdmin()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [IsManagerOrAdmin()] # IsOwnerOrAdmin будет проверять, что менеджер управляет магазином товара
        elif self.action == 'toggle_favorite':
            return [IsAuthenticated()]
        return [IsAdminUser()]

    def perform_create(self, serializer):
        # Менеджер может создавать товары только для своих магазинов
        if self.request.user.role == 'manager':
            shops = serializer.validated_data.get('shops')
            if not all(shop in self.request.user.shops.all() for shop in shops):
                raise serializers.ValidationError("Вы можете добавлять товары только в магазины, которыми управляете.")
        serializer.save()

    def perform_update(self, serializer):
        # Менеджер может обновлять товары только для своих магазинов
        if self.request.user.role == 'manager':
            shops = serializer.validated_data.get('shops')
            if not all(shop in self.request.user.shops.all() for shop in shops):
                raise serializers.ValidationError("Вы можете обновлять товары только в магазинах, которыми управляете.")
        serializer.save()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # Увеличиваем счетчик просмотров
        instance.views_count = F('views_count') + 1
        instance.save(update_fields=['views_count'])
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def toggle_favorite(self, request, pk=None):
        product = self.get_object()
        user = request.user
        if user.favorites.filter(pk=product.pk).exists():
            user.favorites.remove(product)
            message = _("Товар удален из избранного.")
        else:
            user.favorites.add(product)
            message = _("Товар добавлен в избранное.")
        return Response({'message': message}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def search(self, request):
        query = request.query_params.get('q', '')
        if not query:
            return Response({'detail': _('Параметр "q" обязателен для поиска.')}, status=status.HTTP_400_BAD_REQUEST)

        # Проверяем, используем ли мы PostgreSQL (только PostgreSQL поддерживает SearchVector)
        from django.conf import settings
        db_engine = settings.DATABASES['default']['ENGINE']
        
        if 'postgresql' in db_engine:
            # Используем полнотекстовый поиск PostgreSQL
            from django.contrib.postgres.search import SearchQuery, SearchRank
            from django.db.models import F
            search_query = SearchQuery(query)
            products = self.get_queryset().annotate(
                rank=SearchRank(F('search_vector'), search_query)
            ).filter(search_vector=search_query).order_by('-rank')
        else:
            # Для других баз данных (например, SQLite) используем простой поиск по названию и описанию
            from django.db import models
            products = self.get_queryset().filter(
                models.Q(name__icontains=query) | models.Q(description__icontains=query)
            )

        page = self.paginate_queryset(products)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)


class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.filter(is_active=True)
    serializer_class = LocationSerializer
    permission_classes = [AllowAny]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'region', 'country']
    ordering_fields = ['name', 'region']

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAdminUser()]


class UserLocationViewSet(viewsets.ModelViewSet):
    queryset = UserLocation.objects.all()
    serializer_class = UserLocationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserLocation.objects.filter(user=self.request.user)

    @action(detail=False, methods=['get'])
    def current(self, request):
        """Получить текущую локацию пользователя"""
        try:
            user_location = UserLocation.objects.filter(user=request.user).first()
            if user_location:
                serializer = self.get_serializer(user_location)
                return Response(serializer.data)
            else:
                return Response({'detail': 'Локация не установлена'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def set_location(self, request):
        """Установить локацию пользователя"""
        location_id = request.data.get('location_id')
        is_auto_detected = request.data.get('is_auto_detected', False)
        
        if not location_id:
            return Response({'detail': 'location_id обязателен'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            location = Location.objects.get(id=location_id, is_active=True)
            
            # Удаляем предыдущие локации пользователя
            UserLocation.objects.filter(user=request.user).delete()
            
            # Создаем новую локацию
            user_location = UserLocation.objects.create(
                user=request.user,
                location=location,
                is_auto_detected=is_auto_detected
            )
            
            serializer = self.get_serializer(user_location)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Location.DoesNotExist:
            return Response({'detail': 'Локация не найдена'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def detect_location(self, request):
        """Автоматическое определение локации по координатам"""
        latitude = request.data.get('latitude')
        longitude = request.data.get('longitude')
        
        if not latitude or not longitude:
            return Response({'detail': 'latitude и longitude обязательны'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Простой поиск ближайшей локации (в реальном проекте лучше использовать более точные алгоритмы)
            from django.db.models import F
            from math import sqrt
            
            locations = Location.objects.filter(is_active=True)
            closest_location = None
            min_distance = float('inf')
            
            for location in locations:
                if location.latitude and location.longitude:
                    distance = sqrt(
                        (float(latitude) - location.latitude) ** 2 + 
                        (float(longitude) - location.longitude) ** 2
                    )
                    if distance < min_distance:
                        min_distance = distance
                        closest_location = location
            
            if closest_location:
                # Удаляем предыдущие локации пользователя
                UserLocation.objects.filter(user=request.user).delete()
                
                # Создаем новую локацию
                user_location = UserLocation.objects.create(
                    user=request.user,
                    location=closest_location,
                    is_auto_detected=True
                )
                
                serializer = self.get_serializer(user_location)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response({'detail': 'Ближайшая локация не найдена'}, status=status.HTTP_404_NOT_FOUND)
                
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class CatalogViewSet(viewsets.ViewSet):
    """API для получения данных каталога"""
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['get'])
    def categories(self, request):
        """Получить все категории с подкатегориями для каталога"""
        root_categories = Category.objects.filter(
            parent__isnull=True, 
            is_active=True, 
            show_in_megamenu=True
        ).order_by('sort_order', 'slug')
        
        result = []
        for category in root_categories:
            category_data = {
                'id': category.id,
                'name': category.name,
                'icon': category.icon,
                'subcategories': []
            }
            
            for subcategory in category.get_children():
                subcategory_data = {
                    'id': subcategory.id,
                    'name': subcategory.name,
                    'slug': subcategory.slug,
                    'subsubcategories': []
                }
                
                for subsubcategory in subcategory.get_children():
                    subsubcategory_data = {
                        'id': subsubcategory.id,
                        'name': subsubcategory.name,
                        'slug': subsubcategory.slug
                    }
                    subsubcategory_data['subsubcategories'].append(subsubcategory_data)
                
                category_data['subcategories'].append(subcategory_data)
            
            result.append(category_data)
        
        return Response(result)


class OrderViewSet(viewsets.ModelViewSet):
    """API для заказов"""
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['status', 'payment_status']
    ordering_fields = ['created_at', 'total_amount']
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return Order.objects.all().select_related('user').prefetch_related('items__product__images', 'items__product__category')
        return Order.objects.filter(user=self.request.user).prefetch_related('items__product__images', 'items__product__category')
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Отменить заказ"""
        order = self.get_object()
        if order.status in ['pending', 'confirmed']:
            order.status = 'cancelled'
            order.save()
            return Response({'message': 'Заказ отменен'}, status=status.HTTP_200_OK)
        return Response({'error': 'Заказ нельзя отменить'}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def confirm_payment(self, request, pk=None):
        """Подтвердить оплату"""
        order = self.get_object()
        if order.payment_status == 'pending':
            order.payment_status = 'paid'
            order.save()
            return Response({'message': 'Оплата подтверждена'}, status=status.HTTP_200_OK)
        return Response({'error': 'Оплата уже подтверждена'}, status=status.HTTP_400_BAD_REQUEST)


class CartViewSet(viewsets.ModelViewSet):
    """API для корзины"""
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user).prefetch_related('items__product__images', 'items__product__category')
    
    def get_object(self):
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        return cart
    
    @action(detail=False, methods=['get'])
    def my_cart(self, request):
        """Получить корзину текущего пользователя"""
        cart, created = Cart.objects.get_or_create(user=request.user)
        serializer = self.get_serializer(cart)
        return Response(serializer.data)
    
    @method_decorator(ratelimit(key='user', rate='30/h', method='POST'))
    @action(detail=False, methods=['post'])
    def add_item(self, request):
        """Добавить товар в корзину"""
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))
        
        if not product_id:
            return Response({'error': 'product_id обязателен'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({'error': 'Товар не найден'}, status=status.HTTP_404_NOT_FOUND)
        
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )
        
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        
        serializer = self.get_serializer(cart)
        return Response(serializer.data)
    
    @method_decorator(ratelimit(key='user', rate='50/h', method='POST'))
    @action(detail=False, methods=['post'])
    def update_item(self, request):
        """Обновить количество товара в корзине"""
        item_id = request.data.get('item_id')
        quantity = int(request.data.get('quantity', 1))
        
        if not item_id:
            return Response({'error': 'item_id обязателен'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            cart_item = CartItem.objects.get(id=item_id, cart__user=request.user)
        except CartItem.DoesNotExist:
            return Response({'error': 'Товар в корзине не найден'}, status=status.HTTP_404_NOT_FOUND)
        
        if quantity <= 0:
            cart_item.delete()
        else:
            cart_item.quantity = quantity
            cart_item.save()
        
        cart = cart_item.cart
        serializer = self.get_serializer(cart)
        return Response(serializer.data)
    
    @method_decorator(ratelimit(key='user', rate='30/h', method='POST'))
    @action(detail=False, methods=['post'])
    def remove_item(self, request):
        """Удалить товар из корзины"""
        item_id = request.data.get('item_id')
        
        if not item_id:
            return Response({'error': 'item_id обязателен'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            cart_item = CartItem.objects.get(id=item_id, cart__user=request.user)
            cart_item.delete()
        except CartItem.DoesNotExist:
            return Response({'error': 'Товар в корзине не найден'}, status=status.HTTP_404_NOT_FOUND)
        
        cart = CartItem.objects.filter(cart__user=request.user).first().cart if CartItem.objects.filter(cart__user=request.user).exists() else Cart.objects.get(user=request.user)
        serializer = self.get_serializer(cart)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def clear(self, request):
        """Очистить корзину"""
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart.items.all().delete()
        serializer = self.get_serializer(cart)
        return Response(serializer.data)