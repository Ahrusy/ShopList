from django import template
from ..models import Category

register = template.Library()

@register.inclusion_tag('products/tags/category_tree.html')
def show_category_tree():
    root_categories = Category.objects.filter(parent__isnull=True).prefetch_related('children')
    return {'root_categories': root_categories}