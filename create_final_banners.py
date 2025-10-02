#!/usr/bin/env python3
"""
Скрипт для создания финальных маркетинговых баннеров
"""

import os
import sys
import django
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from django.core.files.base import ContentFile

# Настройка Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shoplist.settings')
django.setup()

from products.models import Banner

def create_banner_image(title, subtitle, width=400, height=200, bg_color=(255, 107, 107)):
    """Создает изображение баннера"""
    # Создаем изображение
    img = Image.new('RGB', (width, height), bg_color)
    draw = ImageDraw.Draw(img)
    
    # Используем стандартный шрифт
    try:
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()
    except:
        title_font = None
        subtitle_font = None
    
    # Рисуем текст
    text_color = (255, 255, 255)
    
    # Заголовок
    draw.text((20, 50), title, fill=text_color, font=title_font)
    # Подзаголовок
    draw.text((20, 100), subtitle, fill=text_color, font=subtitle_font)
    
    # Сохраняем в BytesIO
    img_io = BytesIO()
    img.save(img_io, format='JPEG', quality=85)
    img_io.seek(0)
    
    return ContentFile(img_io.getvalue())

def create_final_banners():
    """Создает финальные маркетинговые баннеры"""
    print("🎯 Создание финальных маркетинговых баннеров...")
    
    # Удаляем существующие баннеры
    Banner.objects.all().delete()
    print("🗑️  Удалены существующие баннеры")
    
    # Список маркетинговых баннеров без эмодзи
    banners_data = [
        {
            'title': 'МЕГА РАСПРОДАЖА',
            'subtitle': 'Скидки до 80% на электронику и бытовую технику',
            'banner_type': 'main',
            'bg_color': (220, 38, 127),  # Ярко-розовый
            'link': '/ru/categories/electronics/',
            'sort_order': 1
        },
        {
            'title': 'ПРЕМИУМ КОЛЛЕКЦИЯ',
            'subtitle': 'Эксклюзивные товары от мировых брендов',
            'banner_type': 'main',
            'bg_color': (59, 130, 246),  # Синий
            'link': '/ru/categories/premium/',
            'sort_order': 2
        },
        {
            'title': 'ДЛЯ ДОМА И САДА',
            'subtitle': 'Все необходимое для уюта и комфорта',
            'banner_type': 'main',
            'bg_color': (34, 197, 94),  # Зеленый
            'link': '/ru/categories/home-garden/',
            'sort_order': 3
        },
        {
            'title': 'ДЕТСКИЙ МИР',
            'subtitle': 'Безопасные и качественные товары для детей',
            'banner_type': 'footer',
            'bg_color': (251, 191, 36),  # Желтый
            'link': '/ru/categories/kids/',
            'sort_order': 1
        },
        {
            'title': 'КРАСОТА И ЗДОРОВЬЕ',
            'subtitle': 'Уход за собой и поддержание здоровья',
            'banner_type': 'footer',
            'bg_color': (236, 72, 153),  # Розовый
            'link': '/ru/categories/beauty/',
            'sort_order': 2
        },
        {
            'title': 'СПОРТ И АКТИВНОСТЬ',
            'subtitle': 'Экипировка для спорта и активного отдыха',
            'banner_type': 'footer',
            'bg_color': (16, 185, 129),  # Изумрудный
            'link': '/ru/categories/sports/',
            'sort_order': 3
        },
        {
            'title': 'НОВИНКИ ТЕХНОЛОГИЙ',
            'subtitle': 'Последние достижения в мире гаджетов',
            'banner_type': 'sidebar',
            'bg_color': (99, 102, 241),  # Фиолетовый
            'link': '/ru/categories/technology/',
            'sort_order': 1
        },
        {
            'title': 'МОДА И СТИЛЬ',
            'subtitle': 'Актуальные тренды в одежде и аксессуарах',
            'banner_type': 'sidebar',
            'bg_color': (239, 68, 68),  # Красный
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
            
            # Создаем изображение
            width = 400 if banner_data['banner_type'] in ['main'] else 300
            height = 200 if banner_data['banner_type'] in ['main'] else 150
            
            image_content = create_banner_image(
                banner_data['title'],
                banner_data['subtitle'],
                width=width,
                height=height,
                bg_color=banner_data['bg_color']
            )
            
            # Сохраняем изображение
            banner.image.save(
                f"final_banner_{banner.id}.jpg",
                image_content,
                save=True
            )
            
            print(f"✅ Создан баннер: {banner.title}")
            created_count += 1
            
        except Exception as e:
            print(f"❌ Ошибка при создании баннера '{banner_data['title']}': {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n🎉 Создано {created_count} маркетинговых баннеров")
    print(f"📊 Всего баннеров в базе: {Banner.objects.count()}")
    
    # Показываем созданные баннеры
    print("\n📋 Список всех баннеров:")
    for banner in Banner.objects.all().order_by('sort_order'):
        print(f"  - {banner.title} ({banner.banner_type}) - {'Активен' if banner.is_active else 'Неактивен'}")

if __name__ == '__main__':
    create_final_banners()



