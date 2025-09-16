from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from .models import Cart, CartItem, Product
from django.utils.translation import gettext_lazy as _


def cart_view(request):
    """Страница корзины"""
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_items = cart.items.select_related('product').prefetch_related('product__images')
    else:
        # Для неавторизованных пользователей показываем пустую корзину
        cart = None
        cart_items = CartItem.objects.none()
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
    }
    return render(request, 'cart.html', context)


@csrf_exempt
@require_POST
def add_to_cart(request, product_id):
    """Добавить товар в корзину"""
    if not request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False, 
                'message': 'Необходимо войти в систему',
                'redirect': '/ru/auth/login/'
            }, status=401)
        else:
            messages.error(request, 'Необходимо войти в систему')
            return redirect('login')
    
    product = get_object_or_404(Product, id=product_id)
    
    # Получаем данные из JSON или POST
    if request.content_type == 'application/json':
        import json
        data = json.loads(request.body)
        quantity = int(data.get('quantity', 1))
    else:
        quantity = int(request.POST.get('quantity', 1))
    
    if quantity <= 0:
        return JsonResponse({'success': False, 'message': 'Количество должно быть больше 0'})
    
    if quantity > product.stock_quantity:
        return JsonResponse({'success': False, 'message': 'Недостаточно товара на складе'})
    
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': quantity}
    )
    
    if not created:
        cart_item.quantity += quantity
        if cart_item.quantity > product.stock_quantity:
            cart_item.quantity = product.stock_quantity
        cart_item.save()
    
    # Обновляем корзину
    cart.updated_at = cart.updated_at
    cart.save()
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': f'Товар "{product.name}" добавлен в корзину',
            'cart_total_items': cart.total_items,
            'cart_total_price': cart.total_price
        })
    else:
        messages.success(request, f'Товар "{product.name}" добавлен в корзину')
        return redirect('cart')


@csrf_exempt
@require_POST
def update_cart_item(request, item_id):
    """Обновить количество товара в корзине"""
    if not request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False, 
                'message': 'Необходимо войти в систему',
                'redirect': '/ru/auth/login/'
            }, status=401)
        else:
            messages.error(request, 'Необходимо войти в систему')
            return redirect('login')
    
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    
    # Получаем данные из JSON или POST
    if request.content_type == 'application/json':
        import json
        data = json.loads(request.body)
        quantity = int(data.get('quantity', 1))
    else:
        quantity = int(request.POST.get('quantity', 1))
    
    if quantity <= 0:
        cart_item.delete()
        message = 'Товар удален из корзины'
    else:
        if quantity > cart_item.product.stock_quantity:
            quantity = cart_item.product.stock_quantity
            message = f'Количество ограничено наличием на складе ({quantity} шт.)'
        else:
            message = 'Количество обновлено'
        
        cart_item.quantity = quantity
        cart_item.save()
    
    cart = cart_item.cart
    cart.updated_at = cart.updated_at
    cart.save()
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': message,
            'cart_total_items': cart.total_items,
            'cart_total_price': cart.total_price,
            'item_total_price': cart_item.total_price
        })
    else:
        messages.success(request, message)
        return redirect('cart')


@csrf_exempt
@require_POST
def remove_from_cart(request, item_id):
    """Удалить товар из корзины"""
    if not request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False, 
                'message': 'Необходимо войти в систему',
                'redirect': '/ru/auth/login/'
            }, status=401)
        else:
            messages.error(request, 'Необходимо войти в систему')
            return redirect('login')
    
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    product_name = cart_item.product.name
    cart_item.delete()
    
    cart = cart_item.cart
    cart.updated_at = cart.updated_at
    cart.save()
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': f'Товар "{product_name}" удален из корзины',
            'cart_total_items': cart.total_items,
            'cart_total_price': cart.total_price
        })
    else:
        messages.success(request, f'Товар "{product_name}" удален из корзины')
        return redirect('cart')


@csrf_exempt
@require_POST
def clear_cart(request):
    """Очистить корзину"""
    if not request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False, 
                'message': 'Необходимо войти в систему',
                'redirect': '/ru/auth/login/'
            }, status=401)
        else:
            messages.error(request, 'Необходимо войти в систему')
            return redirect('login')
    
    cart = get_object_or_404(Cart, user=request.user)
    cart.items.all().delete()
    cart.updated_at = cart.updated_at
    cart.save()
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': 'Корзина очищена',
            'cart_total_items': 0,
            'cart_total_price': 0
        })
    else:
        messages.success(request, 'Корзина очищена')
        return redirect('cart')


def cart_count(request):
    """Получить количество товаров в корзине для AJAX"""
    if not request.user.is_authenticated:
        return JsonResponse({'count': 0, 'total_price': 0})
    
    try:
        cart = Cart.objects.get(user=request.user)
        return JsonResponse({
            'count': cart.total_items,
            'total_price': cart.total_price
        })
    except Cart.DoesNotExist:
        return JsonResponse({'count': 0, 'total_price': 0})
