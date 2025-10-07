"""
Аналитика для ShopList
"""

from django.db.models import Count, Sum, Avg, Q
from django.utils import timezone
from datetime import timedelta
from .models import Product, Order, User, Category
import json


class AnalyticsService:
    """Сервис для получения аналитических данных"""
    
    @staticmethod
    def get_dashboard_data():
        """Получает данные для дашборда аналитики"""
        now = timezone.now()
        last_30_days = now - timedelta(days=30)
        last_7_days = now - timedelta(days=7)
        
        # Основные метрики
        total_products = Product.objects.filter(is_active=True).count()
        total_orders = Order.objects.count()
        total_revenue = Order.objects.filter(
            status='delivered',
            payment_status='paid'
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        
        active_users = User.objects.filter(
            last_login__gte=last_30_days
        ).count()
        
        # Топ товары по просмотрам
        top_products = Product.objects.filter(
            is_active=True
        ).order_by('-views_count')[:10]
        
        # Данные для графика продаж (последние 7 дней)
        sales_data = []
        sales_labels = []
        
        for i in range(7):
            date = now - timedelta(days=6-i)
            day_orders = Order.objects.filter(
                created_at__date=date.date(),
                status='delivered',
                payment_status='paid'
            ).aggregate(total=Sum('total_amount'))['total'] or 0
            
            sales_data.append(float(day_orders))
            sales_labels.append(date.strftime('%d.%m'))
        
        # Данные для графика категорий
        categories_data = []
        categories_labels = []
        
        category_stats = Category.objects.annotate(
            product_count=Count('products', filter=Q(products__is_active=True))
        ).filter(product_count__gt=0).order_by('-product_count')[:7]
        
        for category in category_stats:
            categories_data.append(category.product_count)
            categories_labels.append(category.name)
        
        return {
            'total_products': total_products,
            'total_orders': total_orders,
            'total_revenue': total_revenue,
            'active_users': active_users,
            'top_products': top_products,
            'sales_data': json.dumps(sales_data),
            'sales_labels': json.dumps(sales_labels),
            'categories_data': json.dumps(categories_data),
            'categories_labels': json.dumps(categories_labels),
        }
    
    @staticmethod
    def get_product_analytics(product_id):
        """Получает аналитику для конкретного товара"""
        try:
            product = Product.objects.get(id=product_id)
            
            # Статистика просмотров за последние 30 дней
            now = timezone.now()
            views_data = []
            views_labels = []
            
            for i in range(30):
                date = now - timedelta(days=29-i)
                # Здесь можно добавить модель для отслеживания просмотров по дням
                # Пока используем случайные данные для демонстрации
                views_data.append(product.views_count // 30)
                views_labels.append(date.strftime('%d.%m'))
            
            return {
                'product': product,
                'views_data': json.dumps(views_data),
                'views_labels': json.dumps(views_labels),
                'total_views': product.views_count,
                'rating': product.rating,
                'reviews_count': product.reviews_count,
            }
        except Product.DoesNotExist:
            return None
    
    @staticmethod
    def get_sales_analytics(period='30d'):
        """Получает аналитику продаж за период"""
        now = timezone.now()
        
        if period == '7d':
            start_date = now - timedelta(days=7)
            date_format = '%d.%m'
        elif period == '30d':
            start_date = now - timedelta(days=30)
            date_format = '%d.%m'
        elif period == '90d':
            start_date = now - timedelta(days=90)
            date_format = '%d.%m'
        else:
            start_date = now - timedelta(days=30)
            date_format = '%d.%m'
        
        orders = Order.objects.filter(
            created_at__gte=start_date,
            status='delivered',
            payment_status='paid'
        ).values('created_at__date').annotate(
            total=Sum('total_amount'),
            count=Count('id')
        ).order_by('created_at__date')
        
        sales_data = []
        sales_labels = []
        
        for order in orders:
            sales_data.append(float(order['total']))
            sales_labels.append(order['created_at__date'].strftime(date_format))
        
        return {
            'sales_data': json.dumps(sales_data),
            'sales_labels': json.dumps(sales_labels),
        }
    
    @staticmethod
    def get_user_analytics():
        """Получает аналитику пользователей"""
        now = timezone.now()
        last_30_days = now - timedelta(days=30)
        
        # Регистрации за последние 30 дней
        registrations = User.objects.filter(
            date_joined__gte=last_30_days
        ).extra(
            select={'day': 'date(date_joined)'}
        ).values('day').annotate(
            count=Count('id')
        ).order_by('day')
        
        reg_data = []
        reg_labels = []
        
        for reg in registrations:
            reg_data.append(reg['count'])
            reg_labels.append(reg['day'].strftime('%d.%m'))
        
        # Активность пользователей по ролям
        role_stats = User.objects.values('role').annotate(
            count=Count('id')
        ).order_by('role')
        
        role_data = []
        role_labels = []
        
        for role in role_stats:
            role_data.append(role['count'])
            role_labels.append(dict(User.ROLE_CHOICES).get(role['role'], role['role']))
        
        return {
            'registrations_data': json.dumps(reg_data),
            'registrations_labels': json.dumps(reg_labels),
            'roles_data': json.dumps(role_data),
            'roles_labels': json.dumps(role_labels),
        }