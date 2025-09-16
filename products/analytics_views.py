from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import TemplateView
from django.db.models import Sum, Count, Avg, Q
from django.db.models.functions import TruncDay, TruncMonth
from django.utils import timezone
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _
from .models import Product, Order, OrderItem, Review, Seller, Commission
import json

class SellerAnalyticsView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """Аналитический дашборд для продавца"""
    template_name = 'analytics/seller_dashboard.html'
    
    def test_func(self):
        return self.request.user.role in ['seller', 'admin']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        if self.request.user.role == 'seller':
            seller = get_object_or_404(Seller, user=self.request.user)
            products = Product.objects.filter(seller=seller)
        else:  # admin
            seller = None
            products = Product.objects.all()
        
        # Период для анализа (последние 30 дней)
        end_date = timezone.now()
        start_date = end_date - timedelta(days=30)
        
        # Общая статистика
        total_products = products.count()
        active_products = products.filter(is_active=True).count()
        
        # Статистика заказов
        if seller:
            orders = Order.objects.filter(
                items__product__seller=seller
            ).distinct()
        else:
            orders = Order.objects.all()
        
        total_orders = orders.count()
        completed_orders = orders.filter(status='delivered').count()
        pending_orders = orders.filter(status__in=['pending', 'confirmed', 'processing']).count()
        
        # Выручка
        total_revenue = orders.filter(status='delivered').aggregate(
            total=Sum('total_amount')
        )['total'] or 0
        
        # Комиссии
        if seller:
            total_commissions = Commission.objects.filter(seller=seller).aggregate(
                total=Sum('amount')
            )['total'] or 0
        else:
            total_commissions = Commission.objects.aggregate(
                total=Sum('amount')
            )['total'] or 0
        
        # Рейтинг товаров
        avg_rating = products.aggregate(avg=Avg('rating'))['avg'] or 0
        total_reviews = Review.objects.filter(product__in=products).count()
        
        # Топ товары по продажам
        top_products = products.annotate(
            total_sales=Sum('orderitem__quantity')
        ).order_by('-total_sales')[:5]
        
        # График продаж по дням
        sales_by_day = orders.filter(
            created_at__gte=start_date,
            status='delivered'
        ).annotate(
            day=TruncDay('created_at')
        ).values('day').annotate(
            total=Sum('total_amount'),
            count=Count('id')
        ).order_by('day')
        
        # График заказов по месяцам
        orders_by_month = orders.filter(
            created_at__gte=start_date - timedelta(days=365)
        ).annotate(
            month=TruncMonth('created_at')
        ).values('month').annotate(
            total=Sum('total_amount'),
            count=Count('id')
        ).order_by('month')
        
        context.update({
            'seller': seller,
            'total_products': total_products,
            'active_products': active_products,
            'total_orders': total_orders,
            'completed_orders': completed_orders,
            'pending_orders': pending_orders,
            'total_revenue': total_revenue,
            'total_commissions': total_commissions,
            'avg_rating': round(avg_rating, 2),
            'total_reviews': total_reviews,
            'top_products': top_products,
            'sales_by_day': list(sales_by_day),
            'orders_by_month': list(orders_by_month),
        })
        
        return context

@login_required
def analytics_data(request):
    """API для получения данных аналитики (AJAX)"""
    if request.user.role not in ['seller', 'admin']:
        return JsonResponse({'error': 'Нет прав'}, status=403)
    
    chart_type = request.GET.get('type', 'sales')
    period = request.GET.get('period', '30')
    
    try:
        days = int(period)
    except ValueError:
        days = 30
    
    end_date = timezone.now()
    start_date = end_date - timedelta(days=days)
    
    if request.user.role == 'seller':
        seller = get_object_or_404(Seller, user=request.user)
        products = Product.objects.filter(seller=seller)
        orders = Order.objects.filter(
            items__product__seller=seller
        ).distinct()
    else:  # admin
        products = Product.objects.all()
        orders = Order.objects.all()
    
    if chart_type == 'sales':
        # График продаж
        data = orders.filter(
            created_at__gte=start_date,
            status='delivered'
        ).annotate(
            day=TruncDay('created_at')
        ).values('day').annotate(
            total=Sum('total_amount'),
            count=Count('id')
        ).order_by('day')
        
        return JsonResponse({
            'labels': [item['day'].strftime('%Y-%m-%d') for item in data],
            'datasets': [{
                'label': 'Выручка (₽)',
                'data': [float(item['total']) for item in data],
                'borderColor': 'rgb(75, 192, 192)',
                'tension': 0.1
            }]
        })
    
    elif chart_type == 'orders':
        # График заказов
        data = orders.filter(
            created_at__gte=start_date
        ).annotate(
            day=TruncDay('created_at')
        ).values('day').annotate(
            count=Count('id')
        ).order_by('day')
        
        return JsonResponse({
            'labels': [item['day'].strftime('%Y-%m-%d') for item in data],
            'datasets': [{
                'label': 'Количество заказов',
                'data': [item['count'] for item in data],
                'borderColor': 'rgb(255, 99, 132)',
                'tension': 0.1
            }]
        })
    
    elif chart_type == 'products':
        # Топ товары
        data = products.annotate(
            total_sales=Sum('orderitem__quantity'),
            total_revenue=Sum('orderitem__total_price')
        ).order_by('-total_sales')[:10]
        
        return JsonResponse({
            'labels': [product.name[:30] + '...' if len(product.name) > 30 else product.name for product in data],
            'datasets': [{
                'label': 'Продажи (шт.)',
                'data': [product.total_sales or 0 for product in data],
                'backgroundColor': 'rgba(54, 162, 235, 0.2)',
                'borderColor': 'rgba(54, 162, 235, 1)',
                'borderWidth': 1
            }]
        })
    
    elif chart_type == 'reviews':
        # Распределение отзывов по рейтингам
        reviews = Review.objects.filter(product__in=products)
        rating_data = {}
        for i in range(1, 6):
            rating_data[i] = reviews.filter(rating=i).count()
        
        return JsonResponse({
            'labels': ['1 звезда', '2 звезды', '3 звезды', '4 звезды', '5 звезд'],
            'datasets': [{
                'label': 'Количество отзывов',
                'data': [rating_data[i] for i in range(1, 6)],
                'backgroundColor': [
                    'rgba(255, 99, 132, 0.2)',
                    'rgba(255, 205, 86, 0.2)',
                    'rgba(54, 162, 235, 0.2)',
                    'rgba(75, 192, 192, 0.2)',
                    'rgba(153, 102, 255, 0.2)'
                ],
                'borderColor': [
                    'rgba(255, 99, 132, 1)',
                    'rgba(255, 205, 86, 1)',
                    'rgba(54, 162, 235, 1)',
                    'rgba(75, 192, 192, 1)',
                    'rgba(153, 102, 255, 1)'
                ],
                'borderWidth': 1
            }]
        })
    
    return JsonResponse({'error': 'Неверный тип графика'}, status=400)

@login_required
def export_analytics(request):
    """Экспорт аналитики в CSV"""
    if request.user.role not in ['seller', 'admin']:
        return JsonResponse({'error': 'Нет прав'}, status=403)
    
    import csv
    from django.http import HttpResponse
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="analytics.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Дата', 'Заказы', 'Выручка', 'Товары'])
    
    # Данные за последние 30 дней
    end_date = timezone.now()
    start_date = end_date - timedelta(days=30)
    
    if request.user.role == 'seller':
        seller = get_object_or_404(Seller, user=request.user)
        orders = Order.objects.filter(
            items__product__seller=seller
        ).distinct()
    else:
        orders = Order.objects.all()
    
    data = orders.filter(
        created_at__gte=start_date,
        status='delivered'
    ).annotate(
        day=TruncDay('created_at')
    ).values('day').annotate(
        total=Sum('total_amount'),
        count=Count('id')
    ).order_by('day')
    
    for item in data:
        writer.writerow([
            item['day'].strftime('%Y-%m-%d'),
            item['count'],
            item['total'],
            0  # Количество товаров можно добавить отдельно
        ])
    
    return response
