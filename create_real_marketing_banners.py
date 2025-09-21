#!/usr/bin/env python3
"""
Скрипт для создания баннеров с реальными маркетинговыми фотографиями
"""

import os
import sys
import django
import requests
from io import BytesIO
from django.core.files.base import ContentFile

# Настройка Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shoplist.settings')
django.setup()

from products.models import Banner

def download_image(url, timeout=10):
    """Скачивает изображение по URL"""
    try:
        response = requests.get(url, timeout=timeout)
        if response.status_code == 200:
            return ContentFile(response.content)
        return None
    except Exception as e:
        print(f"Ошибка при скачивании изображения {url}: {e}")
        return None

def create_real_marketing_banners():
    """Создает баннеры с реальными маркетинговыми фотографиями"""
    print("🎯 Создание баннеров с реальными маркетинговыми фотографиями...")
    
    # Удаляем существующие баннеры
    Banner.objects.all().delete()
    print("🗑️  Удалены существующие баннеры")
    
    # Список баннеров с реальными изображениями товаров
    banners_data = [
        {
            'title': '🔥 МЕГА РАСПРОДАЖА СМАРТФОНОВ',
            'subtitle': 'iPhone, Samsung, Xiaomi со скидкой до 70%!',
            'banner_type': 'main',
            'image_url': 'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=800&h=400&fit=crop&crop=center',
            'link': '/ru/categories/electronics/',
            'sort_order': 1
        },
        {
            'title': '💎 ПРЕМИУМ ЧАСЫ ROLEX',
            'subtitle': 'Эксклюзивные модели. Ограниченная коллекция.',
            'banner_type': 'main',
            'image_url': 'https://images.unsplash.com/photo-1523170335258-f5c6a6b3e1b5?w=800&h=400&fit=crop&crop=center',
            'link': '/ru/categories/premium/',
            'sort_order': 2
        },
        {
            'title': '🏠 СОВРЕМЕННАЯ КУХНЯ',
            'subtitle': 'Вся техника для идеальной кухни в одном месте',
            'banner_type': 'main',
            'image_url': 'https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=800&h=400&fit=crop&crop=center',
            'link': '/ru/categories/home-garden/',
            'sort_order': 3
        },
        {
            'title': '👶 ДЕТСКИЕ ИГРУШКИ',
            'subtitle': 'Безопасные и развивающие игрушки для детей',
            'banner_type': 'footer',
            'image_url': 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=600&h=300&fit=crop&crop=center',
            'link': '/ru/categories/kids/',
            'sort_order': 1
        },
        {
            'title': '💄 КРАСОТА И ЗДОРОВЬЕ',
            'subtitle': 'Косметика, парфюмерия, средства для ухода',
            'banner_type': 'footer',
            'image_url': 'https://images.unsplash.com/photo-1596462502278-27bfdc403348?w=600&h=300&fit=crop&crop=center',
            'link': '/ru/categories/beauty/',
            'sort_order': 2
        },
        {
            'title': '🏃‍♂️ СПОРТИВНАЯ ОДЕЖДА',
            'subtitle': 'Nike, Adidas, Puma - все для активного образа жизни',
            'banner_type': 'footer',
            'image_url': 'https://images.unsplash.com/photo-1544966503-7cc5ac882d5f?w=600&h=300&fit=crop&crop=center',
            'link': '/ru/categories/sports/',
            'sort_order': 3
        },
        {
            'title': '💻 НОУТБУКИ И ПК',
            'subtitle': 'ASUS, Apple, Dell - мощные компьютеры для работы и игр',
            'banner_type': 'sidebar',
            'image_url': 'https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=600&h=300&fit=crop&crop=center',
            'link': '/ru/categories/technology/',
            'sort_order': 1
        },
        {
            'title': '👗 МОДНАЯ ОДЕЖДА',
            'subtitle': 'Zara, H&M, Uniqlo - актуальные тренды сезона',
            'banner_type': 'sidebar',
            'image_url': 'https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=600&h=300&fit=crop&crop=center',
            'link': '/ru/categories/fashion/',
            'sort_order': 2
        }
    ]
    
    created_count = 0
    
    for banner_data in banners_data:
        try:
            # Создаем баннер
            banner = Banner.objects.create(
                title=banner_data['title'],
                subtitle=banner_data['subtitle'],
                banner_type=banner_data['banner_type'],
                link=banner_data['link'],
                sort_order=banner_data['sort_order'],
                is_active=True
            )
            
            # Скачиваем изображение
            image_content = download_image(banner_data['image_url'])
            
            if image_content:
                # Сохраняем изображение
                banner.image.save(
                    f"marketing_banner_{banner.id}.jpg",
                    image_content,
                    save=True
                )
                print(f"✅ Создан баннер: {banner.title}")
                created_count += 1
            else:
                print(f"❌ Не удалось загрузить изображение для: {banner.title}")
                banner.delete()
                
        except Exception as e:
            print(f"❌ Ошибка при создании баннера '{banner_data['title']}': {e}")
    
    print(f"\n🎉 Создано {created_count} баннеров с реальными фотографиями")
    print(f"📊 Всего баннеров в базе: {Banner.objects.count()}")
    
    # Показываем созданные баннеры
    print("\n📋 Список всех баннеров:")
    for banner in Banner.objects.all().order_by('sort_order'):
        print(f"  - {banner.title} ({banner.banner_type}) - {'Активен' if banner.is_active else 'Неактивен'}")
        print(f"    Подзаголовок: {banner.subtitle}")

if __name__ == '__main__':
    create_real_marketing_banners()



