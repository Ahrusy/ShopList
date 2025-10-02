#!/usr/bin/env python3
"""
Скрипт для обновления баннеров с русскими заголовками
"""

import os
import sys
import django

# Настройка Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shoplist.settings')
django.setup()

from products.models import Banner

def update_banners_russian():
    """Обновляет баннеры с русскими заголовками"""
    print("🎯 Обновление баннеров с русскими заголовками...")
    
    # Обновляем существующие баннеры
    banners_updates = [
        {
            'title': 'МЕГА РАСПРОДАЖА',
            'subtitle': 'Скидки до 80% на электронику и бытовую технику',
            'banner_type': 'main',
            'sort_order': 1
        },
        {
            'title': 'ПРЕМИУМ КОЛЛЕКЦИЯ',
            'subtitle': 'Эксклюзивные товары от мировых брендов',
            'banner_type': 'main',
            'sort_order': 2
        },
        {
            'title': 'ДЛЯ ДОМА И САДА',
            'subtitle': 'Все необходимое для уюта и комфорта',
            'banner_type': 'main',
            'sort_order': 3
        },
        {
            'title': 'ДЕТСКИЙ МИР',
            'subtitle': 'Безопасные и качественные товары для детей',
            'banner_type': 'footer',
            'sort_order': 1
        },
        {
            'title': 'КРАСОТА И ЗДОРОВЬЕ',
            'subtitle': 'Уход за собой и поддержание здоровья',
            'banner_type': 'footer',
            'sort_order': 2
        },
        {
            'title': 'СПОРТ И АКТИВНОСТЬ',
            'subtitle': 'Экипировка для спорта и активного отдыха',
            'banner_type': 'footer',
            'sort_order': 3
        }
    ]
    
    updated_count = 0
    
    for i, banner_data in enumerate(banners_updates):
        try:
            # Получаем баннер по порядку
            banner = Banner.objects.all().order_by('sort_order')[i]
            
            # Обновляем данные
            banner.title = banner_data['title']
            banner.subtitle = banner_data['subtitle']
            banner.banner_type = banner_data['banner_type']
            banner.sort_order = banner_data['sort_order']
            banner.save()
            
            print(f"✅ Обновлен баннер: {banner.title}")
            updated_count += 1
            
        except Exception as e:
            print(f"❌ Ошибка при обновлении баннера '{banner_data['title']}': {e}")
    
    print(f"\n🎉 Обновлено {updated_count} баннеров")
    print(f"📊 Всего баннеров в базе: {Banner.objects.count()}")
    
    # Показываем обновленные баннеры
    print("\n📋 Список всех баннеров:")
    for banner in Banner.objects.all().order_by('sort_order'):
        print(f"  - {banner.title} ({banner.banner_type}) - {'Активен' if banner.is_active else 'Неактивен'}")
        print(f"    Подзаголовок: {banner.subtitle}")

if __name__ == '__main__':
    update_banners_russian()









