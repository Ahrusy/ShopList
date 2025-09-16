from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.db.models import Q, Count
from .models import Order, OrderItem
import json


class OrderListMixin:
    """Миксин для общих методов работы с заказами"""
    
    def get_order_statistics(self, user):
        """Получить статистику заказов пользователя"""
        orders = Order.objects.filter(user=user)
        
        return {
            'total_orders': orders.count(),
            'pending_orders': orders.filter(status='pending').count(),
            'delivered_orders': orders.filter(status='delivered').count(),
            'cancelled_orders': orders.filter(status='cancelled').count(),
        }
    
    def get_status_filters(self):
        """Получить фильтры по статусу заказа"""
        return [
            {'value': 'all', 'label': 'Все заказы'},
            {'value': 'pending', 'label': 'В обработке'},
            {'value': 'processing', 'label': 'Обрабатывается'},
            {'value': 'shipped', 'label': 'Отправлен'},
            {'value': 'delivered', 'label': 'Доставлен'},
            {'value': 'cancelled', 'label': 'Отменен'},
        ]


@login_required
def order_list(request):
    """Страница списка заказов пользователя"""
    mixin = OrderListMixin()
    
    # Получаем заказы пользователя
    orders = Order.objects.filter(user=request.user).prefetch_related('items__product').order_by('-created_at')
    
    # Фильтрация по статусу
    status_filter = request.GET.get('status', 'all')
    if status_filter != 'all':
        orders = orders.filter(status=status_filter)
    
    # Пагинация
    paginator = Paginator(orders, 10)
    page_number = request.GET.get('page')
    orders_page = paginator.get_page(page_number)
    
    # Статистика
    statistics = mixin.get_order_statistics(request.user)
    
    # Фильтры
    status_filters = mixin.get_status_filters()
    
    context = {
        'orders': orders_page,
        'total_orders': statistics['total_orders'],
        'pending_orders': statistics['pending_orders'],
        'delivered_orders': statistics['delivered_orders'],
        'cancelled_orders': statistics['cancelled_orders'],
        'status_filters': status_filters,
    }
    
    return render(request, 'orders/order_list.html', context)


@login_required
def order_detail(request, order_id):
    """Детальная страница заказа"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    context = {
        'order': order,
    }
    
    return render(request, 'orders/order_detail.html', context)


@login_required
@require_http_methods(["POST"])
def cancel_order(request, order_id):
    """Отмена заказа"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    if order.status in ['pending', 'processing']:
        order.status = 'cancelled'
        order.save()
        
        return JsonResponse({'success': True, 'message': 'Заказ отменен'})
    else:
        return JsonResponse({'success': False, 'message': 'Заказ нельзя отменить'}, status=400)


@login_required
@require_http_methods(["POST"])
def repeat_order(request, order_id):
    """Повторение заказа"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    # Добавляем товары из заказа в корзину
    cart = request.session.get('cart', {})
    
    for item in order.items.all():
        product_id = str(item.product.id)
        if product_id in cart:
            cart[product_id]['quantity'] += item.quantity
        else:
            cart[product_id] = {
                'quantity': item.quantity,
                'price': float(item.product.price)
            }
    
    request.session['cart'] = cart
    request.session.modified = True
    
    return JsonResponse({'success': True, 'message': 'Товары добавлены в корзину'})
