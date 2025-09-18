from django.urls import path
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from products.models import Favorite, Product

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
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Требуется авторизация'}, status=401)
    
    product = get_object_or_404(Product, id=product_id)
    favorite, created = Favorite.objects.get_or_create(
        user=request.user,
        product=product
    )
    
    if created:
        return JsonResponse({'success': True, 'message': 'Товар добавлен в избранное'})
    else:
        return JsonResponse({'success': False, 'message': 'Товар уже в избранном'})


@csrf_exempt
@require_http_methods(["POST"])
def remove_from_favorites(request, product_id):
    """Удалить товар из избранного"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Требуется авторизация'}, status=401)
    
    product = get_object_or_404(Product, id=product_id)
    try:
        favorite = Favorite.objects.get(user=request.user, product=product)
        favorite.delete()
        return JsonResponse({'success': True, 'message': 'Товар удален из избранного'})
    except Favorite.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Товар не найден в избранном'})


@require_http_methods(["GET"])
def check_favorite_status(request, product_id):
    """Проверить статус товара в избранном"""
    if not request.user.is_authenticated:
        return JsonResponse({'is_favorite': False})
    
    product = get_object_or_404(Product, id=product_id)
    is_favorite = Favorite.objects.filter(user=request.user, product=product).exists()
    
    return JsonResponse({'is_favorite': is_favorite})

app_name = 'favorites'

urlpatterns = [
    path('', favorite_list_view, name='favorite_list'),
    path('add/<int:product_id>/', add_to_favorites, name='add_to_favorites'),
    path('remove/<int:product_id>/', remove_from_favorites, name='remove_from_favorites'),
    path('check/<int:product_id>/', check_favorite_status, name='check_favorite_status'),
]
