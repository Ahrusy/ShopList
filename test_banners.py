#!/usr/bin/env python3
"""
Скрипт для тестирования баннеров
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
from django.urls import reverse

def test_banners():
    """Тестирует отображение баннеров"""
    print("🎯 Тестирование баннеров...")
    
    # Проверяем баннеры в базе данных
    banners = Banner.objects.filter(is_active=True).order_by('sort_order')
    print(f"📊 Найдено {banners.count()} активных баннеров:")
    
    for banner in banners:
        print(f"  - {banner.title} ({banner.banner_type})")
        print(f"    Подзаголовок: {banner.subtitle}")
        print(f"    Ссылка: {banner.link}")
        print(f"    Изображение: {'Есть' if banner.image else 'Нет'}")
        print()
    
    # Тестируем главную страницу
    client = Client()
    try:
        response = client.get('/ru/')
        print(f"✅ Главная страница загружается: {response.status_code}")
        
        if 'banners' in response.context:
            context_banners = response.context['banners']
            print(f"📋 Баннеры в контексте: {len(context_banners)}")
            for banner in context_banners:
                print(f"  - {banner.title}")
        else:
            print("❌ Баннеры не найдены в контексте")
            
    except Exception as e:
        print(f"❌ Ошибка при загрузке главной страницы: {e}")
    
    # Проверяем типы баннеров
    main_banners = Banner.objects.filter(banner_type='main', is_active=True)
    footer_banners = Banner.objects.filter(banner_type='footer', is_active=True)
    sidebar_banners = Banner.objects.filter(banner_type='sidebar', is_active=True)
    
    print(f"📊 Распределение баннеров по типам:")
    print(f"  - Главные баннеры: {main_banners.count()}")
    print(f"  - Нижние баннеры: {footer_banners.count()}")
    print(f"  - Боковые баннеры: {sidebar_banners.count()}")

if __name__ == '__main__':
    test_banners()



