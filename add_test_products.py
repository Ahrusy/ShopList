#!/usr/bin/env python
import os
import sys
import django

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shoplist.settings')
django.setup()

from products.models import Category, Shop, Seller, Product, User
from decimal import Decimal

# Создаем категории
electronics, _ = Category.objects.get_or_create(
    slug='electronics',
    defaults={'name': 'Электроника', 'icon': 'laptop'}
)

clothing, _ = Category.objects.get_or_create(
    slug='clothing', 
    defaults={'name': 'Одежда', 'icon': 'tshirt'}
)

# Создаем магазин
shop, _ = Shop.objects.get_or_create(
    name='Тестовый магазин',
    defaults={
        'address': 'Москва, ул. Тестовая, 1',
        'city': 'Москва',
        'phone': '+7 (999) 123-45-67',
        'email': 'test@shop.ru'
    }
)

# Создаем продавца
user, _ = User.objects.get_or_create(
    username='seller1',
    defaults={
        'email': 'seller1@example.com',
        'role': 'seller'
    }
)
if not user.password:
    user.set_password('password123')
    user.save()

seller, _ = Seller.objects.get_or_create(
    user=user,
    defaults={
        'company_name': 'ООО Тестовая компания',
        'description': 'Продаем качественные товары',
        'commission_rate': Decimal('5.0'),
        'is_verified': True
    }
)

# Создаем товары
products_data = [
    {
        'name': 'iPhone 15 Pro',
        'description': 'Новейший смартфон от Apple с чипом A17 Pro',
        'price': Decimal('99999.00'),
        'category': electronics,
        'stock_quantity': 10
    },
    {
        'name': 'MacBook Air M2',
        'description': 'Легкий и мощный ноутбук для работы и творчества',
        'price': Decimal('129999.00'),
        'category': electronics,
        'stock_quantity': 5
    },
    {
        'name': 'Джинсы Levis 501',
        'description': 'Классические джинсы из денима',
        'price': Decimal('5999.00'),
        'category': clothing,
        'stock_quantity': 20
    },
    {
        'name': 'Футболка Nike',
        'description': 'Удобная футболка для спорта и повседневной носки',
        'price': Decimal('2999.00'),
        'category': clothing,
        'stock_quantity': 50
    },
    {
        'name': 'AirPods Pro',
        'description': 'Беспроводные наушники с активным шумоподавлением',
        'price': Decimal('24999.00'),
        'category': electronics,
        'stock_quantity': 15
    }
]

for product_data in products_data:
    product, created = Product.objects.get_or_create(
        name=product_data['name'],
        defaults={
            'description': product_data['description'],
            'price': product_data['price'],
            'category': product_data['category'],
            'seller': seller,
            'stock_quantity': product_data['stock_quantity'],
            'rating': Decimal('4.5'),
            'reviews_count': 10
        }
    )
    if created:
        print(f"Создан товар: {product.name}")

print("Тестовые товары добавлены!")
print("Откройте http://127.0.0.1:8000/ для просмотра каталога")
