"""
Асинхронные задачи для ShopList
"""

from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.contrib.auth import get_user_model
from .models import Product, Order, Notification
from .notification_service import NotificationService
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


@shared_task(bind=True, max_retries=3)
def send_email_notification(self, user_id, subject, template_name, context=None):
    """Асинхронная отправка email уведомлений"""
    try:
        user = User.objects.get(id=user_id)
        context = context or {}
        context.update({
            'user': user,
            'site_name': getattr(settings, 'SITE_NAME', 'ShopList'),
            'site_url': getattr(settings, 'SITE_URL', 'http://localhost:8000'),
        })
        
        # Render email content
        html_message = render_to_string(f'emails/{template_name}.html', context)
        text_message = render_to_string(f'emails/{template_name}.txt', context)
        
        # Send email
        send_mail(
            subject=subject,
            message=text_message,
            html_message=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False
        )
        
        logger.info(f"Email sent to {user.email}: {subject}")
        return f"Email sent successfully to {user.email}"
        
    except User.DoesNotExist:
        logger.error(f"User with id {user_id} not found")
        return f"User with id {user_id} not found"
    except Exception as exc:
        logger.error(f"Error sending email: {exc}")
        # Retry the task
        raise self.retry(exc=exc, countdown=60)


@shared_task
def update_product_views(product_id):
    """Асинхронное обновление счетчика просмотров товара"""
    try:
        product = Product.objects.get(id=product_id)
        product.views_count += 1
        product.save(update_fields=['views_count'])
        logger.info(f"Updated views for product {product.name}: {product.views_count}")
        return f"Views updated for product {product.name}"
    except Product.DoesNotExist:
        logger.error(f"Product with id {product_id} not found")
        return f"Product with id {product_id} not found"


@shared_task
def process_order_notifications(order_id):
    """Асинхронная обработка уведомлений для заказа"""
    try:
        order = Order.objects.get(id=order_id)
        
        # Отправляем уведомление пользователю
        NotificationService.notify_order_created(order)
        
        # Уведомляем менеджеров магазинов
        for item in order.items.all():
            if item.product.seller:
                NotificationService.create_notification(
                    user=item.product.seller.user,
                    notification_type='order_created',
                    title='Новый заказ',
                    message=f'Получен заказ на товар "{item.product.name}"'
                )
        
        logger.info(f"Notifications processed for order {order.order_number}")
        return f"Notifications sent for order {order.order_number}"
        
    except Order.DoesNotExist:
        logger.error(f"Order with id {order_id} not found")
        return f"Order with id {order_id} not found"


@shared_task
def cleanup_old_notifications():
    """Очистка старых уведомлений (старше 30 дней)"""
    from django.utils import timezone
    from datetime import timedelta
    
    cutoff_date = timezone.now() - timedelta(days=30)
    deleted_count = Notification.objects.filter(
        created_at__lt=cutoff_date,
        is_read=True
    ).delete()[0]
    
    logger.info(f"Cleaned up {deleted_count} old notifications")
    return f"Cleaned up {deleted_count} old notifications"


@shared_task
def generate_analytics_report():
    """Генерация аналитического отчета"""
    from .analytics import AnalyticsService
    
    try:
        analytics_data = AnalyticsService.get_dashboard_data()
        
        # Отправляем отчет администраторам
        admins = User.objects.filter(role='admin', is_active=True)
        
        for admin in admins:
            send_email_notification.delay(
                user_id=admin.id,
                subject='Еженедельный отчет ShopList',
                template_name='analytics_report',
                context={'analytics': analytics_data}
            )
        
        logger.info("Analytics report generated and sent to admins")
        return "Analytics report generated successfully"
        
    except Exception as exc:
        logger.error(f"Error generating analytics report: {exc}")
        return f"Error generating analytics report: {exc}"


@shared_task
def update_product_ratings():
    """Обновление рейтингов товаров на основе отзывов"""
    from django.db.models import Avg
    
    products = Product.objects.all()
    updated_count = 0
    
    for product in products:
        avg_rating = product.reviews.filter(is_moderated=True).aggregate(
            avg_rating=Avg('rating')
        )['avg_rating']
        
        if avg_rating is not None:
            product.rating = round(avg_rating, 2)
            product.reviews_count = product.reviews.filter(is_moderated=True).count()
            product.save(update_fields=['rating', 'reviews_count'])
            updated_count += 1
    
    logger.info(f"Updated ratings for {updated_count} products")
    return f"Updated ratings for {updated_count} products"


@shared_task
def backup_database():
    """Создание резервной копии базы данных"""
    import subprocess
    import os
    from django.utils import timezone
    
    try:
        timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f"shoplist_backup_{timestamp}.sql"
        backup_path = os.path.join(settings.BASE_DIR, 'backups', backup_filename)
        
        # Создаем папку для бэкапов если её нет
        os.makedirs(os.path.dirname(backup_path), exist_ok=True)
        
        # Выполняем pg_dump (для PostgreSQL)
        db_settings = settings.DATABASES['default']
        cmd = [
            'pg_dump',
            f"--host={db_settings['HOST']}",
            f"--port={db_settings['PORT']}",
            f"--username={db_settings['USER']}",
            f"--dbname={db_settings['NAME']}",
            f"--file={backup_path}"
        ]
        
        env = os.environ.copy()
        env['PGPASSWORD'] = db_settings['PASSWORD']
        
        result = subprocess.run(cmd, env=env, capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info(f"Database backup created: {backup_filename}")
            return f"Database backup created: {backup_filename}"
        else:
            logger.error(f"Database backup failed: {result.stderr}")
            return f"Database backup failed: {result.stderr}"
            
    except Exception as exc:
        logger.error(f"Error creating database backup: {exc}")
        return f"Error creating database backup: {exc}"


@shared_task
def send_promotional_emails(user_ids, subject, template_name, context=None):
    """Массовая отправка промо-писем"""
    sent_count = 0
    failed_count = 0
    
    for user_id in user_ids:
        try:
            send_email_notification.delay(user_id, subject, template_name, context)
            sent_count += 1
        except Exception as exc:
            logger.error(f"Failed to queue email for user {user_id}: {exc}")
            failed_count += 1
    
    logger.info(f"Promotional emails queued: {sent_count} sent, {failed_count} failed")
    return f"Promotional emails queued: {sent_count} sent, {failed_count} failed"