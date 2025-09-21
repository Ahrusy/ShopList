from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.utils.crypto import get_random_string
from django.core.cache import cache
from django.core.mail import send_mail
from django.conf import settings
import json
import re
import random
from .models import User
import logging

logger = logging.getLogger(__name__)


class AuthMixin:
    """Миксин для общих методов аутентификации"""
    
    def validate_phone(self, phone):
        """Валидация номера телефона"""
        # Убираем все нецифровые символы
        phone_digits = re.sub(r'\D', '', phone)
        
        # Проверяем формат российского номера
        if phone_digits.startswith('7') and len(phone_digits) == 11:
            return '+7' + phone_digits[1:]
        elif phone_digits.startswith('8') and len(phone_digits) == 11:
            return '+7' + phone_digits[1:]
        elif len(phone_digits) == 10:
            return '+7' + phone_digits
        else:
            raise ValidationError('Неверный формат номера телефона')
    
    def generate_sms_code(self):
        """Генерация SMS кода"""
        return str(random.randint(100000, 999999))
    
    def generate_email_code(self):
        """Генерация кода подтверждения для email"""
        return str(random.randint(100000, 999999))
    
    def send_sms_code(self, phone, code):
        """Отправка SMS кода (заглушка)"""
        # В реальном проекте здесь будет интеграция с SMS-сервисом
        logger.info(f'SMS код {code} отправлен на номер {phone}')
        return True
    
    def send_email_verification(self, email, code):
        """Отправка кода подтверждения на email"""
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
                    <h2>Добро пожаловать в ShopList!</h2>
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
        Добро пожаловать в ShopList!
        
        Ваш код подтверждения: {code}
        
        Введите этот код для завершения регистрации.
        Код действителен в течение 10 минут.
        
        Если вы не регистрировались на нашем сайте, проигнорируйте это письмо.
        
        С уважением,
        Команда ShopList
        '''
        
        try:
            from django.core.mail import EmailMultiAlternatives
            
            msg = EmailMultiAlternatives(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [email]
            )
            msg.attach_alternative(html_message, "text/html")
            msg.send()
            
            return True
        except Exception as e:
            logger.error(f'Ошибка отправки email: {e}')
            return False
    
    def send_system_email(self, email, subject, message, html_message=None):
        """Отправка системного письма"""
        try:
            from django.core.mail import EmailMultiAlternatives
            
            msg = EmailMultiAlternatives(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [email]
            )
            
            if html_message:
                msg.attach_alternative(html_message, "text/html")
            
            msg.send()
            return True
        except Exception as e:
            logger.error(f'Ошибка отправки системного email: {e}')
            return False


def register_view(request):
    """Страница регистрации"""
    if request.user.is_authenticated:
        return redirect('index')
    
    if request.method == 'POST':
        return handle_registration(request)
    
    return render(request, 'auth/register.html', {'form': None})


@csrf_exempt
def handle_registration(request):
    """Обработка регистрации"""
    mixin = AuthMixin()
    
    try:
        data = json.loads(request.body) if request.content_type == 'application/json' else request.POST
        method = data.get('registration_method', 'phone')
        
        if method == 'phone':
            return register_by_phone(request, data, mixin)
        elif method == 'email':
            return register_by_email(request, data, mixin)
        else:
            return JsonResponse({'success': False, 'message': 'Неверный метод регистрации'}, status=400)
            
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Неверный формат данных'}, status=400)
    except Exception as e:
        logger.error(f'Ошибка регистрации: {e}')
        return JsonResponse({'success': False, 'message': 'Ошибка сервера'}, status=500)


def register_by_phone(request, data, mixin):
    """Регистрация по телефону"""
    phone = data.get('phone')
    sms_code = data.get('sms_code')
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    
    if not all([phone, sms_code, first_name, last_name]):
        return JsonResponse({'success': False, 'message': 'Заполните все поля'}, status=400)
    
    try:
        # Валидируем телефон
        formatted_phone = mixin.validate_phone(phone)
        
        # Проверяем SMS код
        cached_code = cache.get(f'sms_code_{formatted_phone}')
        if not cached_code or cached_code != sms_code:
            return JsonResponse({'success': False, 'message': 'Неверный код подтверждения'}, status=400)
        
        # Проверяем, не зарегистрирован ли уже пользователь
        if User.objects.filter(phone=formatted_phone).exists():
            return JsonResponse({'success': False, 'message': 'Пользователь с таким номером уже зарегистрирован'}, status=400)
        
        # Создаем пользователя
        username = f'user_{get_random_string(8)}'
        user = User.objects.create_user(
            username=username,
            first_name=first_name,
            last_name=last_name,
            phone=formatted_phone,
            is_active=True
        )
        
        # Удаляем использованный код
        cache.delete(f'sms_code_{formatted_phone}')
        
        # Авторизуем пользователя
        login(request, user)
        
        return JsonResponse({'success': True, 'message': 'Регистрация успешна', 'redirect': '/'})
        
    except ValidationError as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)
    except Exception as e:
        logger.error(f'Ошибка регистрации по телефону: {e}')
        return JsonResponse({'success': False, 'message': 'Ошибка сервера'}, status=500)


def register_by_email(request, data, mixin):
    """Регистрация по email с подтверждением кода"""
    email = data.get('email')
    email_code = data.get('email_code')
    
    if not all([email, email_code]):
        return JsonResponse({'success': False, 'message': 'Введите email и код подтверждения'}, status=400)
    
    try:
        # Получаем данные регистрации из кэша
        registration_data = cache.get(f'email_registration_{email}')
        if not registration_data:
            return JsonResponse({'success': False, 'message': 'Время действия кода истекло. Запросите новый код'}, status=400)
        
        # Проверяем код подтверждения
        if registration_data['code'] != email_code:
            return JsonResponse({'success': False, 'message': 'Неверный код подтверждения'}, status=400)
        
        # Проверяем, не зарегистрирован ли уже пользователь (дополнительная проверка)
        if User.objects.filter(email=email).exists():
            return JsonResponse({'success': False, 'message': 'Пользователь с данным email уже существует'}, status=400)
        
        if User.objects.filter(phone=registration_data['phone']).exists():
            return JsonResponse({'success': False, 'message': 'Пользователь с данным номером телефона уже существует'}, status=400)
        
        # Создаем пользователя
        username = f'user_{get_random_string(8)}'
        user = User.objects.create_user(
            username=username,
            email=email,
            password=registration_data['password'],
            first_name=registration_data['first_name'],
            last_name=registration_data['last_name'],
            phone=registration_data['phone'],
            is_active=True
        )
        
        # Добавляем отчество, если указано
        if registration_data.get('middle_name'):
            user.middle_name = registration_data['middle_name']
            user.save()
        
        # Удаляем данные регистрации из кэша
        cache.delete(f'email_registration_{email}')
        
        # Авторизуем пользователя
        login(request, user)
        
        return JsonResponse({'success': True, 'message': 'Регистрация успешна', 'redirect': '/'})
        
    except Exception as e:
        logger.error(f'Ошибка регистрации по email: {e}')
        return JsonResponse({'success': False, 'message': 'Ошибка сервера'}, status=500)


def login_view(request):
    """Страница входа"""
    if request.user.is_authenticated:
        return redirect('index')
    
    if request.method == 'POST':
        return handle_login(request)
    
    return render(request, 'auth/login.html', {'form': None})


def handle_login(request):
    """Обработка входа"""
    mixin = AuthMixin()
    
    try:
        data = json.loads(request.body) if request.content_type == 'application/json' else request.POST
        method = data.get('login_method', 'phone')
        
        if method == 'phone':
            return login_by_phone(request, data, mixin)
        elif method == 'email':
            return login_by_email(request, data, mixin)
        else:
            return JsonResponse({'success': False, 'message': 'Неверный метод входа'}, status=400)
            
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Неверный формат данных'}, status=400)
    except Exception as e:
        logger.error(f'Ошибка входа: {e}')
        return JsonResponse({'success': False, 'message': 'Ошибка сервера'}, status=500)


def login_by_phone(request, data, mixin):
    """Вход по телефону"""
    phone = data.get('phone')
    sms_code = data.get('sms_code')
    
    if not all([phone, sms_code]):
        return JsonResponse({'success': False, 'message': 'Заполните все поля'}, status=400)
    
    try:
        # Валидируем телефон
        formatted_phone = mixin.validate_phone(phone)
        
        # Проверяем SMS код
        cached_code = cache.get(f'sms_code_{formatted_phone}')
        if not cached_code or cached_code != sms_code:
            return JsonResponse({'success': False, 'message': 'Неверный код подтверждения'}, status=400)
        
        # Ищем пользователя
        try:
            user = User.objects.get(phone=formatted_phone)
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Пользователь не найден'}, status=400)
        
        # Удаляем использованный код
        cache.delete(f'sms_code_{formatted_phone}')
        
        # Авторизуем пользователя
        login(request, user)
        
        return JsonResponse({'success': True, 'message': 'Вход выполнен', 'redirect': '/'})
        
    except ValidationError as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)
    except Exception as e:
        logger.error(f'Ошибка входа по телефону: {e}')
        return JsonResponse({'success': False, 'message': 'Ошибка сервера'}, status=500)


def login_by_email(request, data, mixin):
    """Вход по email"""
    email = data.get('email')
    password = data.get('password')
    remember_me = data.get('remember_me', False)
    
    if not all([email, password]):
        return JsonResponse({'success': False, 'message': 'Заполните все поля'}, status=400)
    
    try:
        # Аутентифицируем пользователя
        user = authenticate(request, username=email, password=password)
        
        if user is None:
            return JsonResponse({'success': False, 'message': 'Неверный email или пароль'}, status=400)
        
        # Авторизуем пользователя
        login(request, user)
        
        # Настройка сессии
        if not remember_me:
            request.session.set_expiry(0)  # Сессия истекает при закрытии браузера
        
        return JsonResponse({'success': True, 'message': 'Вход выполнен', 'redirect': '/'})
        
    except Exception as e:
        logger.error(f'Ошибка входа по email: {e}')
        return JsonResponse({'success': False, 'message': 'Ошибка сервера'}, status=500)


@require_http_methods(["POST"])
def send_sms_code(request):
    """Отправка SMS кода"""
    mixin = AuthMixin()
    
    try:
        data = json.loads(request.body)
        phone = data.get('phone')
        
        if not phone:
            return JsonResponse({'success': False, 'message': 'Номер телефона не указан'}, status=400)
        
        # Валидируем телефон
        formatted_phone = mixin.validate_phone(phone)
        
        # Генерируем код
        code = mixin.generate_sms_code()
        
        # Сохраняем код в кэше на 5 минут
        cache.set(f'sms_code_{formatted_phone}', code, 300)
        
        # Отправляем SMS
        if mixin.send_sms_code(formatted_phone, code):
            return JsonResponse({'success': True, 'message': 'SMS отправлен'})
        else:
            return JsonResponse({'success': False, 'message': 'Ошибка отправки SMS'}, status=500)
        
    except ValidationError as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Неверный формат данных'}, status=400)
    except Exception as e:
        logger.error(f'Ошибка отправки SMS: {e}')
        return JsonResponse({'success': False, 'message': 'Ошибка сервера'}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def send_email_code(request):
    """Отправка кода подтверждения на email"""
    mixin = AuthMixin()
    
    try:
        data = json.loads(request.body)
        email = data.get('email')
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        middle_name = data.get('middle_name', '')
        phone = data.get('phone')
        password = data.get('password')
        password_confirm = data.get('password_confirm')
        
        if not all([email, first_name, last_name, phone, password, password_confirm]):
            return JsonResponse({'success': False, 'message': 'Заполните все обязательные поля'}, status=400)
        
        if password != password_confirm:
            return JsonResponse({'success': False, 'message': 'Пароли не совпадают'}, status=400)
        
        if len(password) < 8:
            return JsonResponse({'success': False, 'message': 'Пароль должен содержать минимум 8 символов'}, status=400)
        
        # Проверяем, не зарегистрирован ли уже пользователь
        if User.objects.filter(email=email).exists():
            return JsonResponse({'success': False, 'message': 'Пользователь с данным email уже существует'}, status=400)
        
        # Валидируем телефон
        try:
            formatted_phone = mixin.validate_phone(phone)
        except ValidationError as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=400)
        
        # Проверяем, не зарегистрирован ли уже пользователь с таким телефоном
        if User.objects.filter(phone=formatted_phone).exists():
            return JsonResponse({'success': False, 'message': 'Пользователь с данным номером телефона уже существует'}, status=400)
        
        # Генерируем код
        code = mixin.generate_email_code()
        
        # Сохраняем данные регистрации в кэше на 10 минут
        registration_data = {
            'email': email,
            'first_name': first_name,
            'last_name': last_name,
            'middle_name': middle_name,
            'phone': formatted_phone,
            'password': password,
            'code': code
        }
        cache.set(f'email_registration_{email}', registration_data, 600)
        
        # Отправляем код на email
        from .email_utils import EmailService
        if EmailService.send_verification_code(email, code, first_name):
            return JsonResponse({'success': True, 'message': 'Код подтверждения отправлен на email'})
        else:
            return JsonResponse({'success': False, 'message': 'Ошибка отправки email'}, status=500)
        
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Неверный формат данных'}, status=400)
    except Exception as e:
        logger.error(f'Ошибка отправки email кода: {e}')
        return JsonResponse({'success': False, 'message': 'Ошибка сервера'}, status=500)


@login_required
def logout_view(request):
    """Выход из системы"""
    from django.contrib.auth import logout
    logout(request)
    return redirect('index')
