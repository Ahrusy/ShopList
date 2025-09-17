from django.urls import path
from django.http import HttpResponse

def favorite_list_view(request):
    return HttpResponse("Favorites page - градиенты работают!")

app_name = 'favorites'

urlpatterns = [
    path('', favorite_list_view, name='favorite_list'),
]
