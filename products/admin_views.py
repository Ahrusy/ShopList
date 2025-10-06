"""
Admin views for enhanced category management
"""
import logging
from django.shortcuts import render, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.template.loader import render_to_string
from .models import Category, Product

logger = logging.getLogger(__name__)


@staff_member_required
def category_preview(request, category_id):
    """
    Предварительный просмотр мега меню для категории
    """
    try:
        logger.info(f"Загрузка предварительного просмотра для категории ID: {category_id}")
        category = get_object_or_404(Category, id=category_id)
        logger.info(f"Категория найдена: {category.name}")
    except Exception as e:
        logger.error(f"Ошибка при загрузке категории {category_id}: {str(e)}")
        from django.http import HttpResponse
        return HttpResponse(f"Ошибка при загрузке категории: {str(e)}", status=404)
    
    # Получаем структуру категории для мега меню
    subcategories_level_2 = category.get_level_2_children()
    subcategories_level_3 = {}
    
    for subcat in subcategories_level_2:
        subcategories_level_3[subcat.id] = subcat.get_level_3_children()
    
    # Получаем рекомендуемые товары
    featured_products = category.featured_products.filter(is_active=True)[:6]
    
    # Если нет рекомендуемых товаров, берем популярные из категории
    if not featured_products.exists():
        featured_products = category.products.filter(
            is_active=True
        ).order_by('-views_count', '-rating')[:6]
    
    context = {
        'category': category,
        'subcategories_level_2': subcategories_level_2,
        'subcategories_level_3': subcategories_level_3,
        'featured_products': featured_products,
        'is_preview': True,
    }
    
    return render(request, 'admin/category_preview.html', context)


@staff_member_required
def category_tree_data(request):
    """
    API для получения данных дерева категорий
    """
    categories = Category.objects.filter(is_active=True).select_related('parent')
    
    def build_tree(parent=None):
        tree = []
        for category in categories.filter(parent=parent):
            node = {
                'id': category.id,
                'name': category.name,
                'slug': category.slug,
                'level': category.category_level,
                'products_count': category.products_count,
                'has_products': category.has_products,
                'show_in_megamenu': category.show_in_megamenu,
                'children': build_tree(category)
            }
            tree.append(node)
        return tree
    
    tree_data = build_tree()
    return JsonResponse({'tree': tree_data})


@staff_member_required
def category_statistics(request):
    """
    API для получения статистики категорий
    """
    total_categories = Category.objects.count()
    active_categories = Category.objects.filter(is_active=True).count()
    categories_with_products = Category.objects.filter(has_products=True).count()
    megamenu_categories = Category.objects.filter(show_in_megamenu=True).count()
    
    # Статистика по уровням
    level_stats = {}
    for level in range(3):
        level_stats[level] = Category.objects.filter(category_level=level).count()
    
    # Топ категории по количеству товаров
    top_categories = Category.objects.filter(
        is_active=True, 
        has_products=True
    ).order_by('-products_count')[:10]
    
    top_categories_data = [
        {
            'name': cat.name,
            'products_count': cat.products_count,
            'level': cat.category_level
        }
        for cat in top_categories
    ]
    
    stats = {
        'total_categories': total_categories,
        'active_categories': active_categories,
        'categories_with_products': categories_with_products,
        'megamenu_categories': megamenu_categories,
        'level_stats': level_stats,
        'top_categories': top_categories_data,
    }
    
    return JsonResponse(stats)


@staff_member_required
def bulk_create_subcategories(request):
    """
    API для массового создания подкатегорий
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    category_ids = request.POST.getlist('category_ids')
    created_count = 0
    errors = []
    
    for category_id in category_ids:
        try:
            category = Category.objects.get(id=category_id)
            subcategories = category.ensure_subcategories()
            created_count += len(subcategories)
        except Category.DoesNotExist:
            errors.append(f'Категория с ID {category_id} не найдена')
        except Exception as e:
            errors.append(f'Ошибка для категории {category_id}: {str(e)}')
    
    return JsonResponse({
        'created_count': created_count,
        'errors': errors,
        'success': len(errors) == 0
    })


@staff_member_required
def update_category_counts(request):
    """
    API для обновления счетчиков товаров в категориях
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    category_ids = request.POST.getlist('category_ids')
    updated_count = 0
    
    for category_id in category_ids:
        try:
            category = Category.objects.get(id=category_id)
            category.update_products_count()
            category.save()
            updated_count += 1
        except Category.DoesNotExist:
            continue
    
    return JsonResponse({
        'updated_count': updated_count,
        'success': True
    })