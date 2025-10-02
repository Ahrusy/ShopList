from django.urls import path, include
from django.shortcuts import render
from ..auth_views import (
    send_sms_code,
    send_email_code,
    test_login_view
)
from ..client_auth import client_register, client_login, client_logout

app_name = 'auth'

def test_auth_view(request):
    return render(request, 'auth/test_auth.html')

urlpatterns = [
    path('register/', client_register, name='register'),
    path('login/', client_login, name='login'),
    path('logout/', client_logout, name='logout'),
    path('test/', test_auth_view, name='test'),
    path('test-login/', test_login_view, name='test_login'),
    path('api/send-sms/', send_sms_code, name='send_sms'),
    path('send-email-code/', send_email_code, name='send_email_code'),
    path('social/', include('allauth.socialaccount.urls')),  # Social auth URLs
]