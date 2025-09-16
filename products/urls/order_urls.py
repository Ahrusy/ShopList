from django.urls import path
from ..views.order_views import order_list, order_detail, cancel_order, repeat_order

app_name = 'orders'

urlpatterns = [
    path('', order_list, name='order_list'),
    path('<int:order_id>/', order_detail, name='order_detail'),
    path('<int:order_id>/cancel/', cancel_order, name='cancel_order'),
    path('<int:order_id>/repeat/', repeat_order, name='repeat_order'),
]
