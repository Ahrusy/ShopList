#!/usr/bin/env python
"""
Script to create test products for the main page
"""
import os
import sys
import django
from django.core.files.base import ContentFile
import random

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shoplist.settings')
django.setup()

from products.models import Product, Category, ProductImage, Tag
from django.contrib.auth import get_user_model

User = get_user_model()

def create_test_products():
    """Create test products for the main page"""
    
    print("Creating test products...")
    
    # Create a test seller if none exists
    try:
        seller_user = User.objects.get(username='test_seller')
    except User.DoesNotExist:
        seller_user = User.objects.create_user(
            username='test_seller',
            email='seller@test.com',
            password='testpass123',
            role='seller'
        )
    
    # Create or get seller profile
    from products.models import Seller
    try:
        seller = Seller.objects.get(user=seller_user)
    except Seller.DoesNotExist:
        seller = Seller.objects.create(
            user=seller_user,
            company_name='Test Seller Company',
            description='Test seller for demo products',
            commission_rate=5.00
        )
    
    # Create categories if they don't exist
    categories_data = [
        {'name': 'Смартфоны', 'slug': 'smartfony'},
        {'name': 'Ноутбуки', 'slug': 'noutbuki'},
        {'name': 'Часы', 'slug': 'chasy'},
        {'name': 'Красота и здоровье', 'slug': 'krasota-i-zdorove'},
        {'name': 'Одежда', 'slug': 'odezhda'},
        {'name': 'Детские товары', 'slug': 'detskie-tovary'},
        {'name': 'Бытовая техника', 'slug': 'bytovaya-tehnika'},
        {'name': 'Спорт и отдых', 'slug': 'sport-i-otdyh'},
    ]
    
    categories = []
    for cat_data in categories_data:
        category, created = Category.objects.get_or_create(
            slug=cat_data['slug'],
            defaults={
                'name': cat_data['name'],
                'is_active': True
            }
        )
        categories.append(category)
        if created:
            print(f"Created category: {category.name}")
    
    # Create tags
    tags_data = ['Новинка', 'Хит продаж', 'Распродажа', 'Премиум']
    tags = []
    for tag_name in tags_data:
        tag, created = Tag.objects.get_or_create(
            name=tag_name,
            defaults={
                'color': '#007bff'
            }
        )
        tags.append(tag)
    
    # Create test products
    products_data = [
        {
            'name': 'Смартфон Apple iPhone 15 Pro',
            'description': 'Новейший смартфон Apple с процессором A17 Pro, титановым корпусом и улучшенной камерой.',
            'price': 99990.00,
            'discount_price': 89990.00,
            'category': categories[0],  # Смартфоны
            'stock_quantity': 25,
            'rating': 4.8
        },
        {
            'name': 'Ноутбук Dell XPS 13',
            'description': 'Ультрабук с процессором Intel Core 11-го поколения, экраном InfinityEdge и до 16 часов автономной работы.',
            'price': 129990.00,
            'discount_price': 119990.00,
            'category': categories[1],  # Ноутбуки
            'stock_quantity': 15,
            'rating': 4.7
        },
        {
            'name': 'Часы Rolex Submariner',
            'description': 'Легендарные водолазные часы Rolex с автоматическим механизмом и водонепроницаемостью до 300 метров.',
            'price': 899000.00,
            'category': categories[2],  # Часы
            'stock_quantity': 5,
            'rating': 5.0
        },
        {
            'name': 'Крем для лица La Mer',
            'description': 'Революционный увлажняющий крем для лица, который увлажняет кожу до 24 часов и уменьшает признаки старения.',
            'price': 24500.00,
            'discount_price': 19900.00,
            'category': categories[3],  # Красота и здоровье
            'stock_quantity': 50,
            'rating': 4.9
        },
        {
            'name': 'Куртка мужская зимняя',
            'description': 'Утепленная мужская куртка на синтепоне, водонепроницаемая, с капюшоном и множеством карманов.',
            'price': 8990.00,
            'category': categories[4],  # Одежда
            'stock_quantity': 30,
            'rating': 4.5
        },
        {
            'name': 'Конструктор LEGO Technic',
            'description': 'Детский конструктор с 1000 деталей для создания реалистичной модели гоночного автомобиля.',
            'price': 12990.00,
            'discount_price': 9990.00,
            'category': categories[5],  # Детские товары
            'stock_quantity': 40,
            'rating': 4.6
        },
        {
            'name': 'Робот-пылесос Xiaomi',
            'description': 'Умный робот-пылесос с лазерной навигацией, мощной suction и приложением для управления.',
            'price': 24990.00,
            'category': categories[6],  # Бытовая техника
            'stock_quantity': 20,
            'rating': 4.4
        },
        {
            'name': 'Велотренажер NordicTrack',
            'description': 'Профессиональный велотренажер с 22-дюймовым экраном, подключением к приложениям и 24 уровнями сопротивления.',
            'price': 69990.00,
            'discount_price': 59990.00,
            'category': categories[7],  # Спорт и отдых
            'stock_quantity': 8,
            'rating': 4.7
        },
        {
            'name': 'Смартфон Samsung Galaxy S24 Ultra',
            'description': 'Флагманский смартфон Samsung с процессором Snapdragon 8 Gen 3, камерой 200 МП и стилусом S Pen.',
            'price': 119990.00,
            'category': categories[0],  # Смартфоны
            'stock_quantity': 18,
            'rating': 4.9
        },
        {
            'name': 'Ноутбук MacBook Pro 16"',
            'description': 'Профессиональный ноутбук Apple с чипом M3 Pro, экраном Liquid Retina XDR и до 22 часов автономной работы.',
            'price': 299990.00,
            'discount_price': 279990.00,
            'category': categories[1],  # Ноутбуки
            'stock_quantity': 10,
            'rating': 4.9
        },
        {
            'name': 'Часы Casio G-Shock',
            'description': 'Прочные и надежные часы Casio с ударопрочным корпусом, водонепроницаемостью и подсветкой.',
            'price': 9990.00,
            'category': categories[2],  # Часы
            'stock_quantity': 100,
            'rating': 4.6
        },
        {
            'name': 'Массажная кушетка BeautyFit',
            'description': 'Профессиональная массажная кушетка для салонов красоты с регулируемой высотой и подогревом.',
            'price': 34990.00,
            'category': categories[3],  # Красота и здоровье
            'stock_quantity': 12,
            'rating': 4.3
        }
    ]
    
    # Create products
    for i, product_data in enumerate(products_data):
        product = Product.objects.create(
            name=product_data['name'],
            description=product_data['description'],
            price=product_data['price'],
            discount_price=product_data.get('discount_price'),
            category=product_data['category'],
            seller=seller,
            stock_quantity=product_data['stock_quantity'],
            rating=product_data['rating'],
            is_active=True,
            views_count=random.randint(50, 500),
            reviews_count=random.randint(5, 50)
        )
        
        # Add random tags
        if random.choice([True, False]):
            product.tags.add(random.choice(tags))
        if random.choice([True, False]):
            product.tags.add(random.choice(tags))
        
        # Create a simple product image
        image_content = create_simple_product_image(product_data['name'])
        image = ProductImage.objects.create(
            product=product,
            alt_text=f"Изображение {product_data['name']}"
        )
        image.image.save(f'product_{i+1}.png', ContentFile(image_content))
        image.save()
        
        print(f"Created product: {product.name}")
    
    print(f"\n✅ Created {Product.objects.filter(is_active=True).count()} active products")
    print("🎉 Products created successfully!")

def create_simple_product_image(product_name):
    """Create a simple colored image for product"""
    import io
    from PIL import Image, ImageDraw, ImageFont
    
    # Create image
    width, height = 300, 300
    image = Image.new('RGB', (width, height), color=(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
    draw = ImageDraw.Draw(image)
    
    # Try to use a font, fallback to default if not available
    try:
        font = ImageFont.truetype("arial.ttf", 16)
    except:
        font = ImageFont.load_default()
    
    # Draw text
    draw.text((10, 10), product_name[:20], fill=(255, 255, 255), font=font)
    
    # Save to bytes
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='PNG')
    return img_byte_arr.getvalue()

if __name__ == "__main__":
    create_test_products()