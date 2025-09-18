from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
import json
from .models import ProductBanner
from django.core.paginator import Paginator
from django.db.models import Q

@csrf_exempt
@require_http_methods(["GET"])
def product_banners_list(request):
    """API для получения списка товарных баннеров"""
    try:
        banners = ProductBanner.objects.filter(is_active=True).order_by('sort_order')
        
        # Пагинация
        page = request.GET.get('page', 1)
        per_page = request.GET.get('per_page', 10)
        paginator = Paginator(banners, per_page)
        page_obj = paginator.get_page(page)
        
        banners_data = []
        for banner in page_obj:
            banners_data.append({
                'id': banner.id,
                'title': banner.title,
                'subtitle': banner.subtitle,
                'description': banner.description,
                'image_url': banner.image.url if banner.image else None,
                'link': banner.link,
                'style': banner.style,
                'style_display': banner.get_style_display(),
                'button_text': banner.button_text,
                'background_color': banner.background_color,
                'text_color': banner.text_color,
                'sort_order': banner.sort_order,
                'is_active': banner.is_active,
                'created_at': banner.created_at.isoformat() if banner.created_at else None,
                'updated_at': banner.updated_at.isoformat() if banner.updated_at else None,
            })
        
        return JsonResponse({
            'success': True,
            'data': banners_data,
            'pagination': {
                'current_page': page_obj.number,
                'total_pages': paginator.num_pages,
                'total_items': paginator.count,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous(),
            }
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def product_banner_detail(request, banner_id):
    """API для получения детальной информации о товарном баннере"""
    try:
        banner = ProductBanner.objects.get(id=banner_id, is_active=True)
        
        banner_data = {
            'id': banner.id,
            'title': banner.title,
            'subtitle': banner.subtitle,
            'description': banner.description,
            'image_url': banner.image.url if banner.image else None,
            'link': banner.link,
            'style': banner.style,
            'style_display': banner.get_style_display(),
            'button_text': banner.button_text,
            'background_color': banner.background_color,
            'text_color': banner.text_color,
            'sort_order': banner.sort_order,
            'is_active': banner.is_active,
            'created_at': banner.created_at.isoformat() if banner.created_at else None,
            'updated_at': banner.updated_at.isoformat() if banner.updated_at else None,
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
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def product_banner_create(request):
    """API для создания нового товарного баннера"""
    try:
        data = json.loads(request.body)
        
        # Валидация обязательных полей
        required_fields = ['title', 'style']
        for field in required_fields:
            if field not in data:
                return JsonResponse({
                    'success': False,
                    'error': f'Поле {field} обязательно для заполнения'
                }, status=400)
        
        # Создание баннера
        banner = ProductBanner.objects.create(
            title=data['title'],
            subtitle=data.get('subtitle', ''),
            description=data.get('description', ''),
            link=data.get('link', ''),
            style=data['style'],
            button_text=data.get('button_text', 'Подробнее'),
            background_color=data.get('background_color', '#000000'),
            text_color=data.get('text_color', '#FFFFFF'),
            sort_order=data.get('sort_order', 0),
            is_active=data.get('is_active', True)
        )
        
        # Если есть изображение, сохраняем его
        if 'image' in request.FILES:
            banner.image = request.FILES['image']
            banner.save()
        
        return JsonResponse({
            'success': True,
            'data': {
                'id': banner.id,
                'title': banner.title,
                'message': 'Баннер успешно создан'
            }
        })
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Неверный формат JSON'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["PUT"])
def product_banner_update(request, banner_id):
    """API для обновления товарного баннера"""
    try:
        banner = ProductBanner.objects.get(id=banner_id)
        data = json.loads(request.body)
        
        # Обновление полей
        for field in ['title', 'subtitle', 'description', 'link', 'style', 'button_text', 
                     'background_color', 'text_color', 'sort_order', 'is_active']:
            if field in data:
                setattr(banner, field, data[field])
        
        banner.save()
        
        # Если есть новое изображение, сохраняем его
        if 'image' in request.FILES:
            banner.image = request.FILES['image']
            banner.save()
        
        return JsonResponse({
            'success': True,
            'data': {
                'id': banner.id,
                'title': banner.title,
                'message': 'Баннер успешно обновлен'
            }
        })
    except ProductBanner.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Баннер не найден'
        }, status=404)
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Неверный формат JSON'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["DELETE"])
def product_banner_delete(request, banner_id):
    """API для удаления товарного баннера"""
    try:
        banner = ProductBanner.objects.get(id=banner_id)
        banner_title = banner.title
        banner.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'Баннер "{banner_title}" успешно удален'
        })
    except ProductBanner.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Баннер не найден'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def product_banner_toggle_active(request, banner_id):
    """API для переключения статуса активности баннера"""
    try:
        banner = ProductBanner.objects.get(id=banner_id)
        banner.is_active = not banner.is_active
        banner.save()
        
        return JsonResponse({
            'success': True,
            'data': {
                'id': banner.id,
                'is_active': banner.is_active,
                'message': f'Статус баннера изменен на {"активен" if banner.is_active else "неактивен"}'
            }
        })
    except ProductBanner.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Баннер не найден'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def product_banner_reorder(request):
    """API для изменения порядка баннеров"""
    try:
        data = json.loads(request.body)
        banner_orders = data.get('banner_orders', [])
        
        for item in banner_orders:
            banner_id = item.get('id')
            new_order = item.get('sort_order')
            if banner_id and new_order is not None:
                ProductBanner.objects.filter(id=banner_id).update(sort_order=new_order)
        
        return JsonResponse({
            'success': True,
            'message': 'Порядок баннеров успешно обновлен'
        })
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Неверный формат JSON'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
