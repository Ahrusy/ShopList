#!/usr/bin/env python
"""
Исправленный скрипт для создания товаров с правильными полями
"""
import os
import django
import random
from faker import Faker

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shoplist.settings')
django.setup()

from django.db import connection
from django.contrib.auth import get_user_model

User = get_user_model()
fake = Faker('ru_RU')

def create_products():
    """Создание товаров с правильными полями"""
    print("🚀 Создаем товары с правильными полями...")
    
    with connection.cursor() as cursor:
        # Создаем пользователя для продавца
        cursor.execute("""
            INSERT INTO products_user (username, email, first_name, last_name, is_staff, is_active, date_joined, role)
            SELECT %s, %s, %s, %s, %s, %s, NOW(), %s
            WHERE NOT EXISTS (SELECT 1 FROM products_user WHERE username = %s)
        """, ["seller", "seller@example.com", "Продавец", "Магазин", False, True, "seller", "seller"])
        
        cursor.execute("SELECT id FROM products_user WHERE username = %s", ["seller"])
        user_id = cursor.fetchone()[0]
        
        # Создаем категории
        categories = [
            {"name": "Смартфоны", "slug": "smartphones"},
            {"name": "Ноутбуки", "slug": "laptops"},
            {"name": "Бытовая техника", "slug": "appliances"},
            {"name": "Одежда", "slug": "clothing"},
            {"name": "Обувь", "slug": "shoes"},
            {"name": "Спорт", "slug": "sports"},
            {"name": "Книги", "slug": "books"},
            {"name": "Мебель", "slug": "furniture"},
            {"name": "Красота", "slug": "beauty"},
            {"name": "Здоровье", "slug": "health"},
        ]
        
        category_ids = {}
        
        for category in categories:
            cursor.execute("""
                INSERT INTO products_category (slug, icon, is_active, created_at, updated_at)
                SELECT %s, %s, %s, NOW(), NOW()
                WHERE NOT EXISTS (SELECT 1 FROM products_category WHERE slug = %s)
            """, [category["slug"], "tag", True, category["slug"]])
            
            cursor.execute("SELECT id FROM products_category WHERE slug = %s", [category["slug"]])
            category_id = cursor.fetchone()[0]
            category_ids[category["name"]] = category_id
            
            cursor.execute("""
                INSERT INTO products_category_translation (master_id, language_code, name, description)
                SELECT %s, %s, %s, %s
                WHERE NOT EXISTS (SELECT 1 FROM products_category_translation WHERE master_id = %s AND language_code = %s)
            """, [category_id, 'ru', category["name"], f"Товары категории {category['name']}", category_id, 'ru'])
        
        # Создаем продавца
        cursor.execute("""
            INSERT INTO products_seller (user_id, company_name, description, commission_rate, is_verified, rating, total_sales, total_revenue, created_at, updated_at)
            SELECT %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW()
            WHERE NOT EXISTS (SELECT 1 FROM products_seller WHERE company_name = %s)
        """, [user_id, "Интернет-магазин", "Онлайн магазин с широким ассортиментом", 5.0, True, 4.5, 0, 0.0, "Интернет-магазин"])
        
        cursor.execute("SELECT id FROM products_seller WHERE company_name = %s", ["Интернет-магазин"])
        seller_id = cursor.fetchone()[0]
        
        # Создаем товары
        products = [
            {"name": "iPhone 15 Pro Max 256GB", "price": 129990, "category": "Смартфоны"},
            {"name": "Samsung Galaxy S24 Ultra", "price": 119990, "category": "Смартфоны"},
            {"name": "Xiaomi 14 Pro", "price": 89990, "category": "Смартфоны"},
            {"name": "MacBook Pro 14 M3", "price": 199990, "category": "Ноутбуки"},
            {"name": "ASUS ROG Strix G15", "price": 89990, "category": "Ноутбуки"},
            {"name": "Lenovo ThinkPad X1", "price": 149990, "category": "Ноутбуки"},
            {"name": "Холодильник Samsung RB37K", "price": 45990, "category": "Бытовая техника"},
            {"name": "Стиральная машина LG F2J3", "price": 32990, "category": "Бытовая техника"},
            {"name": "Телевизор Samsung 55 QLED", "price": 79990, "category": "Бытовая техника"},
            {"name": "Куртка мужская зимняя", "price": 15990, "category": "Одежда"},
            {"name": "Джинсы мужские классические", "price": 4990, "category": "Одежда"},
            {"name": "Платье женское вечернее", "price": 8990, "category": "Одежда"},
            {"name": "Кроссовки Nike Air Max", "price": 12990, "category": "Обувь"},
            {"name": "Ботинки мужские кожаные", "price": 8990, "category": "Обувь"},
            {"name": "Туфли женские на каблуке", "price": 6990, "category": "Обувь"},
            {"name": "Гантели разборные 20кг", "price": 4990, "category": "Спорт"},
            {"name": "Коврик для йоги", "price": 1990, "category": "Спорт"},
            {"name": "Велосипед горный", "price": 25990, "category": "Спорт"},
            {"name": "Война и мир Л.Н. Толстой", "price": 890, "category": "Книги"},
            {"name": "Гарри Поттер и философский камень", "price": 1290, "category": "Книги"},
            {"name": "Диван угловой", "price": 45990, "category": "Мебель"},
            {"name": "Стол обеденный", "price": 19990, "category": "Мебель"},
            {"name": "Стул офисный", "price": 8990, "category": "Мебель"},
            {"name": "Крем для лица La Mer", "price": 45990, "category": "Красота"},
            {"name": "Парфюм Chanel №5", "price": 12990, "category": "Красота"},
            {"name": "Витамины Centrum", "price": 1990, "category": "Здоровье"},
            {"name": "Тонометр Omron M3", "price": 3990, "category": "Здоровье"},
            {"name": "Глюкометр", "price": 2990, "category": "Здоровье"},
        ]
        
        saved_count = 0
        
        for product_data in products:
            try:
                name = product_data['name']
                price = product_data['price']
                category_name = product_data['category']
                category_id = category_ids[category_name]
                sku = f"PROD-{fake.unique.random_number(digits=6)}"
                
                cursor.execute("""
                    INSERT INTO products_product (category_id, seller_id, currency, price, sku, stock_quantity, is_active, rating, reviews_count, views_count, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                    RETURNING id
                """, [category_id, seller_id, 'RUB', price, sku, random.randint(5, 100), True, round(random.uniform(4.0, 5.0), 2), random.randint(0, 50), random.randint(20, 300)])
                
                product_id = cursor.fetchone()[0]
                
                cursor.execute("""
                    INSERT INTO products_product_translation (master_id, language_code, name, description)
                    VALUES (%s, %s, %s, %s)
                """, [product_id, 'ru', name, f"Качественный товар {name}. Отличный выбор для ваших потребностей."])
                
                saved_count += 1
                print(f"✅ Сохранен товар: {name} - {price} ₽")
                
            except Exception as e:
                print(f"❌ Ошибка при сохранении товара: {e}")
        
        print(f"\n🎉 Сохранено {saved_count} товаров в базу данных!")

if __name__ == '__main__':
    create_products()

