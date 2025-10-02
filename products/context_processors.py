from .client_auth import get_current_client

def client(request):
    return {'client': getattr(request, 'client', None) or get_current_client(request)}

from .models import Category


def catalog_categories(request):
    """Контекстный процессор для передачи категорий каталога во все шаблоны"""
    return {
        'catalog_categories': Category.objects.filter(
            parent__isnull=True, 
            is_active=True, 
            show_in_megamenu=True
        ).prefetch_related(
            'children__children'
        ).order_by('sort_order', 'slug')
    }

