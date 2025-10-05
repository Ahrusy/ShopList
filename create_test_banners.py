#!/usr/bin/env python
"""
Script to create test banners for the main page
"""
import os
import sys
import django
from django.core.files.base import ContentFile
import random

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shoplist.settings')
django.setup()

from products.models import Banner, ProductBanner

def create_test_banners():
    """Create test banners for the main page"""
    
    # Clear existing banners
    Banner.objects.all().delete()
    ProductBanner.objects.all().delete()
    
    print("Creating test banners...")
    
    # Create advertising banners
    banner_data = [
        {
            'title': '🔥 МЕГА РАСПРОДАЖА СМАРТФОНОВ',
            'subtitle': 'Скидки до 50% на все модели iPhone и Samsung',
            'link': '/category/smartfony/',
            'banner_type': 'main',
            'sort_order': 1
        },
        {
            'title': '💻 НОУТБУКИ И ПК',
            'subtitle': 'Мощные компьютеры для работы и игр',
            'link': '/category/kompyutery/',
            'banner_type': 'main',
            'sort_order': 2
        },
        {
            'title': '👶 ДЕТСКИЕ ИГРУШКИ',
            'subtitle': 'Развивающие игрушки для детей всех возрастов',
            'link': '/category/detskie-tovary/',
            'banner_type': 'main',
            'sort_order': 3
        },
        {
            'title': '💄 КРАСОТА И ЗДОРОВЬЕ',
            'subtitle': 'Косметика и уходовые средства премиум класса',
            'link': '/category/krasota-i-zdorove/',
            'banner_type': 'main',
            'sort_order': 4
        },
        {
            'title': '👗 МОДНАЯ ОДЕЖДА',
            'subtitle': 'Новинки сезона от известных брендов',
            'link': '/category/odezhda/',
            'banner_type': 'main',
            'sort_order': 5
        },
        {
            'title': '💎 ПРЕМИУМ ЧАСЫ ROLEX',
            'subtitle': 'Эксклюзивные коллекции мужских и женских часов',
            'link': '/category/chasy/',
            'banner_type': 'main',
            'sort_order': 6
        },
        {
            'title': '🏠 СОВРЕМЕННАЯ КУХНЯ',
            'subtitle': 'Техника и аксессуары для кухни',
            'link': '/category/bytovaya-tehnika/',
            'banner_type': 'main',
            'sort_order': 7
        },
        {
            'title': '🏃‍♂️ СПОРТИВНАЯ ОДЕЖДА',
            'subtitle': 'Одежда и обувь для активного образа жизни',
            'link': '/category/sport-i-otdyh/',
            'banner_type': 'main',
            'sort_order': 8
        }
    ]
    
    # Create banners
    for i, data in enumerate(banner_data):
        banner = Banner.objects.create(
            title=data['title'],
            subtitle=data['subtitle'],
            link=data['link'],
            banner_type=data['banner_type'],
            sort_order=data['sort_order'],
            is_active=True
        )
        
        # Create a simple colored image for the banner
        image_content = create_simple_banner_image(f"Banner {i+1}", data['title'])
        banner.image.save(f'banner_{i+1}.png', ContentFile(image_content))
        banner.save()
        
        print(f"Created banner: {banner.title}")
    
    # Create product banners for slider
    product_banner_data = [
        {
            'title': 'Смартфоны',
            'subtitle': 'Новинки 2025',
            'description': 'Самые свежие модели смартфонов по лучшим ценам',
            'link': '/category/smartfony/',
            'style': 'new',
            'button_text': 'Выбрать',
            'background_color': '#FF6B35',
            'text_color': '#FFFFFF',
            'sort_order': 1
        },
        {
            'title': 'Ноутбуки',
            'subtitle': 'До -30%',
            'description': 'Мощные ноутбуки для работы и игр со скидкой',
            'link': '/category/noutbuki/',
            'style': 'discount',
            'button_text': 'Купить',
            'background_color': '#005BFF',
            'text_color': '#FFFFFF',
            'sort_order': 2
        },
        {
            'title': 'Часы',
            'subtitle': 'Премиум',
            'description': 'Элитные часы от известных брендов',
            'link': '/category/chasy/',
            'style': 'premium',
            'button_text': 'Смотреть',
            'background_color': '#2E7D32',
            'text_color': '#FFFFFF',
            'sort_order': 3
        },
        {
            'title': 'Косметика',
            'subtitle': 'Хит продаж',
            'description': 'Популярные товары по уходу за кожей',
            'link': '/category/krasota-i-zdorove/',
            'style': 'popular',
            'button_text': 'Выбрать',
            'background_color': '#9C27B0',
            'text_color': '#FFFFFF',
            'sort_order': 4
        },
        {
            'title': 'Доставка',
            'subtitle': 'Бесплатно',
            'description': 'Бесплатная доставка при заказе от 3000 ₽',
            'link': '/delivery/',
            'style': 'delivery',
            'button_text': 'Подробнее',
            'background_color': '#FFC107',
            'text_color': '#000000',
            'sort_order': 5
        },
        {
            'title': 'Распродажа',
            'subtitle': 'До -70%',
            'description': 'Распродажа товаров прошлого сезона',
            'link': '/sale/',
            'style': 'sale',
            'button_text': 'Смотреть',
            'background_color': '#F44336',
            'text_color': '#FFFFFF',
            'sort_order': 6
        }
    ]
    
    # Create product banners
    for i, data in enumerate(product_banner_data):
        product_banner = ProductBanner.objects.create(
            title=data['title'],
            subtitle=data['subtitle'],
            description=data['description'],
            link=data['link'],
            style=data['style'],
            button_text=data['button_text'],
            background_color=data['background_color'],
            text_color=data['text_color'],
            sort_order=data['sort_order'],
            is_active=True
        )
        
        # Create a simple colored image for the product banner
        image_content = create_simple_product_banner_image(
            data['title'], 
            data['subtitle'], 
            data['background_color']
        )
        product_banner.image.save(f'product_banner_{i+1}.png', ContentFile(image_content))
        product_banner.save()
        
        print(f"Created product banner: {product_banner.title}")
    
    print(f"\n✅ Created {Banner.objects.count()} advertising banners")
    print(f"✅ Created {ProductBanner.objects.count()} product banners")
    print("🎉 Banners created successfully!")

def create_simple_banner_image(text, title):
    """Create a simple colored image for banner"""
    # Create a simple colored image with text
    import io
    from PIL import Image, ImageDraw, ImageFont
    
    # Create image
    width, height = 800, 320
    image = Image.new('RGB', (width, height), color=(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
    draw = ImageDraw.Draw(image)
    
    # Try to use a font, fallback to default if not available
    try:
        font = ImageFont.truetype("arial.ttf", 24)
        title_font = ImageFont.truetype("arial.ttf", 32)
    except:
        font = ImageFont.load_default()
        title_font = ImageFont.load_default()
    
    # Draw text
    draw.text((50, 50), title, fill=(255, 255, 255), font=title_font)
    draw.text((50, 100), text, fill=(255, 255, 255), font=font)
    
    # Save to bytes
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='PNG')
    return img_byte_arr.getvalue()

def create_simple_product_banner_image(title, subtitle, bg_color):
    """Create a simple colored image for product banner"""
    import io
    from PIL import Image, ImageDraw, ImageFont
    
    # Create image
    width, height = 400, 300
    # Convert hex color to RGB
    if bg_color.startswith('#'):
        bg_color = tuple(int(bg_color[i:i+2], 16) for i in (1, 3, 5))
    else:
        bg_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    
    image = Image.new('RGB', (width, height), color=bg_color)
    draw = ImageDraw.Draw(image)
    
    # Try to use a font, fallback to default if not available
    try:
        font = ImageFont.truetype("arial.ttf", 20)
        subtitle_font = ImageFont.truetype("arial.ttf", 16)
    except:
        font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()
    
    # Draw text
    draw.text((20, 20), title, fill=(255, 255, 255), font=font)
    draw.text((20, 60), subtitle, fill=(255, 255, 255), font=subtitle_font)
    
    # Save to bytes
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='PNG')
    return img_byte_arr.getvalue()

if __name__ == "__main__":
    create_test_banners()