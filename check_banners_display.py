#!/usr/bin/env python3
"""
Скрипт для проверки отображения баннеров на главной странице
"""

import os
import sys
import django

# Настройка Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shoplist.settings')
django.setup()

from products.models import Banner
from django.test import Client

def check_banners_display():
    """Проверяет отображение баннеров на главной странице"""
    print("🎯 Проверка отображения баннеров...")
    
    # Проверяем баннеры в базе данных
    banners = Banner.objects.filter(is_active=True)
    print(f"📊 Баннеров в базе данных: {banners.count()}")
    
    for banner in banners:
        print(f"  - {banner.title} ({banner.banner_type}) - {'Активен' if banner.is_active else 'Неактивен'}")
        print(f"    Изображение: {'Есть' if banner.image else 'Нет'}")
    
    # Тестируем главную страницу
    client = Client()
    try:
        response = client.get('/ru/')
        print(f"\n✅ Главная страница загружается: {response.status_code}")
        
        if hasattr(response, 'context') and response.context:
            if 'banners' in response.context:
                context_banners = response.context['banners']
                print(f"📋 Баннеры в контексте: {len(context_banners)}")
                for banner in context_banners:
                    print(f"  - {banner.title}")
            else:
                print("❌ Баннеры не найдены в контексте")
                print(f"Доступные ключи контекста: {list(response.context.keys())}")
        else:
            print("❌ Контекст не доступен")
            
    except Exception as e:
        print(f"❌ Ошибка при загрузке главной страницы: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    check_banners_display()









