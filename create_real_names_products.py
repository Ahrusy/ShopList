#!/usr/bin/env python
"""
Скрипт для создания товаров с реальными названиями
"""
import os
import django
from decimal import Decimal
import random
from faker import Faker

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
                    INSERT INTO products_category (slug, icon, is_active, created_at, updated_at)
                    SELECT %s, %s, %s, NOW(), NOW()
                    WHERE NOT EXISTS (SELECT 1 FROM products_category WHERE slug = %s)
                """, [category_slug, 'tag', True, category_slug])
                
                # Получаем ID категории
                cursor.execute("SELECT id FROM products_category WHERE slug = %s", [category_slug])
                category_id = cursor.fetchone()[0]
                
                # Создаем перевод категории
                cursor.execute("""
                    INSERT INTO products_category_translation (master_id, language_code, name, description)
                    SELECT %s, %s, %s, %s
                    WHERE NOT EXISTS (SELECT 1 FROM products_category_translation WHERE master_id = %s AND language_code = %s)
                """, [category_id, 'ru', product_data['category'], f'Категория {product_data["category"]}', category_id, 'ru'])
                
                # Создаем продавца
                cursor.execute("""
                    INSERT INTO products_seller (company_name, description, created_at, updated_at)
                    SELECT %s, %s, NOW(), NOW()
                    WHERE NOT EXISTS (SELECT 1 FROM products_seller WHERE company_name = %s)
                """, ["OZON Marketplace", "Официальный маркетплейс OZON", "OZON Marketplace"])
                
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
                        INSERT INTO products_productcharacteristic (product_id, name, value, unit)
                        VALUES (%s, %s, %s, %s)
                    """, [product_id, char_name, char_value, "шт"])
                
                # Создаем магазин
                cursor.execute("""
                    INSERT INTO products_shop (phone, email, created_at, updated_at)
                    SELECT %s, %s, NOW(), NOW()
                    WHERE NOT EXISTS (SELECT 1 FROM products_shop WHERE phone = %s)
                """, ["+7 (495) 232-32-32", "store@ozon.ru", "+7 (495) 232-32-32"])
                
                # Получаем ID магазина
                cursor.execute("SELECT id FROM products_shop WHERE phone = %s", ["+7 (495) 232-32-32"])
                shop_id = cursor.fetchone()[0]
                
                # Создаем перевод магазина
                cursor.execute("""
                    INSERT INTO products_shop_translation (master_id, language_code, name, address, city)
                    SELECT %s, %s, %s, %s, %s
                    WHERE NOT EXISTS (SELECT 1 FROM products_shop_translation WHERE master_id = %s AND language_code = %s)
                """, [shop_id, 'ru', "OZON Store", "Москва, ул. Льва Толстого, 16", "Москва", shop_id, 'ru'])
                
                # Связываем товар с магазином
                cursor.execute("""
                    INSERT INTO products_product_shops (product_id, shop_id)
                    SELECT %s, %s
                    WHERE NOT EXISTS (SELECT 1 FROM products_product_shops WHERE product_id = %s AND shop_id = %s)
                """, [product_id, shop_id, product_id, shop_id])
                
                products_created += 1
                print(f"✅ Создан товар: {product_data['name']} - {price} ₽")
                
            except Exception as e:
                print(f"❌ Ошибка при создании товара {product_data['name']}: {e}")
        
        print(f"\n🎉 Готово! Создано {products_created} реальных товаров!")
        return products_created

if __name__ == '__main__':
    create_real_products_with_sql()
