from rest_framework import permissions
from django.shortcuts import get_object_or_404
from ..models import Product, Shop

class IsManagerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow managers or admins to create/update/delete objects.
    """
    def has_permission(self, request, view):
        if request.user and request.user.is_authenticated:
            return request.user.role in ['manager', 'admin']
        return False

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the snippet.
        if request.user.role == 'admin':
            return True
        elif request.user.role == 'manager':
            if isinstance(obj, Product):
                # Менеджер может редактировать только товары, связанные с его магазинами
                return obj.shops.filter(managers=request.user).exists()
            elif isinstance(obj, Shop):
                # Менеджер может редактировать только свои магазины
                return obj.managers.filter(pk=request.user.pk).exists()
            # Добавьте другие проверки для других моделей, если необходимо
            return False
        return False

class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object or admins to edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner or admin.
        if request.user.is_staff or request.user.is_superuser: # Admin
            return True
        
        # Assuming the object has an 'owner' or 'user' field
        return obj.user == request.user