from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.db import transaction
from django.core.paginator import Paginator
from .models import User, Order, Favorite, Product
from .profile_forms import ProfileUpdateForm


@login_required
def profile_dashboard(request):
    """Главная страница личного кабинета"""
    user_orders = Order.objects.filter(user=request.user).order_by('-created_at')[:5]
    total_orders = Order.objects.filter(user=request.user).count()
    
    stats = {
        'total_orders': total_orders,
        'pending_orders': Order.objects.filter(user=request.user, status='pending').count(),
        'completed_orders': Order.objects.filter(user=request.user, status='delivered').count(),
        'total_spent': sum(order.total_amount for order in Order.objects.filter(user=request.user, status='delivered'))
    }
    
    context = {
        'user_orders': user_orders,
        'stats': stats,
    }
    return render(request, 'profile/dashboard.html', context)


@login_required
def profile_edit(request):
    """Редактирование профиля"""
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль успешно обновлен!')
            return redirect('profile:dashboard')
    else:
        form = ProfileUpdateForm(instance=request.user)
    
    context = {
        'form': form,
    }
    return render(request, 'profile/edit.html', context)


@login_required
def profile_orders(request):
    """Список заказов пользователя"""
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    
    # Пагинация
    paginator = Paginator(orders, 10)
    page_number = request.GET.get('page')
    orders = paginator.get_page(page_number)
    
    context = {
        'orders': orders,
    }
    return render(request, 'profile/orders.html', context)


@login_required
def profile_favorites(request):
    """Список избранных товаров"""
    favorites = Favorite.objects.filter(user=request.user).select_related('product')
    
    context = {
        'favorites': favorites,
    }
    return render(request, 'profile/favorites.html', context)


@login_required
def profile_settings(request):
    """Настройки аккаунта"""
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Пароль успешно изменен!')
            return redirect('profile:settings')
    else:
        form = PasswordChangeForm(request.user)
    
    context = {
        'form': form,
    }
    return render(request, 'profile/settings.html', context)