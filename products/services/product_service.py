from django.db.models import F
# PostgreSQL search imports (conditionally imported where needed)
# from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from ..models import Product, Category, Shop, Tag
from ..repositories.product_repository import ProductRepository # Импортируем репозиторий
from django.utils import translation

class ProductService:
    @staticmethod
    def get_all_products():
        return ProductRepository.get_all_products()

    @staticmethod
    def get_product_by_id(product_id):
        return ProductRepository.get_product_by_id(product_id)

    @staticmethod
    def create_product(data):
        return ProductRepository.create_product(data)

    @staticmethod
    def update_product(product_id, data):
        return ProductRepository.update_product(product_id, data)

    @staticmethod
    def delete_product(product_id):
        return ProductRepository.delete_product(product_id)

    @staticmethod
    def get_filtered_products(filters):
        queryset = ProductRepository.get_all_products()

        category_id = filters.get('category')
        if category_id:
            queryset = queryset.filter(category__id=category_id)

        shop_ids = filters.getlist('shops')
        if shop_ids:
            queryset = queryset.filter(shops__id__in=shop_ids).distinct()

        tag_ids = filters.getlist('tags')
        if tag_ids:
            queryset = queryset.filter(tags__id__in=tag_ids).distinct()

        price_min = filters.get('price_min')
        if price_min:
            queryset = queryset.filter(price__gte=price_min)

        price_max = filters.get('price_max')
        if price_max:
            queryset = queryset.filter(price__lte=price_max)

        query = filters.get('q')
        if query:
            # Проверяем, используем ли мы PostgreSQL (только PostgreSQL поддерживает SearchVector)
            from django.conf import settings
            db_engine = settings.DATABASES['default']['ENGINE']
            
            if 'postgresql' in db_engine:
                # Используем полнотекстовый поиск PostgreSQL
                from django.contrib.postgres.search import SearchQuery, SearchRank
                from django.db.models import F
                search_query = SearchQuery(query)
                queryset = queryset.annotate(
                    rank=SearchRank(F('search_vector'), search_query)
                ).filter(search_vector=search_query).order_by('-rank')
            else:
                # Для других баз данных (например, SQLite) используем простой поиск по названию и описанию
                from django.db import models
                queryset = queryset.filter(
                    models.Q(name__icontains=query) | models.Q(description__icontains=query)
                )

        return queryset

    @staticmethod
    def increment_product_views(product):
        product.views_count = F('views_count') + 1
        product.save(update_fields=['views_count'])
        product.refresh_from_db()
        return product

    @staticmethod
    def toggle_favorite(user, product):
        if user.favorites.filter(pk=product.pk).exists():
            user.favorites.remove(product)
            return False, _(f"Товар '{product.name}' удален из избранного.")
        else:
            user.favorites.add(product)
            return True, _(f"Товар '{product.name}' добавлен в избранное.")