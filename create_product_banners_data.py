#!/usr/bin/env python
"""
Скрипт для создания товарных баннеров в базе данных
"""
import os
import sys
import django

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from products.models import ProductBanner

def create_product_banners():
    """Создает товарные баннеры"""
    
    banners_data = [
        {
            'title': 'НОВИНКИ',
            'subtitle': 'Свежие поступления каждый день',
            'description': 'Новейшие товары от ведущих брендов',
            'style': 'new',
            'button_text': 'Смотреть новинки',
            'link': '/products/?sort=new',
            'background_color': '#FF6B35',
            'text_color': '#FFFFFF',
            'sort_order': 1
        },
        {
            'title': 'СКИДКИ ДО 70%',
            'subtitle': 'На электронику и бытовую технику',
            'description': 'Огромные скидки на популярные товары',
            'style': 'discount',
            'button_text': 'Смотреть скидки',
            'link': '/products/?discount=true',
            'background_color': '#E53E3E',
            'text_color': '#FFFFFF',
            'sort_order': 2
        },
        {
            'title': 'ПРЕМИУМ БРЕНДЫ',
            'subtitle': 'Только оригинальная продукция',
            'description': 'Эксклюзивные товары премиум-класса',
            'style': 'premium',
            'button_text': 'Премиум товары',
            'link': '/products/?brand=premium',
            'background_color': '#805AD5',
            'text_color': '#FFFFFF',
            'sort_order': 3
        },
        {
            'title': 'БЕСПЛАТНАЯ ДОСТАВКА',
            'subtitle': 'При заказе от 2000₽',
            'description': 'Быстрая и бесплатная доставка по всей России',
            'style': 'delivery',
            'button_text': 'Условия доставки',
            'link': '/products/?free_delivery=true',
            'background_color': '#38A169',
            'text_color': '#FFFFFF',
            'sort_order': 4
        },
        {
            'title': 'ХИТЫ ПРОДАЖ',
            'subtitle': 'Самые популярные товары',
            'description': 'Товары, которые выбирают наши покупатели',
            'style': 'popular',
            'button_text': 'Смотреть хиты',
            'link': '/products/?sort=popular',
            'background_color': '#D69E2E',
            'text_color': '#FFFFFF',
            'sort_order': 5
        },
        {
            'title': 'РАСПРОДАЖА',
            'subtitle': 'Ограниченное предложение',
            'description': 'Последние дни распродажи со скидками до 50%',
            'style': 'sale',
            'button_text': 'Успеть купить',
            'link': '/products/?sale=true',
            'background_color': '#C53030',
            'text_color': '#FFFFFF',
            'sort_order': 6
        }
    ]
    
    created_count = 0
    
    for banner_data in banners_data:
        banner, created = ProductBanner.objects.get_or_create(
            title=banner_data['title'],
            defaults={
                'subtitle': banner_data['subtitle'],
                'description': banner_data['description'],
                'style': banner_data['style'],
                'button_text': banner_data['button_text'],
                'link': banner_data['link'],
                'background_color': banner_data['background_color'],
                'text_color': banner_data['text_color'],
                'sort_order': banner_data['sort_order'],
                'is_active': True
            }
        )
        
        if created:
            created_count += 1
            print(f"✅ Создан баннер: {banner.title}")
        else:
            print(f"⚠️  Баннер уже существует: {banner.title}")
    
    print(f"\n🎉 Создано {created_count} новых товарных баннеров!")
    print(f"📊 Всего баннеров в базе: {ProductBanner.objects.count()}")
    
    # Показываем активные баннеры
    active_banners = ProductBanner.objects.filter(is_active=True).order_by('sort_order')
    print(f"\n📋 Активные баннеры ({active_banners.count()}):")
    for banner in active_banners:
        print(f"  {banner.sort_order}. {banner.title} ({banner.get_style_display()})")

if __name__ == '__main__':
    create_product_banners()
