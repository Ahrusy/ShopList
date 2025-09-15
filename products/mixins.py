from django.contrib.auth.mixins import AccessMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.contrib import messages

class RoleRequiredMixin(AccessMixin):
    allowed_roles = []

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, "Для доступа к этой странице необходимо войти в систему.")
            return self.handle_no_permission()
        if not request.user.role in self.allowed_roles:
            messages.error(request, "У вас нет прав для доступа к этой странице.")
            return redirect(reverse_lazy('index')) # Перенаправляем на главную страницу, если роль не соответствует
        return super().dispatch(request, *args, **kwargs)

class SalesExecutiveRequiredMixin(RoleRequiredMixin):
    allowed_roles = ['sales_executive', 'admin']

class AdminRequiredMixin(RoleRequiredMixin):
    allowed_roles = ['admin']