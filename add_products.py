#!/usr/bin/env python
import os
import sys
import django

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shoplist.settings')
django.setup()

from products.models import Category, Shop, Seller, Product, User, Tag
from decimal import Decimal

print("=== ДОБАВЛЕНИЕ ТЕСТОВЫХ ДАННЫХ ===")

# Создаем категории
electronics, _ = Category.objects.get_or_create(
    slug='electronics',
    defaults={'name': 'Электроника', 'icon': 'laptop', 'description': 'Электронные товары'}
)

clothing, _ = Category.objects.get_or_create(
    slug='clothing', 
    defaults={'name': 'Одежда', 'icon': 'tshirt', 'description': 'Одежда и обувь'}
)

# Создаем теги
tag1, _ = Tag.objects.get_or_create(name='Популярное')
tag2, _ = Tag.objects.get_or_create(name='Новинка')
tag3, _ = Tag.objects.get_or_create(name='Скидка')

# Создаем магазин
shop, _ = Shop.objects.get_or_create(
    name='ТехноМир',
    defaults={
        'address': 'Москва, ул. Тверская, 1',
        'city': 'Москва',
        'phone': '+7 (999) 123-45-67',
        'email': 'tech@shop.ru'
    }
)

# Создаем продавца
user, _ = User.objects.get_or_create(
    username='seller1',
    defaults={
        'email': 'seller1@example.com',
        'role': 'seller',
        'first_name': 'Иван',
        'last_name': 'Петров'
    }
)
if not user.password:
    user.set_password('password123')
    user.save()

seller, _ = Seller.objects.get_or_create(
    user=user,
    defaults={
        'company_name': 'ООО ТехноМир',
        'description': 'Продаем качественную электронику',
        'commission_rate': Decimal('5.0'),
        'is_verified': True
    }
)

# Создаем товары
products_data = [
    {
        'name': 'iPhone 15 Pro',
        'description': 'Новейший смартфон от Apple с чипом A17 Pro, камерой 48 МП и дисплеем Super Retina XDR',
        'price': Decimal('99999.00'),
        'discount_price': Decimal('89999.00'),
        'category': electronics,
        'stock_quantity': 10,
        'tags': [tag1, tag2]
    },
    {
        'name': 'MacBook Air M2',
        'description': 'Легкий и мощный ноутбук для работы и творчества с чипом M2 и дисплеем Liquid Retina',
        'price': Decimal('129999.00'),
        'category': electronics,
        'stock_quantity': 5,
        'tags': [tag1, tag3]
    },
    {
        'name': 'Джинсы Levis 501',
        'description': 'Классические джинсы из денима с прямым кроем',
        'price': Decimal('5999.00'),
        'discount_price': Decimal('4499.00'),
        'category': clothing,
        'stock_quantity': 20,
        'tags': [tag2, tag3]
    },
    {
        'name': 'Футболка Nike',
        'description': 'Удобная футболка для спорта и повседневной носки из дышащей ткани',
        'price': Decimal('2999.00'),
        'category': clothing,
        'stock_quantity': 50,
        'tags': [tag1]
    },
    {
        'name': 'AirPods Pro',
        'description': 'Беспроводные наушники с активным шумоподавлением и пространственным звуком',
        'price': Decimal('24999.00'),
        'category': electronics,
        'stock_quantity': 15,
        'tags': [tag1, tag2]
    }
]

for product_data in products_data:
    product, created = Product.objects.get_or_create(
        name=product_data['name'],
        defaults={
            'description': product_data['description'],
            'price': product_data['price'],
            'discount_price': product_data.get('discount_price'),
            'category': product_data['category'],
            'seller': seller,
            'stock_quantity': product_data['stock_quantity'],
            'rating': Decimal('4.5'),
            'reviews_count': 10
        }
    )
    if created:
        # Добавляем теги
        product.tags.set(product_data['tags'])
        print(f"✅ Создан товар: {product.name} - {product.final_price} ₽")

print(f"\n=== РЕЗУЛЬТАТ ===")
print(f"Категории: {Category.objects.count()}")
print(f"Товары: {Product.objects.count()}")
print(f"Продавцы: {Seller.objects.count()}")
print(f"Теги: {Tag.objects.count()}")
print(f"\n🎉 Тестовые данные добавлены!")
print(f"🌐 Откройте: http://127.0.0.1:8001/")
print(f"🔧 Админка: http://127.0.0.1:8001/admin/ (admin/admin123)")
