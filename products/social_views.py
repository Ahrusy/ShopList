from django.shortcuts import redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import requests
import json
import os


@require_http_methods(["GET"])
def social_login_redirect(request, provider):
    """
    Перенаправляет пользователя на страницу авторизации социальной сети
    """
    if provider == 'google':
        # Use actual Google OAuth credentials if available, otherwise fallback to demo
        client_id = getattr(settings, 'SOCIAL_AUTH_GOOGLE_OAUTH2_KEY', None)
        if not client_id:
            client_id = "123456789012-abcdefghijklmnopqrstuvwxyz123456.apps.googleusercontent.com"
        
        redirect_uri = request.build_absolute_uri('/accounts/social/google/callback/')
        scope = "openid email profile https://www.googleapis.com/auth/calendar"
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
    
    # Exchange code for token
    if provider == 'google':
        client_id = getattr(settings, 'SOCIAL_AUTH_GOOGLE_OAUTH2_KEY', None)
        client_secret = getattr(settings, 'SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET', None)
        
        if not client_id or not client_secret:
            messages.info(request, 'Google OAuth не настроен. Используйте обычный вход.')
            return redirect('auth:login')
        
        redirect_uri = request.build_absolute_uri('/accounts/social/google/callback/')
        
        # Exchange code for access token
        token_url = "https://oauth2.googleapis.com/token"
        data = {
            'client_id': client_id,
            'client_secret': client_secret,
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': redirect_uri,
        }
        
        try:
            response = requests.post(token_url, data=data)
            token_data = response.json()
            
            if 'error' in token_data:
                messages.error(request, f'Ошибка получения токена: {token_data["error_description"]}')
                return redirect('auth:login')
            
            access_token = token_data.get('access_token')
            
            # Get user info
            user_info_url = "https://www.googleapis.com/oauth2/v2/userinfo"
            headers = {'Authorization': f'Bearer {access_token}'}
            user_response = requests.get(user_info_url, headers=headers)
            user_data = user_response.json()
            
            # Here you would create or update the user in your database
            # For now, we'll just show a success message
            messages.success(request, f'Успешная авторизация через Google: {user_data.get("email", "No email")}')
            
            # Save Google Calendar token for future use
            if 'refresh_token' in token_data:
                # Save refresh token to user profile for Google Calendar integration
                pass
            
            return redirect('index')
            
        except Exception as e:
            messages.error(request, f'Ошибка авторизации через Google: {str(e)}')
            return redirect('auth:login')
    
    # For other providers, show demo message
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