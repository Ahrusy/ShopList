from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth import get_user_model
from .models import UserLocation, Location

User = get_user_model()


class LocationMiddleware(MiddlewareMixin):
    """
    Middleware для обработки локации пользователя в сессии
    """
    
    def process_request(self, request):
        # Получаем локацию из сессии или устанавливаем по умолчанию
        if not hasattr(request, 'user_location'):
            request.user_location = self.get_user_location(request)
    
    def process_response(self, request, response):
        return response
    
    def get_user_location(self, request):
        """
        Получает локацию пользователя из базы данных или сессии
        """
        # Если пользователь аутентифицирован, получаем локацию из базы данных
        if hasattr(request, 'user') and request.user.is_authenticated:
            try:
                user_location = UserLocation.objects.filter(user=request.user).first()
                if user_location:
                    return user_location.location
            except Exception:
                pass
        
        # Если пользователь не аутентифицирован, используем сессию
        location_id = request.session.get('user_location_id')
        if location_id:
            try:
                return Location.objects.get(id=location_id, is_active=True)
            except Location.DoesNotExist:
                pass
        
        # Возвращаем локацию по умолчанию (Москва)
        try:
            return Location.objects.filter(
                name__icontains='Москва',
                is_active=True
            ).first() or Location.objects.filter(is_active=True).first()
        except Exception:
            return None
    
    def set_user_location(self, request, location):
        """
        Устанавливает локацию пользователя в сессию или базу данных
        """
        if hasattr(request, 'user') and request.user.is_authenticated:
            # Для аутентифицированных пользователей сохраняем в базу данных
            try:
                UserLocation.objects.filter(user=request.user).delete()
                UserLocation.objects.create(
                    user=request.user,
                    location=location,
                    is_auto_detected=False
                )
            except Exception:
                pass
        else:
            # Для неаутентифицированных пользователей сохраняем в сессию
            request.session['user_location_id'] = location.id





