#!/usr/bin/env python3
"""
Скрипт для создания тестовых рекламных баннеров
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

def create_test_banners():
    """Создает тестовые баннеры для демонстрации"""
    print("🎯 Создание тестовых баннеров...")
    
    # Список тестовых баннеров
    banners_data = [
        {
            'title': 'Скидки до 70%',
            'subtitle': 'На все товары категории "Электроника"',
            'banner_type': 'main',
            'image_url': 'https://via.placeholder.com/400x200/FF6B6B/FFFFFF?text=Скидки+до+70%',
            'link': '/ru/categories/electronics/',
            'sort_order': 1
        },
        {
            'title': 'Новая коллекция',
            'subtitle': 'Одежда и обувь от ведущих брендов',
            'banner_type': 'main',
            'image_url': 'https://via.placeholder.com/400x200/4ECDC4/FFFFFF?text=Новая+коллекция',
            'link': '/ru/categories/clothing/',
            'sort_order': 2
        },
        {
            'title': 'Бытовая техника',
            'subtitle': 'Современные решения для дома',
            'banner_type': 'main',
            'image_url': 'https://via.placeholder.com/400x200/45B7D1/FFFFFF?text=Бытовая+техника',
            'link': '/ru/categories/home-appliances/',
            'sort_order': 3
        },
        {
            'title': 'Спорт и отдых',
            'subtitle': 'Все для активного образа жизни',
            'banner_type': 'footer',
            'image_url': 'https://via.placeholder.com/300x150/96CEB4/FFFFFF?text=Спорт+и+отдых',
            'link': '/ru/categories/sports/',
            'sort_order': 1
        },
        {
            'title': 'Красота и здоровье',
            'subtitle': 'Уход за собой и здоровьем',
            'banner_type': 'footer',
            'image_url': 'https://via.placeholder.com/300x150/FFEAA7/FFFFFF?text=Красота+и+здоровье',
            'link': '/ru/categories/beauty/',
            'sort_order': 2
        },
        {
            'title': 'Детские товары',
            'subtitle': 'Все лучшее для детей',
            'banner_type': 'footer',
            'image_url': 'https://via.placeholder.com/300x150/DDA0DD/FFFFFF?text=Детские+товары',
            'link': '/ru/categories/kids/',
            'sort_order': 3
        }
    ]
    
    created_count = 0
    
    for banner_data in banners_data:
        # Проверяем, существует ли уже такой баннер
        if Banner.objects.filter(title=banner_data['title']).exists():
            print(f"⚠️  Баннер '{banner_data['title']}' уже существует, пропускаем")
            continue
        
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
            
            # Загружаем изображение
            try:
                response = requests.get(banner_data['image_url'], timeout=10)
                if response.status_code == 200:
                    image_content = ContentFile(response.content)
                    banner.image.save(
                        f"banner_{banner.id}.jpg",
                        image_content,
                        save=True
                    )
                    print(f"✅ Создан баннер: {banner.title}")
                    created_count += 1
                else:
                    print(f"❌ Не удалось загрузить изображение для баннера: {banner.title}")
                    banner.delete()
            except Exception as e:
                print(f"❌ Ошибка при загрузке изображения для баннера '{banner.title}': {e}")
                banner.delete()
                
        except Exception as e:
            print(f"❌ Ошибка при создании баннера '{banner_data['title']}': {e}")
    
    print(f"\n🎉 Создано {created_count} баннеров")
    print(f"📊 Всего баннеров в базе: {Banner.objects.count()}")
    
    # Показываем созданные баннеры
    print("\n📋 Список всех баннеров:")
    for banner in Banner.objects.all().order_by('sort_order'):
        print(f"  - {banner.title} ({banner.banner_type}) - {'Активен' if banner.is_active else 'Неактивен'}")

if __name__ == '__main__':
    create_test_banners()



