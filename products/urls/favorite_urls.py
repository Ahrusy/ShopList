from django.urls import path
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from products.models import Favorite, Product

def get_session_favorites(request):
    """Получить избранное из сессии"""
    if 'favorites' not in request.session:
        request.session['favorites'] = []
    return request.session['favorites']

def save_session_favorites(request, favorites):
    """Сохранить избранное в сессию"""
    request.session['favorites'] = favorites

def favorite_list_view(request):
    """Страница избранных товаров"""
    favorite_products = []
    categories = []
    recommended_products = []
    
    if request.user.is_authenticated:
        # Получаем избранные товары пользователя
        favorites = Favorite.objects.filter(user=request.user).select_related('product', 'product__category', 'product__seller').prefetch_related('product__images')
        
        # Получаем товары из избранного
        favorite_products = [fav.product for fav in favorites]
        
        # Получаем категории для фильтрации
        categories = set()
        for product in favorite_products:
            if product.category:
                categories.add(product.category)
        categories = list(categories)
    else:
        # Для неавторизованных пользователей получаем избранное из сессии
        session_favorites = get_session_favorites(request)
        favorite_products = []
        for product_id in session_favorites:
            try:
                product = Product.objects.get(id=product_id, is_active=True)
                favorite_products.append(product)
            except Product.DoesNotExist:
                continue
        
        # Получаем категории для фильтрации
        categories = set()
        for product in favorite_products:
            if product.category:
                categories.add(product.category)
        categories = list(categories)
    
    # Получаем рекомендуемые товары для пустого состояния
    if not favorite_products:
        recommended_products = Product.objects.filter(is_active=True).select_related('category', 'seller').prefetch_related('images')[:8]
    
    context = {
        'favorites': favorite_products,
        'category_filters': categories,
        'favorites_count': len(favorite_products),
        'is_authenticated': request.user.is_authenticated,
        'recommended_products': recommended_products,
    }
    
    return render(request, 'favorites/favorite_list.html', context)


@csrf_exempt
@require_http_methods(["POST"])
def add_to_favorites(request, product_id):
    """Добавить товар в избранное"""
    product = get_object_or_404(Product, id=product_id)
    
    if request.user.is_authenticated:
        # Для авторизованных пользователей - работаем с БД
        favorite, created = Favorite.objects.get_or_create(
            user=request.user,
            product=product
        )
        
        if created:
            return JsonResponse({'success': True, 'message': 'Товар добавлен в избранное'})
        else:
            return JsonResponse({'success': False, 'message': 'Товар уже в избранном'})
    else:
        # Для неавторизованных пользователей - работаем с сессией
        session_favorites = get_session_favorites(request)
        if product_id not in session_favorites:
            session_favorites.append(product_id)
            save_session_favorites(request, session_favorites)
            return JsonResponse({'success': True, 'message': 'Товар добавлен в избранное'})
        else:
            return JsonResponse({'success': False, 'message': 'Товар уже в избранном'})


@csrf_exempt
@require_http_methods(["POST"])
def remove_from_favorites(request, product_id):
    """Удалить товар из избранного"""
    product = get_object_or_404(Product, id=product_id)
    
    if request.user.is_authenticated:
        # Для авторизованных пользователей - работаем с БД
        try:
            favorite = Favorite.objects.get(user=request.user, product=product)
            favorite.delete()
            return JsonResponse({'success': True, 'message': 'Товар удален из избранного'})
        except Favorite.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Товар не найден в избранном'})
    else:
        # Для неавторизованных пользователей - работаем с сессией
        session_favorites = get_session_favorites(request)
        if product_id in session_favorites:
            session_favorites.remove(product_id)
            save_session_favorites(request, session_favorites)
            return JsonResponse({'success': True, 'message': 'Товар удален из избранного'})
        else:
            return JsonResponse({'success': False, 'message': 'Товар не найден в избранном'})


@require_http_methods(["GET"])
def check_favorite_status(request, product_id):
    """Проверить статус товара в избранном"""
    product = get_object_or_404(Product, id=product_id)
    
    if request.user.is_authenticated:
        # Для авторизованных пользователей - проверяем в БД
        is_favorite = Favorite.objects.filter(user=request.user, product=product).exists()
    else:
        # Для неавторизованных пользователей - проверяем в сессии
        session_favorites = get_session_favorites(request)
        is_favorite = product_id in session_favorites
    
    return JsonResponse({'is_favorite': is_favorite})


@csrf_exempt
@require_http_methods(["POST"])
def clear_all_favorites(request):
    """Очистить все избранное"""
    if request.user.is_authenticated:
        # Для авторизованных пользователей - очищаем в БД
        deleted_count = Favorite.objects.filter(user=request.user).delete()[0]
        return JsonResponse({'success': True, 'message': f'Удалено {deleted_count} товаров из избранного'})
    else:
        # Для неавторизованных пользователей - очищаем сессию
        session_favorites = get_session_favorites(request)
        count = len(session_favorites)
        request.session['favorites'] = []
        return JsonResponse({'success': True, 'message': f'Удалено {count} товаров из избранного'})

app_name = 'favorites'

urlpatterns = [
    path('', favorite_list_view, name='favorite_list'),
    path('add/<int:product_id>/', add_to_favorites, name='add_to_favorites'),
    path('remove/<int:product_id>/', remove_from_favorites, name='remove_from_favorites'),
    path('check/<int:product_id>/', check_favorite_status, name='check_favorite_status'),
    path('clear/', clear_all_favorites, name='clear_all_favorites'),
]