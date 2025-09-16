from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.utils.translation import gettext_lazy as _
from django.core.paginator import Paginator
from .models import Notification
import json

@login_required
def notification_list(request):
    """Список уведомлений пользователя"""
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    
    # Пагинация
    paginator = Paginator(notifications, 20)
    page_number = request.GET.get('page')
    notifications = paginator.get_page(page_number)
    
    context = {
        'notifications': notifications,
    }
    return render(request, 'notifications/notification_list.html', context)

@login_required
def notification_detail(request, notification_id):
    """Детальная страница уведомления"""
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    
    # Отмечаем как прочитанное
    if not notification.is_read:
        notification.is_read = True
        notification.save()
    
    context = {
        'notification': notification,
    }
    return render(request, 'notifications/notification_detail.html', context)

@login_required
@require_POST
@csrf_exempt
def mark_as_read(request, notification_id):
    """Отметить уведомление как прочитанное (AJAX)"""
    try:
        notification = get_object_or_404(Notification, id=notification_id, user=request.user)
        notification.is_read = True
        notification.save()
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

@login_required
@require_POST
@csrf_exempt
def mark_all_as_read(request):
    """Отметить все уведомления как прочитанные (AJAX)"""
    try:
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

@login_required
@require_POST
@csrf_exempt
def delete_notification(request, notification_id):
    """Удалить уведомление (AJAX)"""
    try:
        notification = get_object_or_404(Notification, id=notification_id, user=request.user)
        notification.delete()
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

@login_required
def unread_count(request):
    """Получить количество непрочитанных уведомлений (AJAX)"""
    count = Notification.objects.filter(user=request.user, is_read=False).count()
    return JsonResponse({'count': count})

@login_required
def notification_settings(request):
    """Настройки уведомлений"""
    # Здесь можно добавить настройки типов уведомлений для пользователя
    context = {
        'notification_types': Notification.NOTIFICATION_TYPES,
    }
    return render(request, 'notifications/settings.html', context)
