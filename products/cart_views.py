from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from .models import Cart, CartItem, Product
from django.utils.translation import gettext_lazy as _
import json


def get_session_cart(request):
    """Получить корзину из сессии"""
    if 'cart' not in request.session:
        request.session['cart'] = {}
    return request.session['cart']


def save_session_cart(request, cart):
    """Сохранить корзину в сессию"""
    request.session['cart'] = cart


def get_cart_items(request):
    """Получить товары корзины (из БД для авторизованных или из сессии для неавторизованных)"""
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        return cart.items.select_related('product').prefetch_related('product__images')
    else:
        session_cart = get_session_cart(request)
        cart_items = []
        for product_id, quantity in session_cart.items():
            try:
                product = Product.objects.get(id=product_id)
                cart_items.append({
                    'product': product,
                    'quantity': quantity,
                    'total_price': product.price * quantity
                })
            except Product.DoesNotExist:
                continue
        return cart_items


def get_cart_total_items(request):
    """Получить общее количество товаров в корзине"""
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        return cart.total_items
    else:
        session_cart = get_session_cart(request)
        return sum(session_cart.values())


def get_cart_total_price(request):
    """Получить общую стоимость корзины"""
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        return cart.total_price
    else:
        session_cart = get_session_cart(request)
        total = 0
        for product_id, quantity in session_cart.items():
            try:
                product = Product.objects.get(id=product_id)
                total += product.price * quantity
            except Product.DoesNotExist:
                continue
        return total


def cart_view(request):
    """Страница корзины"""
    cart_items = get_cart_items(request)
    cart_total_items = get_cart_total_items(request)
    cart_total_price = get_cart_total_price(request)
    
    # Получаем рекомендуемые товары (исключая те, что уже в корзине)
    cart_product_ids = []
    if request.user.is_authenticated:
        cart_product_ids = [item.product.id for item in cart_items]
    else:
        cart_product_ids = [int(pid) for pid in get_session_cart(request).keys()]
    
    recommended_products = Product.objects.filter(
        is_active=True
    ).exclude(
        id__in=cart_product_ids
    ).order_by('?')[:12]  # Случайные товары для демонстрации
    
    context = {
        'cart_items': cart_items,
        'cart_total_items': cart_total_items,
        'cart_total_price': cart_total_price,
        'user_authenticated': request.user.is_authenticated,
        'recommended_products': recommended_products,
    }
    return render(request, 'cart.html', context)


@csrf_exempt
@require_POST
def add_to_cart(request, product_id):
    """Добавить товар в корзину"""
    product = get_object_or_404(Product, id=product_id)
    
    # Получаем данные из JSON или POST
    if request.content_type == 'application/json':
        data = json.loads(request.body)
        quantity = int(data.get('quantity', 1))
    else:
        quantity = int(request.POST.get('quantity', 1))
    
    if quantity <= 0:
        return JsonResponse({'success': False, 'message': 'Количество должно быть больше 0'})
    
    if quantity > product.stock_quantity:
        return JsonResponse({'success': False, 'message': 'Недостаточно товара на складе'})
    
    if request.user.is_authenticated:
        # Для авторизованных пользователей - работаем с БД
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
        
        cart_total_items = cart.total_items
        cart_total_price = cart.total_price
    else:
        # Для неавторизованных пользователей - работаем с сессией
        session_cart = get_session_cart(request)
        product_id_str = str(product_id)
        
        if product_id_str in session_cart:
            session_cart[product_id_str] += quantity
        else:
            session_cart[product_id_str] = quantity
        
        # Проверяем лимит склада
        if session_cart[product_id_str] > product.stock_quantity:
            session_cart[product_id_str] = product.stock_quantity
        
        save_session_cart(request, session_cart)
        cart_total_items = get_cart_total_items(request)
        cart_total_price = get_cart_total_price(request)
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': f'Товар "{product.name}" добавлен в корзину',
            'cart_total_items': cart_total_items,
            'cart_total_price': str(cart_total_price)
        })
    else:
        messages.success(request, f'Товар "{product.name}" добавлен в корзину')
        return redirect('cart')


@csrf_exempt
@require_POST
def update_cart_item(request, product_id):
    """Обновить количество товара в корзине"""
    product = get_object_or_404(Product, id=product_id)
    
    # Получаем данные из JSON или POST
    if request.content_type == 'application/json':
        data = json.loads(request.body)
        quantity = int(data.get('quantity', 1))
    else:
        quantity = int(request.POST.get('quantity', 1))
    
    if quantity <= 0:
        # Удаляем товар из корзины
        if request.user.is_authenticated:
            try:
                cart_item = CartItem.objects.get(cart__user=request.user, product=product)
                cart_item.delete()
            except CartItem.DoesNotExist:
                pass
        else:
            session_cart = get_session_cart(request)
            product_id_str = str(product_id)
            if product_id_str in session_cart:
                del session_cart[product_id_str]
                save_session_cart(request, session_cart)
        
        message = 'Товар удален из корзины'
    else:
        if quantity > product.stock_quantity:
            quantity = product.stock_quantity
            message = f'Количество ограничено наличием на складе ({quantity} шт.)'
        else:
            message = 'Количество обновлено'
        
        if request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=request.user)
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                defaults={'quantity': quantity}
            )
            if not created:
                cart_item.quantity = quantity
                cart_item.save()
        else:
            session_cart = get_session_cart(request)
            session_cart[str(product_id)] = quantity
            save_session_cart(request, session_cart)
    
    cart_total_items = get_cart_total_items(request)
    cart_total_price = get_cart_total_price(request)
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': message,
            'cart_total_items': cart_total_items,
            'cart_total_price': str(cart_total_price)
        })
    else:
        messages.success(request, message)
        return redirect('cart')


@csrf_exempt
@require_POST
def remove_from_cart(request, product_id):
    """Удалить товар из корзины"""
    product = get_object_or_404(Product, id=product_id)
    
    if request.user.is_authenticated:
        try:
            cart_item = CartItem.objects.get(cart__user=request.user, product=product)
            cart_item.delete()
        except CartItem.DoesNotExist:
            pass
    else:
        session_cart = get_session_cart(request)
        product_id_str = str(product_id)
        if product_id_str in session_cart:
            del session_cart[product_id_str]
            save_session_cart(request, session_cart)
    
    cart_total_items = get_cart_total_items(request)
    cart_total_price = get_cart_total_price(request)
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': f'Товар "{product.name}" удален из корзины',
            'cart_total_items': cart_total_items,
            'cart_total_price': str(cart_total_price)
        })
    else:
        messages.success(request, f'Товар "{product.name}" удален из корзины')
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
            return redirect('auth:login')
    
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
    count = get_cart_total_items(request)
    total_price = get_cart_total_price(request)
    
    return JsonResponse({
        'count': count,
        'total_price': str(total_price)
    })
