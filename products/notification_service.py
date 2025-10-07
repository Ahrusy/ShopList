"""
Сервис уведомлений для ShopList
Поддерживает email и push уведомления
"""

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.translation import gettext as _
from django.contrib.auth import get_user_model
from .models import Notification
import logging
import json

logger = logging.getLogger(__name__)
User = get_user_model()


class NotificationService:
    """Сервис для отправки уведомлений"""
    
    @staticmethod
    def create_notification(user, notification_type, title, message, extra_data=None):
        """Создает уведомление в базе данных"""
        try:
            notification = Notification.objects.create(
                user=user,
                type=notification_type,
                title=title,
                message=message
            )
            logger.info(f"Notification created: {notification.id} for user {user.username}")
            return notification
        except Exception as e:
            logger.error(f"Error creating notification: {e}")
            return None
    
    @staticmethod
    def send_email_notification(user, subject, template_name, context=None, from_email=None):
        """Отправляет email уведомление"""
        try:
            if not user.email:
                logger.warning(f"User {user.username} has no email address")
                return False
            
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
                from_email=from_email or settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False
            )
            
            logger.info(f"Email sent to {user.email}: {subject}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending email to {user.email}: {e}")
            return False
    
    @staticmethod
    def send_push_notification(user, title, message, data=None):
        """Отправляет push уведомление (заглушка для будущей реализации)"""
        try:
            # TODO: Implement push notifications with FCM or similar service
            logger.info(f"Push notification would be sent to {user.username}: {title}")
            return True
        except Exception as e:
            logger.error(f"Error sending push notification: {e}")
            return False
    
    @classmethod
    def notify_order_created(cls, order):
        """Уведомление о создании заказа"""
        user = order.user
        
        # Создаем уведомление в БД
        cls.create_notification(
            user=user,
            notification_type='order_created',
            title=_('Заказ создан'),
            message=_('Ваш заказ №{} успешно создан').format(order.order_number)
        )
        
        # Отправляем email
        cls.send_email_notification(
            user=user,
            subject=_('Заказ №{} создан - ShopList').format(order.order_number),
            template_name='order_created',
            context={'order': order}
        )
        
        # Отправляем push уведомление
        cls.send_push_notification(
            user=user,
            title=_('Заказ создан'),
            message=_('Заказ №{} на сумму {} ₽').format(order.order_number, order.total_amount)
        )
    
    @classmethod
    def notify_order_confirmed(cls, order):
        """Уведомление о подтверждении заказа"""
        user = order.user
        
        cls.create_notification(
            user=user,
            notification_type='order_confirmed',
            title=_('Заказ подтвержден'),
            message=_('Ваш заказ №{} подтвержден и принят в обработку').format(order.order_number)
        )
        
        cls.send_email_notification(
            user=user,
            subject=_('Заказ №{} подтвержден - ShopList').format(order.order_number),
            template_name='order_confirmed',
            context={'order': order}
        )
    
    @classmethod
    def notify_order_shipped(cls, order):
        """Уведомление об отправке заказа"""
        user = order.user
        
        cls.create_notification(
            user=user,
            notification_type='order_shipped',
            title=_('Заказ отправлен'),
            message=_('Ваш заказ №{} отправлен и скоро будет доставлен').format(order.order_number)
        )
        
        cls.send_email_notification(
            user=user,
            subject=_('Заказ №{} отправлен - ShopList').format(order.order_number),
            template_name='order_shipped',
            context={'order': order}
        )
    
    @classmethod
    def notify_order_delivered(cls, order):
        """Уведомление о доставке заказа"""
        user = order.user
        
        cls.create_notification(
            user=user,
            notification_type='order_delivered',
            title=_('Заказ доставлен'),
            message=_('Ваш заказ №{} успешно доставлен').format(order.order_number)
        )
        
        cls.send_email_notification(
            user=user,
            subject=_('Заказ №{} доставлен - ShopList').format(order.order_number),
            template_name='order_delivered',
            context={'order': order}
        )
    
    @classmethod
    def notify_order_cancelled(cls, order):
        """Уведомление об отмене заказа"""
        user = order.user
        
        cls.create_notification(
            user=user,
            notification_type='order_cancelled',
            title=_('Заказ отменен'),
            message=_('Ваш заказ №{} был отменен').format(order.order_number)
        )
        
        cls.send_email_notification(
            user=user,
            subject=_('Заказ №{} отменен - ShopList').format(order.order_number),
            template_name='order_cancelled',
            context={'order': order}
        )
    
    @classmethod
    def notify_review_added(cls, review):
        """Уведомление о добавлении отзыва"""
        # Уведомляем продавца о новом отзыве
        if review.product.seller:
            seller_user = review.product.seller.user
            
            cls.create_notification(
                user=seller_user,
                notification_type='review_added',
                title=_('Новый отзыв'),
                message=_('Получен новый отзыв на товар "{}"').format(review.product.name)
            )
            
            cls.send_email_notification(
                user=seller_user,
                subject=_('Новый отзыв на товар - ShopList'),
                template_name='review_added',
                context={'review': review}
            )
    
    @classmethod
    def notify_product_updated(cls, product, updated_by):
        """Уведомление об обновлении товара"""
        # Уведомляем пользователей, добавивших товар в избранное
        favorite_users = User.objects.filter(favorites=product)
        
        for user in favorite_users:
            cls.create_notification(
                user=user,
                notification_type='product_updated',
                title=_('Товар обновлен'),
                message=_('Товар "{}" из вашего избранного был обновлен').format(product.name)
            )
    
    @classmethod
    def notify_promo_code(cls, users, promo_code):
        """Уведомление о промокоде"""
        for user in users:
            cls.create_notification(
                user=user,
                notification_type='promo_code',
                title=_('Новый промокод'),
                message=_('Доступен новый промокод: {}').format(promo_code.code)
            )
            
            cls.send_email_notification(
                user=user,
                subject=_('Новый промокод - ShopList'),
                template_name='promo_code',
                context={'promo_code': promo_code}
            )
    
    @classmethod
    def get_user_notifications(cls, user, limit=10, unread_only=False):
        """Получает уведомления пользователя"""
        queryset = user.user_notifications.all()
        
        if unread_only:
            queryset = queryset.filter(is_read=False)
        
        return queryset.order_by('-created_at')[:limit]
    
    @classmethod
    def mark_notification_as_read(cls, notification_id, user):
        """Отмечает уведомление как прочитанное"""
        try:
            notification = Notification.objects.get(id=notification_id, user=user)
            notification.is_read = True
            notification.save()
            return True
        except Notification.DoesNotExist:
            return False
    
    @classmethod
    def mark_all_notifications_as_read(cls, user):
        """Отмечает все уведомления пользователя как прочитанные"""
        count = user.user_notifications.filter(is_read=False).update(is_read=True)
        return count
    
    @classmethod
    def get_unread_count(cls, user):
        """Возвращает количество непрочитанных уведомлений"""
        return user.user_notifications.filter(is_read=False).count()


# Функции-хелперы для быстрого использования
def notify_user(user, title, message, notification_type='general', send_email=False, email_template=None):
    """Быстрая отправка уведомления пользователю"""
    service = NotificationService()
    
    # Создаем уведомление в БД
    service.create_notification(user, notification_type, title, message)
    
    # Отправляем email если нужно
    if send_email and email_template:
        service.send_email_notification(
            user=user,
            subject=title,
            template_name=email_template,
            context={'title': title, 'message': message}
        )


def bulk_notify_users(users, title, message, notification_type='general'):
    """Массовая отправка уведомлений"""
    service = NotificationService()
    
    for user in users:
        service.create_notification(user, notification_type, title, message)


def send_welcome_email(user):
    """Отправляет приветственное письмо новому пользователю"""
    service = NotificationService()
    
    service.send_email_notification(
        user=user,
        subject=_('Добро пожаловать в ShopList!'),
        template_name='welcome',
        context={'user': user}
    )