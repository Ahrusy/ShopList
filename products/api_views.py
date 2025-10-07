"""
API views для мега меню и каталога товаров
"""
import logging
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from django.db.models import Q, Count, Prefetch
from .models import Category, Product

logger = logging.getLogger(__name__)


@require_http_methods(["GET"])
@cache_page(60 * 15)  # Кэшируем на 15 минут
def mega_menu_categories(request):
    """
    API endpoint для получения дерева категорий для мега меню
    
    Returns:
        JSON с иерархической структурой категорий
    """
    try:
        logger.info("Loading mega menu categories")
        
        # Получаем все активные категории с подкатегориями
        categories = Category.objects.filter(
            is_active=True,
            show_in_megamenu=True,
            parent=None  # Только корневые категории
        ).prefetch_related(
            Prefetch(
                'children',
                queryset=Category.objects.filter(
                    is_active=True,
                    show_in_megamenu=True
                ).prefetch_related(
                    Prefetch(
                        'children',
                        queryset=Category.objects.filter(
                            is_active=True,
                            show_in_megamenu=True
                        ).order_by('sort_order')
                    )
                ).order_by('sort_order')
            )
        ).order_by('sort_order')
        
        def serialize_category(category):
            """Сериализует категорию в словарь"""
            try:
                return {
                    'id': category.id,
                    'name': category.name,
                    'slug': category.slug,
                    'icon': category.icon or '',
                    'level': getattr(category, 'category_level', 0),
                    'products_count': getattr(category, 'products_count', 0),
                    'has_products': getattr(category, 'has_products', False),
                    'image_url': category.mega_menu_image.url if category.mega_menu_image else None,
                    'description': getattr(category, 'mega_menu_description', ''),
                    'children': [serialize_category(child) for child in category.children.all()]
                }
            except Exception as e:
                logger.error(f"Error serializing category {category.id}: {str(e)}")
                return {
                    'id': category.id,
                    'name': category.name,
                    'slug': category.slug,
                    'icon': '',
                    'level': 0,
                    'products_count': 0,
                    'has_products': False,
                    'image_url': None,
                    'description': '',
                    'children': []
                }
        
        serialized_categories = []
        for cat in categories:
            try:
                serialized_categories.append(serialize_category(cat))
            except Exception as e:
                logger.error(f"Error processing category {cat.id}: {str(e)}")
                continue
        
        data = {
            'success': True,
            'categories': serialized_categories,
            'total_categories': len(serialized_categories)
        }
        
        logger.info(f"Successfully loaded {len(serialized_categories)} categories")
        return JsonResponse(data)
        
    except Exception as e:
        logger.error(f"Error loading mega menu categories: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Ошибка загрузки категорий',
            'categories': [],
            'total_categories': 0
        }, status=500)


@require_http_methods(["GET"])
def category_subcategories(request, category_id):
    """
    API endpoint для получения подкатегорий конкретной категории
    
    Args:
        category_id: ID родительской категории
        
    Returns:
        JSON с подкатегориями
    """
    try:
        logger.info(f"Loading subcategories for category {category_id}")
        
        try:
            category = Category.objects.get(
                id=category_id,
                is_active=True
            )
        except Category.DoesNotExist:
            logger.warning(f"Category {category_id} not found")
            return JsonResponse({
                'success': False,
                'error': 'Категория не найдена'
            }, status=404)
        
        # Получаем подкатегории с их подкатегориями
        subcategories = category.children.filter(
            is_active=True
        ).prefetch_related(
            Prefetch(
                'children',
                queryset=Category.objects.filter(
                    is_active=True
                ).order_by('sort_order')
            )
        ).order_by('sort_order')
        
        def serialize_subcategory(subcategory):
            """Сериализует подкатегорию"""
            try:
                return {
                    'id': subcategory.id,
                    'name': subcategory.name,
                    'slug': subcategory.slug,
                    'icon': getattr(subcategory, 'icon', '') or '',
                    'level': getattr(subcategory, 'category_level', 1),
                    'products_count': getattr(subcategory, 'products_count', 0),
                    'has_products': getattr(subcategory, 'has_products', False),
                    'image_url': subcategory.mega_menu_image.url if subcategory.mega_menu_image else None,
                    'description': getattr(subcategory, 'mega_menu_description', ''),
                    'children': [
                        {
                            'id': child.id,
                            'name': child.name,
                            'slug': child.slug,
                            'products_count': getattr(child, 'products_count', 0),
                            'has_products': getattr(child, 'has_products', False),
                        }
                        for child in subcategory.children.all()
                    ]
                }
            except Exception as e:
                logger.error(f"Error serializing subcategory {subcategory.id}: {str(e)}")
                return {
                    'id': subcategory.id,
                    'name': subcategory.name,
                    'slug': subcategory.slug,
                    'icon': '',
                    'level': 1,
                    'products_count': 0,
                    'has_products': False,
                    'image_url': None,
                    'description': '',
                    'children': []
                }
        
        serialized_subcategories = []
        for sub in subcategories:
            try:
                serialized_subcategories.append(serialize_subcategory(sub))
            except Exception as e:
                logger.error(f"Error processing subcategory {sub.id}: {str(e)}")
                continue
        
        data = {
            'success': True,
            'category': {
                'id': category.id,
                'name': category.name,
                'slug': category.slug,
                'level': getattr(category, 'category_level', 0),
            },
            'subcategories': serialized_subcategories,
            'total_subcategories': len(serialized_subcategories)
        }
        
        logger.info(f"Successfully loaded {len(serialized_subcategories)} subcategories for category {category_id}")
        return JsonResponse(data)
        
    except Exception as e:
        logger.error(f"Error loading subcategories for category {category_id}: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Ошибка загрузки подкатегорий',
            'category': None,
            'subcategories': [],
            'total_subcategories': 0
        }, status=500)


@require_http_methods(["GET"])
def search_categories(request):
    """
    API endpoint для поиска по категориям
    
    Query parameters:
        q: Поисковый запрос
        limit: Максимальное количество результатов (по умолчанию 10)
        
    Returns:
        JSON с результатами поиска
    """
    query = request.GET.get('q', '').strip()
    limit = min(int(request.GET.get('limit', 10)), 50)  # Максимум 50 результатов
    
    if not query or len(query) < 2:
        return JsonResponse({
            'categories': [],
            'total': 0,
            'query': query
        })
    
    # Поиск по названию и описанию категорий
    categories = Category.objects.filter(
        Q(name__icontains=query) | Q(description__icontains=query),
        is_active=True,
        show_in_megamenu=True
    ).select_related('parent').order_by(
        'category_level',  # Сначала корневые категории
        'products_count',  # Потом по количеству товаров
        'name'
    )[:limit]
    
    def get_category_path(category):
        """Возвращает полный путь категории"""
        path = []
        current = category
        while current:
            path.append(current.name)
            current = current.parent
        return ' > '.join(reversed(path))
    
    results = []
    for category in categories:
        results.append({
            'id': category.id,
            'name': category.name,
            'slug': category.slug,
            'level': category.category_level,
            'path': get_category_path(category),
            'products_count': category.products_count,
            'has_products': category.has_products,
            'icon': category.icon,
            'image_url': category.mega_menu_image.url if category.mega_menu_image else None,
        })
    
    data = {
        'categories': results,
        'total': len(results),
        'query': query,
        'has_more': len(results) == limit
    }
    
    return JsonResponse(data)


@require_http_methods(["GET"])
def category_featured_products(request, category_id):
    """
    API endpoint для получения рекомендуемых товаров категории
    
    Args:
        category_id: ID категории
        
    Returns:
        JSON с рекомендуемыми товарами
    """
    try:
        category = Category.objects.get(
            id=category_id,
            is_active=True
        )
    except Category.DoesNotExist:
        return JsonResponse({'error': 'Категория не найдена'}, status=404)
    
    # Получаем рекомендуемые товары или популярные товары из категории
    featured_products = category.featured_products.filter(
        is_active=True
    ).select_related('category').prefetch_related('images')[:6]
    
    if not featured_products:
        # Если нет рекомендуемых, берем популярные товары
        featured_products = Product.objects.filter(
            category=category,
            is_active=True
        ).order_by('-rating', '-views_count').select_related('category').prefetch_related('images')[:6]
    
    def serialize_product(product):
        """Сериализует товар"""
        primary_image = product.images.filter(is_primary=True).first()
        if not primary_image:
            primary_image = product.images.first()
        
        return {
            'id': product.id,
            'name': product.name,
            'price': float(product.price),
            'discount_price': float(product.discount_price) if product.discount_price else None,
            'final_price': float(product.final_price),
            'discount_percentage': round(product.discount_percentage, 1),
            'rating': float(product.rating),
            'reviews_count': product.reviews_count,
            'image_url': primary_image.get_thumbnail_url() if primary_image else None,
            'slug': product.sku,  # Используем SKU как slug
            'brand': product.brand,
        }
    
    data = {
        'category': {
            'id': category.id,
            'name': category.name,
            'slug': category.slug,
        },
        'products': [serialize_product(product) for product in featured_products],
        'total_products': len(featured_products)
    }
    
    return JsonResponse(data)


@require_http_methods(["GET"])
def category_stats(request):
    """
    API endpoint для получения статистики категорий
    
    Returns:
        JSON со статистикой
    """
    cache_key = 'category_stats'
    stats = cache.get(cache_key)
    
    if not stats:
        # Вычисляем статистику
        total_categories = Category.objects.filter(is_active=True).count()
        root_categories = Category.objects.filter(is_active=True, parent=None).count()
        categories_with_products = Category.objects.filter(
            is_active=True,
            has_products=True
        ).count()
        
        # Топ категории по количеству товаров
        top_categories = Category.objects.filter(
            is_active=True,
            has_products=True
        ).order_by('-products_count')[:10]
        
        stats = {
            'total_categories': total_categories,
            'root_categories': root_categories,
            'categories_with_products': categories_with_products,
            'categories_by_level': {
                'level_0': Category.objects.filter(is_active=True, category_level=0).count(),
                'level_1': Category.objects.filter(is_active=True, category_level=1).count(),
                'level_2': Category.objects.filter(is_active=True, category_level=2).count(),
            },
            'top_categories': [
                {
                    'id': cat.id,
                    'name': cat.name,
                    'products_count': cat.products_count,
                    'level': cat.category_level,
                }
                for cat in top_categories
            ]
        }
        
        # Кэшируем на 1 час
        cache.set(cache_key, stats, 60 * 60)
    
    return JsonResponse(stats)

# Product Banner API endpoints
@require_http_methods(["GET"])
def product_banners_list(request):
    """
    API endpoint для получения списка товарных баннеров
    """
    try:
        from .models import ProductBanner
        
        banners = ProductBanner.objects.all().order_by('sort_order', '-created_at')
        
        banners_data = [
            {
                'id': banner.id,
                'title': banner.title,
                'subtitle': banner.subtitle,
                'description': banner.description,
                'image': banner.image.url if banner.image else None,
                'link': banner.link,
                'style': banner.style,
                'button_text': banner.button_text,
                'background_color': banner.background_color,
                'text_color': banner.text_color,
                'is_active': banner.is_active,
                'sort_order': banner.sort_order,
                'created_at': banner.created_at.isoformat() if banner.created_at else None
            }
            for banner in banners
        ]
        
        return JsonResponse({
            'success': True,
            'data': banners_data
        })
        
    except Exception as e:
        logger.error(f"Ошибка при получении списка баннеров: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Ошибка при получении списка баннеров'
        }, status=500)


@require_http_methods(["GET"])
def product_banner_detail(request, banner_id):
    """
    API endpoint для получения детальной информации о баннере
    """
    try:
        from .models import ProductBanner
        
        banner = ProductBanner.objects.get(id=banner_id)
        
        banner_data = {
            'id': banner.id,
            'title': banner.title,
            'subtitle': banner.subtitle,
            'description': banner.description,
            'image': banner.image.url if banner.image else None,
            'link': banner.link,
            'style': banner.style,
            'button_text': banner.button_text,
            'background_color': banner.background_color,
            'text_color': banner.text_color,
            'is_active': banner.is_active,
            'sort_order': banner.sort_order,
            'created_at': banner.created_at.isoformat() if banner.created_at else None
        }
        
        return JsonResponse({
            'success': True,
            'data': banner_data
        })
        
    except ProductBanner.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Баннер не найден'
        }, status=404)
    except Exception as e:
        logger.error(f"Ошибка при получении баннера: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Ошибка при получении баннера'
        }, status=500)


@require_http_methods(["POST"])
def product_banner_create(request):
    """
    API endpoint для создания нового баннера
    """
    try:
        from .models import ProductBanner
        
        # Здесь должна быть логика создания баннера
        # Пока возвращаем заглушку
        return JsonResponse({
            'success': True,
            'message': 'Функция создания баннера в разработке'
        })
        
    except Exception as e:
        logger.error(f"Ошибка при создании баннера: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Ошибка при создании баннера'
        }, status=500)


@require_http_methods(["PUT", "PATCH"])
def product_banner_update(request, banner_id):
    """
    API endpoint для обновления баннера
    """
    try:
        from .models import ProductBanner
        
        # Здесь должна быть логика обновления баннера
        # Пока возвращаем заглушку
        return JsonResponse({
            'success': True,
            'message': 'Функция обновления баннера в разработке'
        })
        
    except Exception as e:
        logger.error(f"Ошибка при обновлении баннера: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Ошибка при обновлении баннера'
        }, status=500)


@require_http_methods(["DELETE"])
def product_banner_delete(request, banner_id):
    """
    API endpoint для удаления баннера
    """
    try:
        from .models import ProductBanner
        
        banner = ProductBanner.objects.get(id=banner_id)
        banner.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Баннер успешно удален'
        })
        
    except ProductBanner.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Баннер не найден'
        }, status=404)
    except Exception as e:
        logger.error(f"Ошибка при удалении баннера: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Ошибка при удалении баннера'
        }, status=500)


@require_http_methods(["POST"])
def product_banner_toggle_active(request, banner_id):
    """
    API endpoint для переключения активности баннера
    """
    try:
        from .models import ProductBanner
        
        banner = ProductBanner.objects.get(id=banner_id)
        banner.is_active = not banner.is_active
        banner.save()
        
        return JsonResponse({
            'success': True,
            'is_active': banner.is_active,
            'message': f'Баннер {"активирован" if banner.is_active else "деактивирован"}'
        })
        
    except ProductBanner.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Баннер не найден'
        }, status=404)
    except Exception as e:
        logger.error(f"Ошибка при переключении активности баннера: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Ошибка при переключении активности баннера'
        }, status=500)


@require_http_methods(["POST"])
def product_banner_reorder(request):
    """
    API endpoint для изменения порядка баннеров
    """
    try:
        from .models import ProductBanner
        import json
        
        data = json.loads(request.body)
        banner_orders = data.get('orders', [])
        
        for item in banner_orders:
            banner_id = item.get('id')
            sort_order = item.get('sort_order')
            
            if banner_id and sort_order is not None:
                ProductBanner.objects.filter(id=banner_id).update(sort_order=sort_order)
        
        return JsonResponse({
            'success': True,
            'message': 'Порядок баннеров обновлен'
        })
        
    except Exception as e:
        logger.error(f"Ошибка при изменении порядка баннеров: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Ошибка при изменении порядка баннеров'
        }, status=500)