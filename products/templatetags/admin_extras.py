"""
Template tags and filters for admin interface
"""
from django import template

register = template.Library()


@register.filter
def lookup(dictionary, key):
    """
    Template filter to lookup a value in a dictionary by key
    Usage: {{ dict|lookup:key }}
    """
    if isinstance(dictionary, dict):
        return dictionary.get(key, [])
    return []


@register.filter
def multiply(value, arg):
    """
    Multiplies the value by the argument
    Usage: {{ value|multiply:2 }}
    """
    try:
        return int(value) * int(arg)
    except (ValueError, TypeError):
        return 0


@register.filter
def indent_level(level):
    """
    Returns HTML indentation for tree display
    Usage: {{ category.level|indent_level }}
    """
    return '&nbsp;&nbsp;&nbsp;&nbsp;' * level


@register.simple_tag
def category_icon(category):
    """
    Returns appropriate icon for category based on whether it has children
    Usage: {% category_icon category %}
    """
    if category.get_children().exists():
        return '📁'
    return '📄'


@register.inclusion_tag('admin/category_tree_node.html')
def render_category_tree(category, level=0):
    """
    Renders a category tree node
    Usage: {% render_category_tree category %}
    """
    return {
        'category': category,
        'level': level,
        'children': category.get_children(),
    }


@register.filter
def has_subcategories(category):
    """
    Checks if category has subcategories
    Usage: {% if category|has_subcategories %}
    """
    return category.get_children().exists()


@register.filter
def products_count_display(count):
    """
    Formats products count for display
    Usage: {{ category.products_count|products_count_display }}
    """
    if count == 0:
        return "Нет товаров"
    elif count == 1:
        return "1 товар"
    elif count < 5:
        return f"{count} товара"
    else:
        return f"{count} товаров"