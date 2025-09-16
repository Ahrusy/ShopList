from django.urls import path
from django.http import HttpResponse
from django.shortcuts import render

def favorite_list_view(request):
    """Простая страница избранного"""
    return render(request, 'favorites/favorite_list.html', {
        'favorites': [],
        'category_filters': [{'value': 'all', 'label': 'Все категории'}],
    })

app_name = 'favorites'

urlpatterns = [
    path('', favorite_list_view, name='favorite_list'),
]
