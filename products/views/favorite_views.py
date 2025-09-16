from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.db.models import Q
from ..models import Product, Favorite
import json


class FavoriteListMixin:
    """Миксин для общих методов работы с избранным"""
    
    def get_category_filters(self, user):
        """Получить фильтры по категориям для избранного"""
        # Получаем уникальные категории из избранного пользователя
        categories = Product.objects.filter(
            favorites__user=user
        ).values_list('category__name', 'category__id').distinct()
        
        filters = [{'value': 'all', 'label': 'Все категории'}]
        for name, id in categories:
            if name:  # Проверяем, что название категории не пустое
                filters.append({'value': str(id), 'label': name})
        
        return filters


@login_required
def favorite_list(request):
    """Страница списка избранного пользователя"""
    mixin = FavoriteListMixin()
    
    # Получаем избранные товары пользователя
    favorites = Favorite.objects.filter(user=request.user).select_related('product__category').order_by('-created_at')
    
    # Фильтрация по категории
    category_filter = request.GET.get('category', 'all')
    if category_filter != 'all':
        favorites = favorites.filter(product__category_id=category_filter)
    
    # Пагинация
    paginator = Paginator(favorites, 12)
    page_number = request.GET.get('page')
    favorites_page = paginator.get_page(page_number)
    
    # Фильтры
    category_filters = mixin.get_category_filters(request.user)
    
    context = {
        'favorites': favorites_page,
        'category_filters': category_filters,
    }
    
    return render(request, 'favorites/favorite_list.html', context)


@login_required
@require_http_methods(["POST"])
def add_to_favorites(request):
    """Добавление товара в избранное"""
    try:
        data = json.loads(request.body)
        product_id = data.get('product_id')
        
        if not product_id:
            return JsonResponse({'success': False, 'message': 'ID товара не указан'}, status=400)
        
        product = get_object_or_404(Product, id=product_id)
        
        # Проверяем, не добавлен ли уже товар в избранное
        favorite, created = Favorite.objects.get_or_create(
            user=request.user,
            product=product
        )
        
        if created:
            return JsonResponse({'success': True, 'message': 'Товар добавлен в избранное'})
        else:
            return JsonResponse({'success': False, 'message': 'Товар уже в избранном'})
            
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Неверный формат данных'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'message': 'Ошибка сервера'}, status=500)


@login_required
@require_http_methods(["POST"])
def remove_from_favorites(request, favorite_id):
    """Удаление товара из избранного"""
    favorite = get_object_or_404(Favorite, id=favorite_id, user=request.user)
    favorite.delete()
    
    return JsonResponse({'success': True, 'message': 'Товар удален из избранного'})


@login_required
@require_http_methods(["POST"])
def toggle_favorite(request):
    """Переключение статуса избранного для товара"""
    try:
        data = json.loads(request.body)
        product_id = data.get('product_id')
        
        if not product_id:
            return JsonResponse({'success': False, 'message': 'ID товара не указан'}, status=400)
        
        product = get_object_or_404(Product, id=product_id)
        
        # Проверяем, есть ли товар в избранном
        try:
            favorite = Favorite.objects.get(user=request.user, product=product)
            favorite.delete()
            is_favorite = False
            message = 'Товар удален из избранного'
        except Favorite.DoesNotExist:
            Favorite.objects.create(user=request.user, product=product)
            is_favorite = True
            message = 'Товар добавлен в избранное'
        
        return JsonResponse({
            'success': True, 
            'message': message,
            'is_favorite': is_favorite
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Неверный формат данных'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'message': 'Ошибка сервера'}, status=500)


@login_required
@require_http_methods(["POST"])
def add_multiple_to_cart(request):
    """Добавление нескольких товаров из избранного в корзину"""
    try:
        data = json.loads(request.body)
        product_ids = data.get('product_ids', [])
        
        if not product_ids:
            return JsonResponse({'success': False, 'message': 'Товары не выбраны'}, status=400)
        
        # Получаем корзину из сессии
        cart = request.session.get('cart', {})
        added_count = 0
        
        for product_id in product_ids:
            product = get_object_or_404(Product, id=product_id)
            product_id_str = str(product_id)
            
            if product_id_str in cart:
                cart[product_id_str]['quantity'] += 1
            else:
                cart[product_id_str] = {
                    'quantity': 1,
                    'price': float(product.price)
                }
            added_count += 1
        
        request.session['cart'] = cart
        request.session.modified = True
        
        return JsonResponse({
            'success': True, 
            'message': f'{added_count} товар{added_count == 1 or added_count > 4 and "ов" or "а"} добавлено в корзину'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Неверный формат данных'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'message': 'Ошибка сервера'}, status=500)
