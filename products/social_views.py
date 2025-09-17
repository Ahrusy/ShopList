from django.shortcuts import redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import requests
import json


@require_http_methods(["GET"])
def social_login_redirect(request, provider):
    """
    Перенаправляет пользователя на страницу авторизации социальной сети
    """
    if provider == 'google':
        # Google OAuth URL - используем демо Client ID для тестирования
        client_id = "123456789012-abcdefghijklmnopqrstuvwxyz123456.apps.googleusercontent.com"
        redirect_uri = request.build_absolute_uri('/accounts/social/google/callback/')
        scope = "openid email profile"
        state = "demo_state_google"
        
        auth_url = (
            f"https://accounts.google.com/o/oauth2/v2/auth?"
            f"client_id={client_id}&"
            f"redirect_uri={redirect_uri}&"
            f"scope={scope}&"
            f"response_type=code&"
            f"state={state}"
        )
        
    elif provider == 'vk':
        # VK OAuth URL - используем демо Client ID для тестирования
        client_id = "12345678"
        redirect_uri = request.build_absolute_uri('/accounts/social/vk/callback/')
        scope = "email"
        state = "demo_state_vk"
        
        auth_url = (
            f"https://oauth.vk.com/authorize?"
            f"client_id={client_id}&"
            f"redirect_uri={redirect_uri}&"
            f"scope={scope}&"
            f"response_type=code&"
            f"state={state}&"
            f"v=5.131"
        )
        
    elif provider == 'yandex':
        # Yandex OAuth URL - используем демо Client ID для тестирования
        client_id = "1234567890abcdef1234567890abcdef"
        redirect_uri = request.build_absolute_uri('/accounts/social/yandex/callback/')
        scope = "login:email login:info"
        state = "demo_state_yandex"
        
        auth_url = (
            f"https://oauth.yandex.ru/authorize?"
            f"response_type=code&"
            f"client_id={client_id}&"
            f"redirect_uri={redirect_uri}&"
            f"scope={scope}&"
            f"state={state}"
        )
    else:
        messages.error(request, 'Неподдерживаемый провайдер социальной сети')
        return redirect('auth:login')
    
    return redirect(auth_url)


@require_http_methods(["GET"])
def social_login_callback(request, provider):
    """
    Обрабатывает callback от социальной сети
    """
    code = request.GET.get('code')
    state = request.GET.get('state')
    error = request.GET.get('error')
    
    if error:
        messages.error(request, f'Ошибка авторизации: {error}')
        return redirect('auth:login')
    
    if not code:
        messages.error(request, 'Код авторизации не получен')
        return redirect('auth:login')
    
    # Здесь должна быть логика обмена кода на токен и получения данных пользователя
    # Для демонстрации просто показываем сообщение
    
    messages.info(request, f'Авторизация через {provider} будет реализована после настройки OAuth приложений')
    return redirect('login')


@csrf_exempt
@require_http_methods(["POST"])
def social_login_demo(request, provider):
    """
    Демо-функция для показа уведомления о том, что функция в разработке
    """
    return JsonResponse({
        'success': False,
        'message': f'Вход через {provider} будет доступен после настройки OAuth приложений',
        'status': 'coming_soon'
    })
