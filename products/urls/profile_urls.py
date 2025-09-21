from django.urls import path
from ..profile_views import (
    profile_dashboard,
    profile_edit,
    profile_orders,
    profile_favorites,
    profile_settings
)

app_name = 'profile'

urlpatterns = [
    path('', profile_dashboard, name='dashboard'),
    path('edit/', profile_edit, name='edit'),
    path('orders/', profile_orders, name='orders'),
    path('favorites/', profile_favorites, name='favorites'),
    path('settings/', profile_settings, name='settings'),
]
