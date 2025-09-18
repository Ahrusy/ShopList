#!/usr/bin/env python3
"""
Скрипт для создания маркетинговых баннеров с качественным контентом
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

def create_banner_image(title, subtitle, width=400, height=200, bg_color=(255, 107, 107), text_color=(255, 255, 255)):
    """Создает изображение баннера с текстом"""
    # Создаем изображение
    img = Image.new('RGB', (width, height), bg_color)
    draw = ImageDraw.Draw(img)
    
    # Пытаемся использовать системный шрифт
    try:
        # Для Windows
        title_font = ImageFont.truetype("arial.ttf", 24)
        subtitle_font = ImageFont.truetype("arial.ttf", 16)
    except:
        try:
            # Альтернативный шрифт
            title_font = ImageFont.truetype("calibri.ttf", 24)
            subtitle_font = ImageFont.truetype("calibri.ttf", 16)
        except:
            # Используем стандартный шрифт
            title_font = ImageFont.load_default()
            subtitle_font = ImageFont.load_default()
    
    # Получаем размеры текста
    title_bbox = draw.textbbox((0, 0), title, font=title_font)
    title_width = title_bbox[2] - title_bbox[0]
    title_height = title_bbox[3] - title_bbox[1]
    
    subtitle_bbox = draw.textbbox((0, 0), subtitle, font=subtitle_font)
    subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
    subtitle_height = subtitle_bbox[3] - subtitle_bbox[1]
    
    # Вычисляем позиции для центрирования
    title_x = (width - title_width) // 2
    title_y = (height - title_height - subtitle_height - 10) // 2
    
    subtitle_x = (width - subtitle_width) // 2
    subtitle_y = title_y + title_height + 10
    
    # Рисуем текст
    draw.text((title_x, title_y), title, fill=text_color, font=title_font)
    draw.text((subtitle_x, subtitle_y), subtitle, fill=text_color, font=subtitle_font)
    
    # Сохраняем в BytesIO
    img_io = BytesIO()
    img.save(img_io, format='JPEG', quality=85)
    img_io.seek(0)
    
    return ContentFile(img_io.getvalue())

def create_marketing_banners():
    """Создает маркетинговые баннеры с качественным контентом"""
    print("🎯 Создание маркетинговых баннеров...")
    
    # Удаляем существующие баннеры
    Banner.objects.all().delete()
    print("🗑️  Удалены существующие баннеры")
    
    # Список маркетинговых баннеров
    banners_data = [
        {
            'title': '🔥 МЕГА РАСПРОДАЖА',
            'subtitle': 'Скидки до 80% на электронику и бытовую технику',
            'banner_type': 'main',
            'bg_color': (220, 38, 127),  # Ярко-розовый
            'text_color': (255, 255, 255),
            'link': '/ru/categories/electronics/',
            'sort_order': 1
        },
        {
            'title': '💎 ПРЕМИУМ КОЛЛЕКЦИЯ',
            'subtitle': 'Эксклюзивные товары от мировых брендов',
            'banner_type': 'main',
            'bg_color': (59, 130, 246),  # Синий
            'text_color': (255, 255, 255),
            'link': '/ru/categories/premium/',
            'sort_order': 2
        },
        {
            'title': '🏠 ДЛЯ ДОМА И САДА',
            'subtitle': 'Все необходимое для уюта и комфорта',
            'banner_type': 'main',
            'bg_color': (34, 197, 94),  # Зеленый
            'text_color': (255, 255, 255),
            'link': '/ru/categories/home-garden/',
            'sort_order': 3
        },
        {
            'title': '👶 ДЕТСКИЙ МИР',
            'subtitle': 'Безопасные и качественные товары для детей',
            'banner_type': 'footer',
            'bg_color': (251, 191, 36),  # Желтый
            'text_color': (0, 0, 0),
            'link': '/ru/categories/kids/',
            'sort_order': 1
        },
        {
            'title': '💄 КРАСОТА И ЗДОРОВЬЕ',
            'subtitle': 'Уход за собой и поддержание здоровья',
            'banner_type': 'footer',
            'bg_color': (236, 72, 153),  # Розовый
            'text_color': (255, 255, 255),
            'link': '/ru/categories/beauty/',
            'sort_order': 2
        },
        {
            'title': '🏃‍♂️ СПОРТ И АКТИВНОСТЬ',
            'subtitle': 'Экипировка для спорта и активного отдыха',
            'banner_type': 'footer',
            'bg_color': (16, 185, 129),  # Изумрудный
            'text_color': (255, 255, 255),
            'link': '/ru/categories/sports/',
            'sort_order': 3
        },
        {
            'title': '📱 НОВИНКИ ТЕХНОЛОГИЙ',
            'subtitle': 'Последние достижения в мире гаджетов',
            'banner_type': 'sidebar',
            'bg_color': (99, 102, 241),  # Фиолетовый
            'text_color': (255, 255, 255),
            'link': '/ru/categories/technology/',
            'sort_order': 1
        },
        {
            'title': '👗 МОДА И СТИЛЬ',
            'subtitle': 'Актуальные тренды в одежде и аксессуарах',
            'banner_type': 'sidebar',
            'bg_color': (239, 68, 68),  # Красный
            'text_color': (255, 255, 255),
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
                bg_color=banner_data['bg_color'],
                text_color=banner_data['text_color']
            )
            
            # Сохраняем изображение
            banner.image.save(
                f"marketing_banner_{banner.id}.jpg",
                image_content,
                save=True
            )
            
            print(f"✅ Создан баннер: {banner.title}")
            created_count += 1
            
        except Exception as e:
            print(f"❌ Ошибка при создании баннера '{banner_data['title']}': {e}")
    
    print(f"\n🎉 Создано {created_count} маркетинговых баннеров")
    print(f"📊 Всего баннеров в базе: {Banner.objects.count()}")
    
    # Показываем созданные баннеры
    print("\n📋 Список всех баннеров:")
    for banner in Banner.objects.all().order_by('sort_order'):
        print(f"  - {banner.title} ({banner.banner_type}) - {'Активен' if banner.is_active else 'Неактивен'}")

if __name__ == '__main__':
    create_marketing_banners()

