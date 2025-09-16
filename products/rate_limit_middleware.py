from django.http import JsonResponse
from django_ratelimit.exceptions import Ratelimited
from django.utils.translation import gettext_lazy as _


class RateLimitMiddleware:
    """Middleware для обработки ошибок rate limiting"""
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        if isinstance(exception, Ratelimited):
            if request.path.startswith('/api/'):
                return JsonResponse({
                    'error': _('Превышен лимит запросов. Попробуйте позже.'),
                    'retry_after': getattr(exception, 'retry_after', 60)
                }, status=429)
            else:
                from django.shortcuts import render
                return render(request, 'rate_limit.html', {
                    'retry_after': getattr(exception, 'retry_after', 60)
                }, status=429)
        return None
