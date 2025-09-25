from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.backends import ModelBackend
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
        logger.info(f"=== REGISTRATION ATTEMPT ===")
        logger.info(f"Request method: {request.method}")
        logger.info(f"Request content type: {request.content_type}")
        logger.info(f"Request POST data: {dict(request.POST)}")
        logger.info(f"Request body: {request.body.decode('utf-8') if request.body else 'No body'}")
        
        # Handle both form data and JSON data
        if request.content_type == 'application/json':
            try:
                data = json.loads(request.body)
                logger.info(f"Parsed JSON data: {data}")
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error: {e}")
                return JsonResponse({'success': False, 'message': 'Неверный формат данных'}, status=400)
        else:
            data = request.POST
            logger.info(f"Form data: {dict(data)}")
        
        method = data.get('registration_method', 'phone')
        logger.info(f"Registration method: {method}")
        
        if method == 'phone':
            return register_by_phone(request, data, mixin)
        elif method == 'email':
            return register_by_email(request, data, mixin)
        else:
            logger.info(f"Invalid registration method: {method}")
            return JsonResponse({'success': False, 'message': 'Неверный метод регистрации'}, status=400)
            
    except Exception as e:
        logger.error(f'Ошибка регистрации: {e}', exc_info=True)
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
        
        # Авторизуем пользователя с указанием бэкенда
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        
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
        
        # Проверяем, не зарегистрирован ли уже пользователь
        # If user exists but this is a retry after failed registration, we allow it
        # Only check phone number to prevent duplicate accounts
        # Проверяем, не зарегистрирован ли уже пользователь с таким телефоном
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
        
        # Авторизуем пользователя с указанием бэкенда
        from django.contrib.auth import login
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        
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
        logger.info(f"=== LOGIN ATTEMPT ===")
        logger.info(f"Request method: {request.method}")
        logger.info(f"Request content type: {request.content_type}")
        logger.info(f"Request POST data: {dict(request.POST)}")
        logger.info(f"Request body: {request.body.decode('utf-8') if request.body else 'No body'}")
        logger.info(f"CSRF cookie: {request.COOKIES.get('csrftoken')}")
        logger.info(f"CSRF token in POST: {request.POST.get('csrfmiddlewaretoken')}")
        
        # Check if this is an AJAX request
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        logger.info(f"Is AJAX request: {is_ajax}")
        
        # Handle both form data and JSON data
        if request.content_type == 'application/json':
            logger.info("Processing JSON data")
            try:
                data = json.loads(request.body)
                method = data.get('login_method', 'phone')
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error: {e}")
                return JsonResponse({'success': False, 'message': 'Неверный формат данных'}, status=400)
        else:
            # Handle regular form data
            logger.info("Processing form data")
            data = request.POST
            method = data.get('login_method', 'phone')
            # If login_method is not in POST data, default to 'phone'
            if not method:
                method = 'phone'
                logger.info("Login method not found in POST data, defaulting to 'phone'")
        
        # Log the method and data for debugging
        logger.info(f"Login method: {method}, Data: {dict(data)}")
        
        if method == 'phone':
            logger.info("Calling login_by_phone")
            return login_by_phone(request, data, mixin)
        elif method == 'email':
            logger.info("Calling login_by_email")
            return login_by_email(request, data, mixin)
        else:
            logger.info(f"Invalid login method: {method}")
            return JsonResponse({'success': False, 'message': 'Неверный метод входа'}, status=400)
            
    except Exception as e:
        logger.error(f'Ошибка входа: {e}', exc_info=True)
        return JsonResponse({'success': False, 'message': 'Ошибка сервера'}, status=500)


@csrf_exempt
def test_login_view(request):
    """Тестовое представление для отладки входа"""
    if request.method == 'POST':
        logger.info("Test login view POST request received")
        logger.info(f"POST data: {request.POST}")
        logger.info(f"Content type: {request.content_type}")
        logger.info(f"CSRF cookie: {request.COOKIES.get('csrftoken')}")
        logger.info(f"CSRF token in POST: {request.POST.get('csrfmiddlewaretoken')}")
        
        # Try to authenticate
        from django.contrib.auth import authenticate
        email = request.POST.get('email')
        password = request.POST.get('password')
        if email and password:
            user = authenticate(request, username=email, password=password)
            logger.info(f"Test authentication result: {user}")
        
        return JsonResponse({'status': 'success', 'message': 'Test login view working', 'data': dict(request.POST)})
    return render(request, 'auth/test_login.html')


def login_by_phone(request, data, mixin):
    """Вход по телефону"""
    logger.info(f"Login by phone data: {data}")
    
    phone = data.get('phone')
    sms_code = data.get('sms_code')
    
    # For phone login, we need phone and SMS code
    if not phone:
        logger.info("Phone missing for phone login")
        # For regular form submissions, return error message
        if request.content_type != 'application/json':
            messages.error(request, 'Введите номер телефона')
            return render(request, 'auth/login.html')
        return JsonResponse({'success': False, 'message': 'Введите номер телефона'}, status=400)
    
    if not sms_code:
        logger.info("SMS code missing for phone login")
        # For regular form submissions, return error message
        if request.content_type != 'application/json':
            messages.error(request, 'Введите код из СМС')
            return render(request, 'auth/login.html')
        return JsonResponse({'success': False, 'message': 'Введите код из СМС'}, status=400)
    
    try:
        # Валидируем телефон
        formatted_phone = mixin.validate_phone(phone)
        logger.info(f"Formatted phone: {formatted_phone}")
        
        # Проверяем SMS код
        cached_code = cache.get(f'sms_code_{formatted_phone}')
        logger.info(f"Cached SMS code: {cached_code}")
        logger.info(f"Provided SMS code: {sms_code}")
        
        if not cached_code or cached_code != sms_code:
            logger.info("Invalid SMS code for phone login")
            # For regular form submissions, return error message
            if request.content_type != 'application/json':
                messages.error(request, 'Неверный код подтверждения')
                return render(request, 'auth/login.html')
            return JsonResponse({'success': False, 'message': 'Неверный код подтверждения'}, status=400)
        
        # Ищем пользователя
        try:
            from .models import User
            from django.contrib.auth import login
            user = User.objects.get(phone=formatted_phone)
            logger.info(f"User found: {user}")
        except User.DoesNotExist:
            logger.info("User not found for phone login")
            # For regular form submissions, return error message
            if request.content_type != 'application/json':
                messages.error(request, 'Пользователь не найден')
                return render(request, 'auth/login.html')
            return JsonResponse({'success': False, 'message': 'Пользователь не найден'}, status=400)
        
        # Удаляем использованный код
        cache.delete(f'sms_code_{formatted_phone}')
        logger.info("SMS code deleted from cache")
        
        # Авторизуем пользователя
        logger.info(f"Logging in user: {user}")
        login(request, user)
        logger.info(f"User logged in successfully: {user}")
        
        # For regular form submissions, redirect instead of JSON response
        if request.content_type != 'application/json':
            logger.info("Redirecting to index after successful phone login")
            return redirect('index')
        
        logger.info("Returning JSON response after successful phone login")
        return JsonResponse({'success': True, 'message': 'Вход выполнен', 'redirect': '/'})
        
    except ValidationError as e:
        logger.info(f"Phone validation error: {e}")
        # For regular form submissions, return error message
        if request.content_type != 'application/json':
            messages.error(request, str(e))
            return render(request, 'auth/login.html')
        return JsonResponse({'success': False, 'message': str(e)}, status=400)
    except Exception as e:
        logger.error(f'Ошибка входа по телефону: {e}', exc_info=True)
        # For regular form submissions, return error message
        if request.content_type != 'application/json':
            messages.error(request, 'Ошибка сервера')
            return render(request, 'auth/login.html')
        return JsonResponse({'success': False, 'message': 'Ошибка сервера'}, status=500)


def login_by_email(request, data, mixin):
    """Вход по email"""
    logger.info(f"=== EMAIL LOGIN ATTEMPT ===")
    logger.info(f"Login by email data: {dict(data)}")
    
    email = data.get('email')
    password = data.get('password')
    remember_me = data.get('remember_me', False)
    
    logger.info(f"Email: {email}")
    logger.info(f"Password provided: {'Yes' if password else 'No'}")
    logger.info(f"Remember me: {remember_me}")
    
    # For email login, we only need email and password
    if not email or not password:
        logger.info("Email or password missing for email login")
        # For regular form submissions, return error message
        if request.content_type != 'application/json':
            messages.error(request, 'Заполните все поля')
            return render(request, 'auth/login.html')
        return JsonResponse({'success': False, 'message': 'Заполните все поля'}, status=400)
    
    try:
        # Аутентифицируем пользователя
        logger.info(f"Attempting to authenticate user with email: {email}")
        
        # Use the default authentication backend
        from django.contrib.auth import authenticate, login
        user = authenticate(request, username=email, password=password)
        logger.info(f"Authentication result: {user}")
        
        if user is None:
            # Let's check if the user exists
            from .models import User
            try:
                user_obj = User.objects.get(email=email)
                logger.info(f"User found in database: {user_obj}")
                logger.info(f"User is_active: {user_obj.is_active}")
                logger.info(f"User password hash: {user_obj.password}")
            except User.DoesNotExist:
                logger.info(f"No user found with email: {email}")
            except Exception as e:
                logger.error(f"Error checking user existence: {e}")
            
            logger.info("Authentication failed for email login")
            # For regular form submissions, return error message
            if request.content_type != 'application/json':
                messages.error(request, 'Неверный email или пароль')
                return render(request, 'auth/login.html')
            return JsonResponse({'success': False, 'message': 'Неверный email или пароль'}, status=400)
        
        # Авторизуем пользователя
        logger.info(f"Logging in user: {user}")
        login(request, user)
        logger.info(f"User logged in successfully: {user}")
        
        # Настройка сессии
        if not remember_me:
            request.session.set_expiry(0)  # Сессия истекает при закрытии браузера
        
        # For regular form submissions, redirect instead of JSON response
        if request.content_type != 'application/json':
            logger.info("Redirecting to index after successful email login")
            return redirect('index')
        
        logger.info("Returning JSON response after successful email login")
        return JsonResponse({'success': True, 'message': 'Вход выполнен', 'redirect': '/'})
        
    except Exception as e:
        logger.error(f'Ошибка входа по email: {e}', exc_info=True)
        # For regular form submissions, return error message
        if request.content_type != 'application/json':
            messages.error(request, 'Ошибка сервера')
            return render(request, 'auth/login.html')
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
        logger.info(f"=== SEND EMAIL CODE ATTEMPT ===")
        logger.info(f"Request content type: {request.content_type}")
        logger.info(f"Request body: {request.body.decode('utf-8') if request.body else 'No body'}")
        
        data = json.loads(request.body)
        logger.info(f"Parsed JSON data: {data}")
        
        email = data.get('email')
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        middle_name = data.get('middle_name', '')
        phone = data.get('phone')
        password = data.get('password')
        password_confirm = data.get('password_confirm')
        
        logger.info(f"Email: {email}, First name: {first_name}, Last name: {last_name}, Phone: {phone}")
        
        if not all([email, first_name, last_name, phone, password, password_confirm]):
            logger.info("Missing required fields")
            return JsonResponse({'success': False, 'message': 'Заполните все обязательные поля'}, status=400)
        
        if password != password_confirm:
            logger.info("Passwords don't match")
            return JsonResponse({'success': False, 'message': 'Пароли не совпадают'}, status=400)
        
        if len(password) < 8:
            logger.info("Password too short")
            return JsonResponse({'success': False, 'message': 'Пароль должен содержать минимум 8 символов'}, status=400)
        
        # Проверяем, не зарегистрирован ли уже пользователь с таким email
        if User.objects.filter(email=email).exists():
            logger.info(f"User already exists with email: {email}")
            return JsonResponse({'success': False, 'message': 'Пользователь с таким email уже существует'}, status=400)
        
        # Валидируем телефон
        try:
            formatted_phone = mixin.validate_phone(phone)
            logger.info(f"Formatted phone: {formatted_phone}")
        except ValidationError as e:
            logger.info(f"Phone validation error: {e}")
            return JsonResponse({'success': False, 'message': str(e)}, status=400)
        
        # Проверяем, не зарегистрирован ли уже пользователь с таким телефоном
        if User.objects.filter(phone=formatted_phone).exists():
            logger.info(f"User already exists with phone: {formatted_phone}")
            return JsonResponse({'success': False, 'message': 'Пользователь с таким номером телефона уже существует'}, status=400)
        
        # Генерируем код
        code = mixin.generate_email_code()
        logger.info(f"Generated code: {code}")
        
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
        logger.info(f"Registration data saved to cache for email: {email}")
        
        # Отправляем код на email
        if mixin.send_email_verification(email, code):
            logger.info(f"Verification code sent to email: {email}")
            return JsonResponse({'success': True, 'message': 'Код подтверждения отправлен на email'})
        else:
            logger.error(f"Failed to send verification code to email: {email}")
            return JsonResponse({'success': False, 'message': 'Ошибка отправки email'}, status=500)
        
    except json.JSONDecodeError:
        logger.error("JSON decode error in send_email_code")
        return JsonResponse({'success': False, 'message': 'Неверный формат данных'}, status=400)
    except Exception as e:
        logger.error(f'Ошибка отправки email кода: {e}', exc_info=True)
        return JsonResponse({'success': False, 'message': 'Ошибка сервера'}, status=500)


@login_required
def logout_view(request):
    """Выход из системы"""
    from django.contrib.auth import logout
    logout(request)
    return redirect('index')
