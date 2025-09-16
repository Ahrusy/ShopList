from django.urls import path
from ..views.favorite_views import (
    favorite_list, 
    add_to_favorites, 
    remove_from_favorites, 
    toggle_favorite,
    add_multiple_to_cart
)

app_name = 'favorites'

urlpatterns = [
    path('', favorite_list, name='favorite_list'),
    path('add/', add_to_favorites, name='add_to_favorites'),
    path('<int:favorite_id>/remove/', remove_from_favorites, name='remove_from_favorites'),
    path('toggle/', toggle_favorite, name='toggle_favorite'),
    path('add-to-cart/', add_multiple_to_cart, name='add_multiple_to_cart'),
]
