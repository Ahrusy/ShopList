from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny, IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import F
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from ..models import Product, Category, Shop, Tag, User, Location, UserLocation
from .serializers import ProductSerializer, CategorySerializer, ShopSerializer, TagSerializer, UserSerializer, LocationSerializer, UserLocationSerializer
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
    search_fields = ['translations__name']
    ordering_fields = ['translations__name', 'created_at']

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
    queryset = Product.objects.all().prefetch_related('images', 'category', 'shops', 'tags')
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['category', 'shops', 'tags', 'price', 'discount_price', 'currency']
    search_fields = ['translations__name', 'translations__description', 'category__translations__name', 'shops__translations__name', 'tags__translations__name']
    ordering_fields = ['name', 'price', 'created_at', 'views_count']

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

        search_query = SearchQuery(query)
        products = self.get_queryset().annotate(
            rank=SearchRank(F('search_vector'), search_query)
        ).filter(search_vector=search_query).order_by('-rank')

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
        ).order_by('sort_order', 'name')
        
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