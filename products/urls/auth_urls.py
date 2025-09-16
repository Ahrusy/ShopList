from django.urls import path
from django.shortcuts import render
from ..views.auth_views import (
    register_view, 
    login_view, 
    logout_view, 
    send_sms_code
)

app_name = 'auth'

def test_auth_view(request):
    return render(request, 'auth/test_auth.html')

urlpatterns = [
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('test/', test_auth_view, name='test'),
    path('api/send-sms/', send_sms_code, name='send_sms'),
]
