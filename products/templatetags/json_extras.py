"""
Дополнительные теги шаблонов для работы с JSON
"""

from django import template
import json

register = template.Library()


@register.filter
def jsonify(value):
    """Преобразует объект в JSON строку"""
    if hasattr(value, '__iter__') and not isinstance(value, (str, bytes)):
        # Если это QuerySet или список объектов
        data = []
        for item in value:
            if hasattr(item, 'name') and hasattr(item, 'latitude') and hasattr(item, 'longitude'):
                # Это магазин
                data.append({
                    'id': item.id,
                    'name': item.name,
                    'address': item.address,
                    'city': item.city,
                    'phone': getattr(item, 'phone', ''),
                    'latitude': item.latitude,
                    'longitude': item.longitude
                })
            else:
                # Обычный объект
                data.append(str(item))
        return json.dumps(data)
    else:
        return json.dumps(value)


@register.filter
def shops_to_json(shops):
    """Преобразует QuerySet магазинов в JSON для карты"""
    data = []
    for shop in shops:
        data.append({
            'id': shop.id,
            'name': shop.name or '',
            'address': shop.address or '',
            'city': shop.city or '',
            'phone': getattr(shop, 'phone', '') or '',
            'latitude': shop.latitude,
            'longitude': shop.longitude
        })
    return json.dumps(data)