from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse_lazy
from django.utils import timezone
from .models import PromoCode, Order, Cart, CartItem
from .forms import PromoCodeForm
import json

class PromoCodeListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """Список промокодов (для администраторов)"""
    model = PromoCode
    template_name = 'promo/promo_list.html'
    context_object_name = 'promo_codes'
    paginate_by = 20
    
    def test_func(self):
        return self.request.user.is_staff
    
    def get_queryset(self):
        return PromoCode.objects.all().order_by('-created_at')

class PromoCodeCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """Создание промокода"""
    model = PromoCode
    form_class = PromoCodeForm
    template_name = 'promo/promo_form.html'
    success_url = reverse_lazy('promo_list')
    
    def test_func(self):
        return self.request.user.is_staff
    
    def form_valid(self, form):
        messages.success(self.request, _("Промокод успешно создан!"))
        return super().form_valid(form)

class PromoCodeUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Редактирование промокода"""
    model = PromoCode
    form_class = PromoCodeForm
    template_name = 'promo/promo_form.html'
    success_url = reverse_lazy('promo_list')
    
    def test_func(self):
        return self.request.user.is_staff
    
    def form_valid(self, form):
        messages.success(self.request, _("Промокод успешно обновлен!"))
        return super().form_valid(form)

class PromoCodeDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Удаление промокода"""
    model = PromoCode
    template_name = 'promo/promo_confirm_delete.html'
    success_url = reverse_lazy('promo_list')
    
    def test_func(self):
        return self.request.user.is_staff
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, _("Промокод удален!"))
        return super().delete(request, *args, **kwargs)

@login_required
def apply_promo_code(request):
    """Применить промокод к корзине (AJAX)"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Метод не разрешен'}, status=405)
    
    try:
        data = json.loads(request.body)
        promo_code = data.get('promo_code')
        
        if not promo_code:
            return JsonResponse({'error': 'Код промокода не указан'}, status=400)
        
        # Получаем промокод
        promo = get_object_or_404(PromoCode, code=promo_code)
        
        # Проверяем валидность
        if not promo.is_valid():
            return JsonResponse({'error': 'Промокод недействителен'}, status=400)
        
        # Получаем корзину пользователя
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_items = cart.items.all()
        
        if not cart_items.exists():
            return JsonResponse({'error': 'Корзина пуста'}, status=400)
        
        # Рассчитываем общую сумму корзины
        total_amount = sum(item.total_price for item in cart_items)
        
        # Проверяем минимальную сумму заказа
        if total_amount < promo.min_order_amount:
            return JsonResponse({
                'error': f'Минимальная сумма заказа для этого промокода: {promo.min_order_amount} ₽'
            }, status=400)
        
        # Рассчитываем скидку
        discount_amount = promo.calculate_discount(total_amount)
        
        if discount_amount <= 0:
            return JsonResponse({'error': 'Скидка не применяется'}, status=400)
        
        # Сохраняем промокод в сессии
        request.session['applied_promo_code'] = promo.code
        request.session['promo_discount'] = float(discount_amount)
        
        return JsonResponse({
            'success': True,
            'discount_amount': float(discount_amount),
            'new_total': float(total_amount - discount_amount),
            'message': f'Промокод применен! Скидка: {discount_amount} ₽'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Неверный формат данных'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def remove_promo_code(request):
    """Удалить промокод из корзины (AJAX)"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Метод не разрешен'}, status=405)
    
    # Удаляем промокод из сессии
    if 'applied_promo_code' in request.session:
        del request.session['applied_promo_code']
    if 'promo_discount' in request.session:
        del request.session['promo_discount']
    
    return JsonResponse({'success': True, 'message': 'Промокод удален'})

@login_required
def check_promo_code(request, code):
    """Проверить промокод (AJAX)"""
    try:
        promo = get_object_or_404(PromoCode, code=code)
        
        if not promo.is_valid():
            return JsonResponse({'valid': False, 'message': 'Промокод недействителен'})
        
        return JsonResponse({
            'valid': True,
            'discount_type': promo.discount_type,
            'discount_value': float(promo.discount_value),
            'min_order_amount': float(promo.min_order_amount),
            'message': 'Промокод действителен'
        })
        
    except PromoCode.DoesNotExist:
        return JsonResponse({'valid': False, 'message': 'Промокод не найден'})

@login_required
def promo_codes_available(request):
    """Список доступных промокодов для пользователя"""
    now = timezone.now()
    promo_codes = PromoCode.objects.filter(
        is_active=True,
        valid_from__lte=now,
        valid_until__gte=now
    ).order_by('-discount_value')
    
    context = {
        'promo_codes': promo_codes,
    }
    return render(request, 'promo/available_promo_codes.html', context)

@login_required
def promo_code_stats(request):
    """Статистика использования промокодов (для администраторов)"""
    if not request.user.is_staff:
        messages.error(request, _("У вас нет прав для просмотра статистики."))
        return redirect('index')
    
    promo_codes = PromoCode.objects.all().order_by('-created_at')
    
    # Статистика использования
    total_promo_codes = promo_codes.count()
    active_promo_codes = promo_codes.filter(is_active=True).count()
    total_uses = sum(promo.used_count for promo in promo_codes)
    
    # Топ промокоды по использованию
    top_promo_codes = promo_codes.order_by('-used_count')[:10]
    
    context = {
        'total_promo_codes': total_promo_codes,
        'active_promo_codes': active_promo_codes,
        'total_uses': total_uses,
        'top_promo_codes': top_promo_codes,
    }
    return render(request, 'promo/promo_stats.html', context)
