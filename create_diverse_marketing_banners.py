#!/usr/bin/env python3
"""
Скрипт для создания разнообразных баннеров с разными изображениями товаров
"""

import os
import sys
import django
import shutil
from django.core.files.base import ContentFile

# Настройка Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shoplist.settings')
django.setup()

from products.models import Banner, Product, ProductImage

def create_diverse_marketing_banners():
    """Создает разнообразные баннеры с разными изображениями товаров"""
    print("🎯 Создание разнообразных баннеров с разными изображениями товаров...")
    
    # Удаляем существующие баннеры
    Banner.objects.all().delete()
    print("🗑️  Удалены существующие баннеры")
    
    # Получаем все товары с изображениями
    products_with_images = list(Product.objects.filter(
        images__isnull=False,
        is_active=True
    ).prefetch_related('images').distinct())
    
    print(f"📊 Найдено {len(products_with_images)} товаров с изображениями")
    
    # Создаем баннеры с разными изображениями
    banners_data = [
        {
            'title': '🔥 МЕГА РАСПРОДАЖА СМАРТФОНОВ',
            'subtitle': 'iPhone, Samsung, Xiaomi со скидкой до 70%!',
            'banner_type': 'main',
            'link': '/ru/categories/electronics/',
            'sort_order': 1
        },
        {
            'title': '💎 ПРЕМИУМ ЧАСЫ ROLEX',
            'subtitle': 'Эксклюзивные модели. Ограниченная коллекция.',
            'banner_type': 'main',
            'link': '/ru/categories/premium/',
            'sort_order': 2
        },
        {
            'title': '🏠 СОВРЕМЕННАЯ КУХНЯ',
            'subtitle': 'Вся техника для идеальной кухни в одном месте',
            'banner_type': 'main',
            'link': '/ru/categories/home-garden/',
            'sort_order': 3
        },
        {
            'title': '👶 ДЕТСКИЕ ИГРУШКИ',
            'subtitle': 'Безопасные и развивающие игрушки для детей',
            'banner_type': 'footer',
            'link': '/ru/categories/kids/',
            'sort_order': 1
        },
        {
            'title': '💄 КРАСОТА И ЗДОРОВЬЕ',
            'subtitle': 'Косметика, парфюмерия, средства для ухода',
            'banner_type': 'footer',
            'link': '/ru/categories/beauty/',
            'sort_order': 2
        },
        {
            'title': '🏃‍♂️ СПОРТИВНАЯ ОДЕЖДА',
            'subtitle': 'Nike, Adidas, Puma - все для активного образа жизни',
            'banner_type': 'footer',
            'link': '/ru/categories/sports/',
            'sort_order': 3
        },
        {
            'title': '💻 НОУТБУКИ И ПК',
            'subtitle': 'ASUS, Apple, Dell - мощные компьютеры для работы и игр',
            'banner_type': 'sidebar',
            'link': '/ru/categories/technology/',
            'sort_order': 1
        },
        {
            'title': '👗 МОДНАЯ ОДЕЖДА',
            'subtitle': 'Zara, H&M, Uniqlo - актуальные тренды сезона',
            'banner_type': 'sidebar',
            'link': '/ru/categories/fashion/',
            'sort_order': 2
        }
    ]
    
    created_count = 0
    used_products = set()  # Отслеживаем использованные товары
    
    for i, banner_data in enumerate(banners_data):
        try:
            # Выбираем товар, который еще не использовался
            suitable_product = None
            for product in products_with_images:
                if product.id not in used_products:
                    suitable_product = product
                    used_products.add(product.id)
                    break
            
            # Если все товары использованы, начинаем заново
            if not suitable_product and products_with_images:
                suitable_product = products_with_images[i % len(products_with_images)]
            
            if not suitable_product:
                print(f"❌ Не найдено товаров с изображениями для баннера: {banner_data['title']}")
                continue
            
            # Получаем первое изображение товара
            product_image = suitable_product.images.first()
            if not product_image:
                print(f"❌ У товара {suitable_product.name} нет изображений")
                continue
            
            # Создаем баннер
            banner = Banner.objects.create(
                title=banner_data['title'],
                subtitle=banner_data['subtitle'],
                banner_type=banner_data['banner_type'],
                link=banner_data['link'],
                sort_order=banner_data['sort_order'],
                is_active=True
            )
            
            # Копируем изображение товара
            if product_image.image:
                # Читаем исходное изображение
                with open(product_image.image.path, 'rb') as f:
                    image_content = ContentFile(f.read())
                
                # Сохраняем как изображение баннера
                banner.image.save(
                    f"marketing_banner_{banner.id}.jpg",
                    image_content,
                    save=True
                )
                
                print(f"✅ Создан баннер: {banner.title}")
                print(f"   Использовано изображение товара: {suitable_product.name}")
                created_count += 1
            else:
                print(f"❌ У товара {suitable_product.name} нет файла изображения")
                banner.delete()
                
        except Exception as e:
            print(f"❌ Ошибка при создании баннера '{banner_data['title']}': {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n🎉 Создано {created_count} баннеров с реальными изображениями товаров")
    print(f"📊 Всего баннеров в базе: {Banner.objects.count()}")
    
    # Показываем созданные баннеры
    print("\n📋 Список всех баннеров:")
    for banner in Banner.objects.all().order_by('sort_order'):
        print(f"  - {banner.title} ({banner.banner_type}) - {'Активен' if banner.is_active else 'Неактивен'}")
        print(f"    Подзаголовок: {banner.subtitle}")
        print(f"    Изображение: {'Есть' if banner.image else 'Нет'}")

if __name__ == '__main__':
    create_diverse_marketing_banners()









