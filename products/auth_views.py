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
    
    def send_sms_code(self, phone, code):
        """Отправка SMS кода (заглушка)"""
        # В реальном проекте здесь будет интеграция с SMS-сервисом
        logger.info(f'SMS код {code} отправлен на номер {phone}')
        return True
    
    def send_email_verification(self, email, code):
        """Отправка кода подтверждения на email"""
        subject = 'Подтверждение регистрации - ShopList'
        message = f'''
        Добро пожаловать в ShopList!
        
        Ваш код подтверждения: {code}
        
        Введите этот код для завершения регистрации.
        
        Если вы не регистрировались на нашем сайте, проигнорируйте это письмо.
        '''
        
        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            return True
        except Exception as e:
            logger.error(f'Ошибка отправки email: {e}')
            return False


def register_view(request):
    """Страница регистрации"""
    if request.user.is_authenticated:
        return redirect('index')
    
    if request.method == 'POST':
        return handle_registration(request)
    
    return render(request, 'auth/register.html')


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
    """Регистрация по email"""
    email = data.get('email')
    password = data.get('password')
    password_confirm = data.get('password_confirm')
    first_name = data.get('first_name_email')
    last_name = data.get('last_name_email')
    
    if not all([email, password, password_confirm, first_name, last_name]):
        return JsonResponse({'success': False, 'message': 'Заполните все поля'}, status=400)
    
    if password != password_confirm:
        return JsonResponse({'success': False, 'message': 'Пароли не совпадают'}, status=400)
    
    if len(password) < 8:
        return JsonResponse({'success': False, 'message': 'Пароль должен содержать минимум 8 символов'}, status=400)
    
    try:
        # Проверяем, не зарегистрирован ли уже пользователь
        if User.objects.filter(email=email).exists():
            return JsonResponse({'success': False, 'message': 'Пользователь с таким email уже зарегистрирован'}, status=400)
        
        # Создаем пользователя
        username = f'user_{get_random_string(8)}'
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            is_active=True
        )
        
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
    
    return render(request, 'auth/login.html')


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


@login_required
def logout_view(request):
    """Выход из системы"""
    from django.contrib.auth import logout
    logout(request)
    return redirect('index')
