"""
Утилиты для отправки email писем
"""
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string
import logging

logger = logging.getLogger(__name__)


class EmailService:
    """Сервис для отправки email писем"""
    
    @staticmethod
    def send_verification_code(email, code, user_name=None):
        """Отправка кода подтверждения регистрации"""
        subject = 'Подтверждение регистрации - ShopList'
        
        # HTML версия письма
        html_message = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #007bff; color: white; padding: 20px; text-align: center; border-radius: 5px 5px 0 0; }}
                .content {{ background: #f8f9fa; padding: 30px; border-radius: 0 0 5px 5px; }}
                .code {{ background: #007bff; color: white; font-size: 24px; font-weight: bold; padding: 15px; text-align: center; border-radius: 5px; margin: 20px 0; letter-spacing: 3px; }}
                .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>ShopList</h1>
                    <p>Подтверждение регистрации</p>
                </div>
                <div class="content">
                    <h2>Добро пожаловать в ShopList{f", {user_name}" if user_name else ""}!</h2>
                    <p>Для завершения регистрации введите следующий код подтверждения:</p>
                    <div class="code">{code}</div>
                    <p><strong>Важно:</strong></p>
                    <ul>
                        <li>Код действителен в течение 10 минут</li>
                        <li>Не передавайте этот код третьим лицам</li>
                        <li>Если вы не регистрировались на нашем сайте, проигнорируйте это письмо</li>
                    </ul>
                    <p>С уважением,<br>Команда ShopList</p>
                </div>
                <div class="footer">
                    <p>Это автоматическое сообщение, не отвечайте на него</p>
                </div>
            </div>
        </body>
        </html>
        '''
        
        # Текстовая версия письма
        message = f'''
        Добро пожаловать в ShopList{f", {user_name}" if user_name else ""}!
        
        Ваш код подтверждения: {code}
        
        Введите этот код для завершения регистрации.
        Код действителен в течение 10 минут.
        
        Если вы не регистрировались на нашем сайте, проигнорируйте это письмо.
        
        С уважением,
        Команда ShopList
        '''
        
        return EmailService._send_email(email, subject, message, html_message)
    
    @staticmethod
    def send_order_confirmation(email, order, user_name=None):
        """Отправка подтверждения заказа"""
        subject = f'Подтверждение заказа #{order.id} - ShopList'
        
        # HTML версия письма
        html_message = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #28a745; color: white; padding: 20px; text-align: center; border-radius: 5px 5px 0 0; }}
                .content {{ background: #f8f9fa; padding: 30px; border-radius: 0 0 5px 5px; }}
                .order-info {{ background: white; padding: 20px; border-radius: 5px; margin: 20px 0; }}
                .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>ShopList</h1>
                    <p>Подтверждение заказа</p>
                </div>
                <div class="content">
                    <h2>Спасибо за заказ{f", {user_name}" if user_name else ""}!</h2>
                    <div class="order-info">
                        <h3>Детали заказа:</h3>
                        <p><strong>Номер заказа:</strong> #{order.id}</p>
                        <p><strong>Дата:</strong> {order.created_at.strftime('%d.%m.%Y %H:%M')}</p>
                        <p><strong>Сумма:</strong> {order.total_amount} ₽</p>
                        <p><strong>Статус:</strong> {order.get_status_display()}</p>
                    </div>
                    <p>Мы обработаем ваш заказ в ближайшее время.</p>
                    <p>С уважением,<br>Команда ShopList</p>
                </div>
                <div class="footer">
                    <p>Это автоматическое сообщение, не отвечайте на него</p>
                </div>
            </div>
        </body>
        </html>
        '''
        
        # Текстовая версия письма
        message = f'''
        Спасибо за заказ{f", {user_name}" if user_name else ""}!
        
        Детали заказа:
        Номер заказа: #{order.id}
        Дата: {order.created_at.strftime('%d.%m.%Y %H:%M')}
        Сумма: {order.total_amount} ₽
        Статус: {order.get_status_display()}
        
        Мы обработаем ваш заказ в ближайшее время.
        
        С уважением,
        Команда ShopList
        '''
        
        return EmailService._send_email(email, subject, message, html_message)
    
    @staticmethod
    def send_password_reset(email, reset_link, user_name=None):
        """Отправка ссылки для сброса пароля"""
        subject = 'Сброс пароля - ShopList'
        
        # HTML версия письма
        html_message = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #dc3545; color: white; padding: 20px; text-align: center; border-radius: 5px 5px 0 0; }}
                .content {{ background: #f8f9fa; padding: 30px; border-radius: 0 0 5px 5px; }}
                .button {{ background: #dc3545; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 20px 0; }}
                .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>ShopList</h1>
                    <p>Сброс пароля</p>
                </div>
                <div class="content">
                    <h2>Сброс пароля{f", {user_name}" if user_name else ""}</h2>
                    <p>Вы запросили сброс пароля для вашего аккаунта.</p>
                    <p>Нажмите на кнопку ниже, чтобы создать новый пароль:</p>
                    <a href="{reset_link}" class="button">Сбросить пароль</a>
                    <p><strong>Важно:</strong></p>
                    <ul>
                        <li>Ссылка действительна в течение 24 часов</li>
                        <li>Если вы не запрашивали сброс пароля, проигнорируйте это письмо</li>
                    </ul>
                    <p>С уважением,<br>Команда ShopList</p>
                </div>
                <div class="footer">
                    <p>Это автоматическое сообщение, не отвечайте на него</p>
                </div>
            </div>
        </body>
        </html>
        '''
        
        # Текстовая версия письма
        message = f'''
        Сброс пароля{f", {user_name}" if user_name else ""}
        
        Вы запросили сброс пароля для вашего аккаунта.
        
        Перейдите по ссылке для создания нового пароля:
        {reset_link}
        
        Ссылка действительна в течение 24 часов.
        
        Если вы не запрашивали сброс пароля, проигнорируйте это письмо.
        
        С уважением,
        Команда ShopList
        '''
        
        return EmailService._send_email(email, subject, message, html_message)
    
    @staticmethod
    def _send_email(email, subject, message, html_message=None):
        """Внутренний метод для отправки email"""
        try:
            msg = EmailMultiAlternatives(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [email]
            )
            
            if html_message:
                msg.attach_alternative(html_message, "text/html")
            
            msg.send()
            logger.info(f'Email отправлен на {email}: {subject}')
            return True
        except Exception as e:
            logger.error(f'Ошибка отправки email на {email}: {e}')
            return False


