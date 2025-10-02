#!/usr/bin/env python
"""
Упрощенный скрипт для создания реальных товаров без Django Parler проблем
"""
import os
import django
from decimal import Decimal
import random
from faker import Faker
import requests
from io import BytesIO
from PIL import Image

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shoplist.settings')
django.setup()

from products.models import Product, Category, Shop, Tag, Seller, ProductImage, ProductCharacteristic
from django.db import connection

fake = Faker('ru_RU')

# Реальные товары с настоящими названиями
REAL_PRODUCTS = [
    {"name": "iPhone 15 Pro Max 256GB", "category": "Смартфоны", "price": 119990, "description": "Новейший iPhone с титановым корпусом, камерой 48 МП и чипом A17 Pro"},
    {"name": "Samsung Galaxy S24 Ultra", "category": "Смартфоны", "price": 99990, "description": "Флагманский смартфон Samsung с S Pen и камерой 200 МП"},
    {"name": "MacBook Air M3 13\"", "category": "Ноутбуки", "price": 129990, "description": "Ультратонкий ноутбук Apple с чипом M3 и дисплеем Liquid Retina"},
    {"name": "Dell XPS 13", "category": "Ноутбуки", "price": 89990, "description": "Премиальный ноутбук Dell с безрамочным дисплеем и процессором Intel Core i7"},
    {"name": "iPad Pro 12.9\" M2", "category": "Планшеты", "price": 79990, "description": "Профессиональный планшет Apple с дисплеем Liquid Retina XDR"},
    {"name": "Sony WH-1000XM5", "category": "Наушники", "price": 29990, "description": "Беспроводные наушники Sony с активным шумоподавлением"},
    {"name": "AirPods Pro 2", "category": "Наушники", "price": 19990, "description": "Беспроводные наушники Apple с активным шумоподавлением и пространственным звуком"},
    {"name": "PlayStation 5", "category": "Игровые консоли", "price": 49990, "description": "Игровая консоль Sony PlayStation 5 с SSD накопителем"},
    {"name": "Xbox Series X", "category": "Игровые консоли", "price": 45990, "description": "Игровая консоль Microsoft Xbox Series X с поддержкой 4K"},
    {"name": "Nintendo Switch OLED", "category": "Игровые консоли", "price": 29990, "description": "Гибридная игровая консоль Nintendo с OLED дисплеем"},
    {"name": "Джинсы Levi's 501", "category": "Джинсы", "price": 5990, "description": "Классические джинсы Levi's 501 из денима премиум качества"},
    {"name": "Кроссовки Nike Air Max 270", "category": "Обувь", "price": 12990, "description": "Спортивные кроссовки Nike с технологией Air Max"},
    {"name": "Куртка The North Face", "category": "Верхняя одежда", "price": 15990, "description": "Зимняя куртка The North Face с мембраной Gore-Tex"},
    {"name": "Рубашка Ralph Lauren", "category": "Рубашки", "price": 7990, "description": "Классическая рубашка Ralph Lauren из хлопка премиум качества"},
    {"name": "Платье Zara", "category": "Платья", "price": 3990, "description": "Элегантное платье Zara для особых случаев"},
    {"name": "Свитер Uniqlo", "category": "Свитеры", "price": 2990, "description": "Теплый свитер Uniqlo из мериносовой шерсти"},
    {"name": "Ботинки Timberland", "category": "Обувь", "price": 11990, "description": "Классические ботинки Timberland из натуральной кожи"},
    {"name": "Шорты Adidas", "category": "Шорты", "price": 1990, "description": "Спортивные шорты Adidas с технологией ClimaLite"},
    {"name": "Кофемашина De'Longhi", "category": "Кухонная техника", "price": 24990, "description": "Автоматическая кофемашина De'Longhi с капучинатором"},
    {"name": "Пылесос Dyson V15", "category": "Бытовая техника", "price": 39990, "description": "Беспроводной пылесос Dyson V15 с лазерной технологией"},
    {"name": "Холодильник Samsung", "category": "Крупная техника", "price": 89990, "description": "Двухкамерный холодильник Samsung с технологией No Frost"},
    {"name": "Стиральная машина LG", "category": "Крупная техника", "price": 49990, "description": "Стиральная машина LG с загрузкой 7 кг и технологией Direct Drive"},
    {"name": "Микроволновка Panasonic", "category": "Кухонная техника", "price": 8990, "description": "Микроволновая печь Panasonic с функцией гриль"},
    {"name": "Блендер Philips", "category": "Кухонная техника", "price": 5990, "description": "Мощный блендер Philips для приготовления смузи и коктейлей"},
    {"name": "Утюг Tefal", "category": "Бытовая техника", "price": 3990, "description": "Паровой утюг Tefal с технологией самоочистки"},
    {"name": "Фен Dyson Supersonic", "category": "Красота и здоровье", "price": 29990, "description": "Фен Dyson Supersonic с технологией цифрового двигателя"},
    {"name": "Гантели 20кг", "category": "Спортивные товары", "price": 4990, "description": "Разборные гантели 20кг для домашних тренировок"},
    {"name": "Беговая дорожка NordicTrack", "category": "Кардио тренажеры", "price": 79990, "description": "Электрическая беговая дорожка NordicTrack с наклоном"},
    {"name": "Велосипед Trek", "category": "Велосипеды", "price": 59990, "description": "Горный велосипед Trek с алюминиевой рамой"},
    {"name": "Йога-мат Liforme", "category": "Йога и фитнес", "price": 3990, "description": "Профессиональный йога-мат Liforme с анатомическими линиями"},
    {"name": "Кроссовки Adidas Ultraboost", "category": "Спортивная обувь", "price": 14990, "description": "Беговые кроссовки Adidas Ultraboost с технологией Boost"},
    {"name": "Спортивный костюм Nike", "category": "Спортивная одежда", "price": 7990, "description": "Спортивный костюм Nike из дышащей ткани Dri-FIT"},
    {"name": "Гиря 16кг", "category": "Спортивные товары", "price": 2990, "description": "Чугунная гиря 16кг для силовых тренировок"},
    {"name": "Скакалка Adidas", "category": "Спортивные товары", "price": 990, "description": "Скоростная скакалка Adidas с регулируемой длиной"},
    {"name": "Гарри Поттер и Философский камень", "category": "Художественная литература", "price": 890, "description": "Первая книга о Гарри Поттере от Дж.К. Роулинг"},
    {"name": "1984 Джордж Оруэлл", "category": "Художественная литература", "price": 590, "description": "Классический роман-антиутопия Джорджа Оруэлла"},
    {"name": "Атлас анатомии человека", "category": "Медицинская литература", "price": 2990, "description": "Подробный атлас анатомии человека для студентов-медиков"},
    {"name": "Python для начинающих", "category": "Программирование", "price": 1990, "description": "Учебник по программированию на Python для новичков"},
    {"name": "Кулинарная книга Джейми Оливера", "category": "Кулинария", "price": 1490, "description": "Сборник рецептов от знаменитого шеф-повара Джейми Оливера"},
    {"name": "Энциклопедия животных", "category": "Детская литература", "price": 1990, "description": "Красочная энциклопедия животных для детей"},
    {"name": "История России", "category": "История", "price": 1290, "description": "Учебник по истории России для школьников"},
    {"name": "Словарь английского языка", "category": "Словари", "price": 890, "description": "Толковый словарь английского языка Oxford"},
]

# Реальные URL изображений товаров
REAL_IMAGE_URLS = [
    "https://images.unsplash.com/photo-1592750475338-74b7b21085ab?w=400&h=400&fit=crop",  # iPhone
    "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=400&h=400&fit=crop",  # Samsung
    "https://images.unsplash.com/photo-1541807084-5c52b6b3adef?w=400&h=400&fit=crop",  # MacBook
    "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=400&h=400&fit=crop",  # Laptop
    "https://images.unsplash.com/photo-1561154464-82e9adf32764?w=400&h=400&fit=crop",  # iPad
    "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400&h=400&fit=crop",  # Headphones
    "https://images.unsplash.com/photo-1606220945770-b5b6c2c55bf1?w=400&h=400&fit=crop",  # AirPods
    "https://images.unsplash.com/photo-1606813907291-d86efa9b94db?w=400&h=400&fit=crop",  # PlayStation
    "https://images.unsplash.com/photo-1621259182978-fbf93132d53d?w=400&h=400&fit=crop",  # Xbox
    "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=400&h=400&fit=crop",  # Nintendo
    "https://images.unsplash.com/photo-1542272604-787c3835535d?w=400&h=400&fit=crop",  # Jeans
    "https://images.unsplash.com/photo-1549298916-b41d501d3772?w=400&h=400&fit=crop",  # Sneakers
    "https://images.unsplash.com/photo-1551028719-00167b16eac5?w=400&h=400&fit=crop",  # Jacket
    "https://images.unsplash.com/photo-1596755094514-f87e34085b2c?w=400&h=400&fit=crop",  # Shirt
    "https://images.unsplash.com/photo-1594633312681-425c7b97ccd1?w=400&h=400&fit=crop",  # Dress
    "https://images.unsplash.com/photo-1434389677669-e08b4cac3105?w=400&h=400&fit=crop",  # Sweater
    "https://images.unsplash.com/photo-1544966503-7cc5ac882d5f?w=400&h=400&fit=crop",  # Boots
    "https://images.unsplash.com/photo-1594633312681-425c7b97ccd1?w=400&h=400&fit=crop",  # Shorts
    "https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?w=400&h=400&fit=crop",  # Coffee machine
    "https://images.unsplash.com/photo-1558618047-3c8c76ca7d13?w=400&h=400&fit=crop",  # Vacuum
    "https://images.unsplash.com/photo-1571175443880-49e1d25b2bc5?w=400&h=400&fit=crop",  # Refrigerator
    "https://images.unsplash.com/photo-1558618047-3c8c76ca7d13?w=400&h=400&fit=crop",  # Washing machine
    "https://images.unsplash.com/photo-1574269909862-7e1d70bb8078?w=400&h=400&fit=crop",  # Microwave
    "https://images.unsplash.com/photo-1585515656519-7b3b1b0b0b0b?w=400&h=400&fit=crop",  # Blender
    "https://images.unsplash.com/photo-1585515656519-7b3b1b0b0b0b?w=400&h=400&fit=crop",  # Iron
    "https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?w=400&h=400&fit=crop",  # Hair dryer
    "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=400&h=400&fit=crop",  # Dumbbells
    "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=400&h=400&fit=crop",  # Treadmill
    "https://images.unsplash.com/photo-1558618047-3c8c76ca7d13?w=400&h=400&fit=crop",  # Bicycle
    "https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?w=400&h=400&fit=crop",  # Yoga mat
    "https://images.unsplash.com/photo-1549298916-b41d501d3772?w=400&h=400&fit=crop",  # Running shoes
    "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=400&h=400&fit=crop",  # Sportswear
    "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=400&h=400&fit=crop",  # Kettlebell
    "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=400&h=400&fit=crop",  # Jump rope
    "https://images.unsplash.com/photo-1544947950-fa07a98d237f?w=400&h=400&fit=crop",  # Books
]

def create_real_products_with_sql():
    """Создание реальных товаров через raw SQL"""
    print("🚀 Начинаем создание реальных товаров через SQL...")
    
    with connection.cursor() as cursor:
        products_created = 0
        
        for i, product_data in enumerate(REAL_PRODUCTS):
            try:
                # Создаем категорию через SQL
                category_slug = product_data['category'].lower().replace(' ', '-').replace('ё', 'e')
                cursor.execute("""
                    INSERT INTO products_category (slug, icon, created_at, updated_at)
                    VALUES (%s, %s, NOW(), NOW())
                    ON CONFLICT (slug) DO NOTHING
                """, [category_slug, 'tag'])
                
                # Получаем ID категории
                cursor.execute("SELECT id FROM products_category WHERE slug = %s", [category_slug])
                category_id = cursor.fetchone()[0]
                
                # Создаем перевод категории
                cursor.execute("""
                    INSERT INTO products_category_translation (master_id, language_code, name, description)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (master_id, language_code) DO NOTHING
                """, [category_id, 'ru', product_data['category'], f'Категория {product_data["category"]}'])
                
                # Создаем продавца
                cursor.execute("""
                    INSERT INTO products_seller (company_name, description, created_at, updated_at)
                    VALUES (%s, %s, NOW(), NOW())
                    ON CONFLICT (company_name) DO NOTHING
                """, ["OZON Marketplace", "Официальный маркетплейс OZON"])
                
                # Получаем ID продавца
                cursor.execute("SELECT id FROM products_seller WHERE company_name = %s", ["OZON Marketplace"])
                seller_id = cursor.fetchone()[0]
                
                # Создаем товар
                sku = f"OZON-{fake.unique.random_number(digits=6)}"
                price = product_data['price']
                discount_price = int(price * 0.8) if random.random() < 0.3 else None
                
                cursor.execute("""
                    INSERT INTO products_product (category_id, seller_id, currency, price, discount_price, sku, stock_quantity, is_active, rating, reviews_count, views_count, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                    RETURNING id
                """, [category_id, seller_id, 'RUB', price, discount_price, sku, random.randint(10, 100), True, round(random.uniform(4.0, 5.0), 2), random.randint(5, 150), random.randint(100, 1000)])
                
                product_id = cursor.fetchone()[0]
                
                # Создаем перевод товара
                cursor.execute("""
                    INSERT INTO products_product_translation (master_id, language_code, name, description)
                    VALUES (%s, %s, %s, %s)
                """, [product_id, 'ru', product_data['name'], product_data['description']])
                
                # Создаем характеристики
                characteristics = [
                    ("Бренд", product_data['name'].split()[0]),
                    ("Страна", random.choice(["Россия", "Китай", "Германия", "Япония", "США", "Южная Корея"])),
                    ("Гарантия", random.choice(["6 месяцев", "1 год", "2 года", "3 года"])),
                    ("Вес", f"{random.randint(100, 5000)} г"),
                    ("Цвет", random.choice(["Черный", "Белый", "Серый", "Красный", "Синий", "Зеленый"])),
                ]
                
                for char_name, char_value in characteristics:
                    cursor.execute("""
                        INSERT INTO products_productcharacteristic (product_id, name, value, created_at, updated_at)
                        VALUES (%s, %s, %s, NOW(), NOW())
                    """, [product_id, char_name, char_value])
                
                # Создаем магазин
                cursor.execute("""
                    INSERT INTO products_shop (phone, email, created_at, updated_at)
                    VALUES (%s, %s, NOW(), NOW())
                    ON CONFLICT (phone) DO NOTHING
                """, ["+7 (495) 232-32-32", "store@ozon.ru"])
                
                # Получаем ID магазина
                cursor.execute("SELECT id FROM products_shop WHERE phone = %s", ["+7 (495) 232-32-32"])
                shop_id = cursor.fetchone()[0]
                
                # Создаем перевод магазина
                cursor.execute("""
                    INSERT INTO products_shop_translation (master_id, language_code, name, address, city)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (master_id, language_code) DO NOTHING
                """, [shop_id, 'ru', "OZON Store", "Москва, ул. Льва Толстого, 16", "Москва"])
                
                # Связываем товар с магазином
                cursor.execute("""
                    INSERT INTO products_product_shops (product_id, shop_id)
                    VALUES (%s, %s)
                    ON CONFLICT DO NOTHING
                """, [product_id, shop_id])
                
                products_created += 1
                print(f"✅ Создан товар: {product_data['name']} - {price} ₽")
                
            except Exception as e:
                print(f"❌ Ошибка при создании товара {product_data['name']}: {e}")
        
        print(f"\n🎉 Готово! Создано {products_created} реальных товаров!")
        return products_created

def download_and_add_images():
    """Загрузка и добавление изображений к товарам"""
    print("🖼️ Начинаем загрузку изображений...")
    
    with connection.cursor() as cursor:
        # Получаем все товары
        cursor.execute("SELECT id, name FROM products_product_translation WHERE language_code = 'ru'")
        products = cursor.fetchall()
        
        images_added = 0
        
        for i, (product_id, product_name) in enumerate(products):
            try:
                # Выбираем изображение
                image_url = REAL_IMAGE_URLS[i % len(REAL_IMAGE_URLS)]
                
                # Загружаем изображение
                response = requests.get(image_url, timeout=10)
                response.raise_for_status()
                
                # Сохраняем изображение
                image_name = f"product_{product_id}_{fake.uuid4()}.jpg"
                image_path = f"media/products/{image_name}"
                
                # Создаем директорию если не существует
                os.makedirs("media/products", exist_ok=True)
                
                with open(image_path, 'wb') as f:
                    f.write(response.content)
                
                # Добавляем запись в базу данных
                cursor.execute("""
                    INSERT INTO products_productimage (product_id, image, created_at, updated_at)
                    VALUES (%s, %s, NOW(), NOW())
                """, [product_id, f"products/{image_name}"])
                
                images_added += 1
                print(f"✅ Добавлено изображение для: {product_name}")
                
            except Exception as e:
                print(f"❌ Ошибка при загрузке изображения для {product_name}: {e}")
        
        print(f"\n🖼️ Готово! Добавлено {images_added} изображений!")
        return images_added

if __name__ == '__main__':
    create_real_products_with_sql()
    download_and_add_images()

