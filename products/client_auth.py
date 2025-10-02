from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.views.decorators.http import require_http_methods
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.hashers import make_password, check_password
from .models import ClientAccount

CLIENT_SESSION_KEY = 'client_id'


def get_current_client(request: HttpRequest):
    client_id = request.session.get(CLIENT_SESSION_KEY)
    if not client_id:
        return None
    try:
        return ClientAccount.objects.get(id=client_id, is_active=True)
    except ClientAccount.DoesNotExist:
        return None


@require_http_methods(["GET", "POST"])
def client_register(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')

        if not email or not password:
            messages.error(request, _('Введите email и пароль'))
            return render(request, 'client_auth/register.html')

        if ClientAccount.objects.filter(email=email).exists():
            messages.error(request, _('Пользователь с таким email уже существует'))
            return render(request, 'client_auth/register.html')

        client = ClientAccount.objects.create(
            email=email,
            password=make_password(password),
            first_name=first_name,
            last_name=last_name,
        )
        request.session[CLIENT_SESSION_KEY] = client.id
        messages.success(request, _('Регистрация успешна'))
        return redirect('index')

    return render(request, 'client_auth/register.html')


@require_http_methods(["GET", "POST"])
def client_login(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        if not email or not password:
            messages.error(request, _('Введите email и пароль'))
            return render(request, 'client_auth/login.html')

        try:
            client = ClientAccount.objects.get(email=email, is_active=True)
        except ClientAccount.DoesNotExist:
            messages.error(request, _('Неверный email или пароль'))
            return render(request, 'client_auth/login.html')

        if not check_password(password, client.password):
            messages.error(request, _('Неверный email или пароль'))
            return render(request, 'client_auth/login.html')

        request.session[CLIENT_SESSION_KEY] = client.id
        messages.success(request, _('Вход выполнен'))
        return redirect('index')

    return render(request, 'client_auth/login.html')


def client_logout(request: HttpRequest) -> HttpResponse:
    # Разлогиниваем стандартную сессию Django (если пользователь авторизован)
    try:
        from django.contrib.auth import logout as django_logout
        django_logout(request)
    except Exception:
        pass

    # Очищаем клиентскую сессию (кастомная авторизация)
    if CLIENT_SESSION_KEY in request.session:
        del request.session[CLIENT_SESSION_KEY]

    messages.info(request, _('Вы вышли из клиентского аккаунта'))
    return redirect('index')





