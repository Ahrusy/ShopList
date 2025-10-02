#!/usr/bin/env python
"""
Быстрый скрипт для создания реальных товаров с использованием готовых данных
"""
import os
import django
import random
from faker import Faker

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shoplist.settings')
django.setup()

from products.models import Product, Category, Shop, Tag, Seller, ProductImage, ProductCharacteristic
from django.db import connection

fake = Faker('ru_RU')

# Реальные данные товаров
REAL_PRODUCTS = [
    # Электроника
    {"name": "iPhone 15 Pro Max 256GB", "price": 129990, "category": "Смартфоны", "description": "Новейший смартфон Apple с титановым корпусом и камерой 48 МП"},
    {"name": "Samsung Galaxy S24 Ultra", "price": 119990, "category": "Смартфоны", "description": "Флагманский смартфон Samsung с S Pen и камерой 200 МП"},
    {"name": "MacBook Pro 14 M3", "price": 199990, "category": "Ноутбуки", "description": "Профессиональный ноутбук Apple с чипом M3"},
    {"name": "ASUS ROG Strix G15", "price": 89990, "category": "Ноутбуки", "description": "Игровой ноутбук с RTX 4060 и процессором AMD Ryzen 7"},
    {"name": "Sony WH-1000XM5", "price": 29990, "category": "Наушники", "description": "Беспроводные наушники с активным шумоподавлением"},
    {"name": "AirPods Pro 2", "price": 19990, "category": "Наушники", "description": "Беспроводные наушники Apple с активным шумоподавлением"},
    
    # Одежда
    {"name": "Куртка мужская зимняя", "price": 15990, "category": "Одежда мужская", "description": "Теплая зимняя куртка из мембранной ткани"},
    {"name": "Джинсы мужские классические", "price": 4990, "category": "Одежда мужская", "description": "Классические джинсы из 100% хлопка"},
    {"name": "Платье женское вечернее", "price": 8990, "category": "Одежда женская", "description": "Элегантное вечернее платье из атласа"},
    {"name": "Блузка женская офисная", "price": 2990, "category": "Одежда женская", "description": "Стильная блузка для офиса из вискозы"},
    {"name": "Кроссовки Nike Air Max", "price": 12990, "category": "Обувь", "description": "Классические кроссовки Nike с технологией Air Max"},
    {"name": "Ботинки мужские кожаные", "price": 8990, "category": "Обувь", "description": "Качественные кожаные ботинки для офиса"},
    
    # Бытовая техника
    {"name": "Холодильник Samsung RB37K", "price": 45990, "category": "Бытовая техника", "description": "Двухкамерный холодильник с No Frost технологией"},
    {"name": "Стиральная машина LG F2J3", "price": 32990, "category": "Бытовая техника", "description": "Стиральная машина с загрузкой 6 кг и прямым приводом"},
    {"name": "Телевизор Samsung 55 QLED", "price": 79990, "category": "Бытовая техника", "description": "4K QLED телевизор с диагональю 55 дюймов"},
    {"name": "Пылесос Dyson V15", "price": 49990, "category": "Бытовая техника", "description": "Беспроводной пылесос с лазерной технологией обнаружения пыли"},
    
    # Красота и здоровье
    {"name": "Крем для лица La Mer", "price": 45990, "category": "Красота", "description": "Роскошный крем для лица с морскими водорослями"},
    {"name": "Парфюм Chanel №5", "price": 12990, "category": "Красота", "description": "Классический женский парфюм Chanel"},
    {"name": "Витамины Centrum", "price": 1990, "category": "Здоровье", "description": "Комплекс витаминов и минералов для взрослых"},
    {"name": "Тонометр Omron M3", "price": 3990, "category": "Здоровье", "description": "Автоматический тонометр для измерения давления"},
    
    # Спорт
    {"name": "Гантели разборные 20кг", "price": 4990, "category": "Спорт", "description": "Набор разборных гантелей для домашних тренировок"},
    {"name": "Коврик для йоги", "price": 1990, "category": "Спорт", "description": "Профессиональный коврик для йоги из натурального каучука"},
    {"name": "Велосипед горный", "price": 25990, "category": "Спорт", "description": "Горный велосипед с 21 передачей и амортизацией"},
    {"name": "Беговая дорожка", "price": 89990, "category": "Спорт", "description": "Электрическая беговая дорожка с наклоном и программами"},
    
    # Книги
    {"name": "Война и мир Л.Н. Толстой", "price": 890, "category": "Книги", "description": "Классический роман Льва Толстого в подарочном издании"},
    {"name": "Гарри Поттер и философский камень", "price": 1290, "category": "Книги", "description": "Первая книга серии о Гарри Поттере"},
    {"name": "Атлас мира", "price": 2990, "category": "Книги", "description": "Подробный атлас мира с картами всех континентов"},
    
    # Дом и сад
    {"name": "Диван угловой", "price": 45990, "category": "Мебель", "description": "Угловой диван с механизмом трансформации"},
    {"name": "Стол обеденный", "price": 19990, "category": "Мебель", "description": "Деревянный обеденный стол на 6 персон"},
    {"name": "Лампа настольная", "price": 2990, "category": "Освещение", "description": "LED лампа с регулировкой яркости и цветовой температуры"},
    {"name": "Горшок для цветов", "price": 890, "category": "Сад", "description": "Керамический горшок для комнатных растений"},
    
    # Автотовары
    {"name": "Автомагнитола Pioneer", "price": 8990, "category": "Автотовары", "description": "2DIN автомагнитола с Bluetooth и USB"},
    {"name": "Автомобильные коврики", "price": 1990, "category": "Автотовары", "description": "Резиновые коврики для салона автомобиля"},
    {"name": "Автошампунь", "price": 490, "category": "Автотовары", "description": "Профессиональный шампунь для мойки автомобиля"},
    
    # Зоотовары
    {"name": "Корм для собак Royal Canin", "price": 2990, "category": "Зоотовары", "description": "Сухой корм для взрослых собак крупных пород"},
    {"name": "Игрушка для кошек", "price": 490, "category": "Зоотовары", "description": "Интерактивная игрушка с кошачьей мятой"},
    {"name": "Аквариум 50л", "price": 4990, "category": "Зоотовары", "description": "Стеклянный аквариум с подсветкой и фильтром"},
    
    # Канцтовары
    {"name": "Ручка шариковая Parker", "price": 2990, "category": "Канцтовары", "description": "Премиальная шариковая ручка Parker"},
    {"name": "Блокнот Moleskine", "price": 1990, "category": "Канцтовары", "description": "Классический блокнот в твердом переплете"},
    {"name": "Папка для документов", "price": 490, "category": "Канцтовары", "description": "Папка-скоросшиватель на 4 кольца"},
    
    # Продукты питания
    {"name": "Кофе в зернах Lavazza", "price": 1290, "category": "Продукты", "description": "Итальянский кофе в зернах премиум класса"},
    {"name": "Чай Earl Grey", "price": 890, "category": "Продукты", "description": "Классический черный чай с бергамотом"},
    {"name": "Мед натуральный", "price": 1990, "category": "Продукты", "description": "Натуральный цветочный мед с пасеки"},
    
    # Ювелирные изделия
    {"name": "Кольцо золотое", "price": 25990, "category": "Украшения", "description": "Золотое кольцо с фианитом 585 пробы"},
    {"name": "Серьги серебряные", "price": 8990, "category": "Украшения", "description": "Серебряные серьги с жемчугом 925 пробы"},
    {"name": "Цепочка золотая", "price": 15990, "category": "Украшения", "description": "Золотая цепочка панцирного плетения 585 пробы"},
    
    # Часы
    {"name": "Часы Casio G-Shock", "price": 8990, "category": "Часы", "description": "Ударопрочные часы с множеством функций"},
    {"name": "Часы Apple Watch", "price": 29990, "category": "Часы", "description": "Умные часы Apple с GPS и мониторингом здоровья"},
    {"name": "Часы механические", "price": 19990, "category": "Часы", "description": "Классические механические часы с автоподзаводом"},
    
    # Сумки
    {"name": "Рюкзак туристический", "price": 4990, "category": "Сумки", "description": "Водонепроницаемый рюкзак для походов 40л"},
    {"name": "Сумка женская кожаная", "price": 8990, "category": "Сумки", "description": "Элегантная кожаная сумка через плечо"},
    {"name": "Портфель мужской", "price": 6990, "category": "Сумки", "description": "Деловой портфель из натуральной кожи"},
    
    # Аксессуары
    {"name": "Ремень кожаный", "price": 2990, "category": "Аксессуары", "description": "Кожаный ремень с металлической пряжкой"},
    {"name": "Шарф шерстяной", "price": 1990, "category": "Аксессуары", "description": "Теплый шерстяной шарф в клетку"},
    {"name": "Перчатки кожаные", "price": 2990, "category": "Аксессуары", "description": "Кожаные перчатки с подкладкой"},
    
    # Инструменты
    {"name": "Дрель аккумуляторная", "price": 4990, "category": "Инструменты", "description": "Аккумуляторная дрель-шуруповерт 18В"},
    {"name": "Набор отверток", "price": 1990, "category": "Инструменты", "description": "Набор из 20 отверток различных размеров"},
    {"name": "Молоток слесарный", "price": 890, "category": "Инструменты", "description": "Слесарный молоток с деревянной ручкой"},
    
    # Сантехника
    {"name": "Смеситель для кухни", "price": 4990, "category": "Сантехника", "description": "Смеситель с выдвижным изливом и фильтром"},
    {"name": "Унитаз подвесной", "price": 8990, "category": "Сантехника", "description": "Подвесной унитаз с системой двойного смыва"},
    {"name": "Ванна акриловая", "price": 25990, "category": "Сантехника", "description": "Акриловая ванна 170см с гидромассажем"},
    {"name": "Душевая кабина", "price": 45990, "category": "Сантехника", "description": "Угловая душевая кабина с тропическим душем"},
    
    # Строительные материалы
    {"name": "Краска акриловая", "price": 1990, "category": "Стройматериалы", "description": "Водоэмульсионная краска для внутренних работ"},
    {"name": "Обои флизелиновые", "price": 1290, "category": "Стройматериалы", "description": "Флизелиновые обои под покраску"},
    {"name": "Плитка керамическая", "price": 2990, "category": "Стройматериалы", "description": "Керамическая плитка для ванной комнаты"},
    
    # Текстиль
    {"name": "Постельное белье", "price": 2990, "category": "Текстиль", "description": "Комплект постельного белья из сатина"},
    {"name": "Полотенце банное", "price": 890, "category": "Текстиль", "description": "Банное полотенце из 100% хлопка"},
    {"name": "Шторы блэкаут", "price": 3990, "category": "Текстиль", "description": "Шторы с эффектом затемнения"},
    
    # Посуда
    {"name": "Набор кастрюль", "price": 8990, "category": "Посуда", "description": "Набор из 3 кастрюль с антипригарным покрытием"},
    {"name": "Тарелки керамические", "price": 1990, "category": "Посуда", "description": "Набор из 6 керамических тарелок"},
    {"name": "Столовые приборы", "price": 2990, "category": "Посуда", "description": "Набор столовых приборов из нержавеющей стали"},
]

def create_categories():
    """Создание категорий"""
    print("📂 Создаем категории...")
    
    with connection.cursor() as cursor:
        categories_created = 0
        
        # Получаем уникальные категории из товаров
        unique_categories = list(set([product['category'] for product in REAL_PRODUCTS]))
        
        for category_name in unique_categories:
            slug = category_name.lower().replace(' ', '-').replace('ё', 'e')
            
            # Создаем категорию
            cursor.execute("""
                INSERT INTO products_category (slug, icon, is_active, created_at, updated_at)
                SELECT %s, %s, %s, NOW(), NOW()
                WHERE NOT EXISTS (SELECT 1 FROM products_category WHERE slug = %s)
            """, [slug, "tag", True, slug])
            
            cursor.execute("SELECT id FROM products_category WHERE slug = %s", [slug])
            category_id = cursor.fetchone()[0]
            
            # Создаем перевод категории
            cursor.execute("""
                INSERT INTO products_category_translation (master_id, language_code, name, description)
                SELECT %s, %s, %s, %s
                WHERE NOT EXISTS (SELECT 1 FROM products_category_translation WHERE master_id = %s AND language_code = %s)
            """, [category_id, 'ru', category_name, f"Товары категории {category_name}", category_id, 'ru'])
            
            categories_created += 1
        
        print(f"✅ Создано {categories_created} категорий")
        return categories_created

def create_seller_and_shop():
    """Создание продавца и магазина"""
    print("🏪 Создаем продавца и магазин...")
    
    with connection.cursor() as cursor:
        # Создаем пользователя для продавца
        cursor.execute("""
            INSERT INTO products_user (username, email, password, first_name, last_name, is_staff, is_active, is_superuser, role, date_joined)
            SELECT %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW()
            WHERE NOT EXISTS (SELECT 1 FROM products_user WHERE username = %s)
        """, ["seller", "seller@shop.ru", "pbkdf2_sha256$600000$dummy$dummy", "Продавец", "Магазин", False, True, False, "seller", "seller"])
        
        cursor.execute("SELECT id FROM products_user WHERE username = %s", ["seller"])
        user_id = cursor.fetchone()[0]
        
        # Создаем продавца
        cursor.execute("""
            INSERT INTO products_seller (user_id, company_name, description, commission_rate, is_verified, rating, total_sales, total_revenue, created_at, updated_at)
            SELECT %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW()
            WHERE NOT EXISTS (SELECT 1 FROM products_seller WHERE company_name = %s)
        """, [user_id, "Интернет-магазин", "Онлайн магазин с широким ассортиментом товаров", 5.0, True, 4.5, 0, 0.0, "Интернет-магазин"])
        
        cursor.execute("SELECT id FROM products_seller WHERE company_name = %s", ["Интернет-магазин"])
        seller_id = cursor.fetchone()[0]
        
        # Создаем магазин
        cursor.execute("""
            INSERT INTO products_shop (phone, email, is_active, created_at, updated_at)
            SELECT %s, %s, %s, NOW(), NOW()
            WHERE NOT EXISTS (SELECT 1 FROM products_shop WHERE phone = %s)
        """, ["+7 (495) 123-45-67", "info@shop.ru", True, "+7 (495) 123-45-67"])
        
        cursor.execute("SELECT id FROM products_shop WHERE phone = %s", ["+7 (495) 123-45-67"])
        shop_id = cursor.fetchone()[0]
        
        cursor.execute("""
            INSERT INTO products_shop_translation (master_id, language_code, name, address, city)
            SELECT %s, %s, %s, %s, %s
            WHERE NOT EXISTS (SELECT 1 FROM products_shop_translation WHERE master_id = %s AND language_code = %s)
        """, [shop_id, 'ru', "Главный магазин", "Москва, ул. Тверская, 1", "Москва", shop_id, 'ru'])
        
        print("✅ Создан продавец и магазин")
        return seller_id, shop_id

def create_products():
    """Создание товаров"""
    print("📦 Создаем товары...")
    
    with connection.cursor() as cursor:
        # Получаем ID продавца и магазина
        cursor.execute("SELECT id FROM products_seller WHERE company_name = %s", ["Интернет-магазин"])
        seller_id = cursor.fetchone()[0]
        
        cursor.execute("SELECT id FROM products_shop WHERE phone = %s", ["+7 (495) 123-45-67"])
        shop_id = cursor.fetchone()[0]
        
        products_created = 0
        
        for product_data in REAL_PRODUCTS:
            try:
                # Получаем ID категории
                category_name = product_data['category']
                slug = category_name.lower().replace(' ', '-').replace('ё', 'e')
                cursor.execute("SELECT id FROM products_category WHERE slug = %s", [slug])
                category_id = cursor.fetchone()[0]
                
                # Создаем товар
                name = product_data['name']
                price = product_data['price']
                description = product_data['description']
                sku = f"PROD-{fake.unique.random_number(digits=6)}"
                
                cursor.execute("""
                    INSERT INTO products_product (category_id, seller_id, currency, price, sku, stock_quantity, is_active, rating, reviews_count, views_count, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                    RETURNING id
                """, [category_id, seller_id, 'RUB', price, sku, random.randint(5, 100), True, round(random.uniform(4.0, 5.0), 2), random.randint(0, 50), random.randint(20, 300)])
                
                product_id = cursor.fetchone()[0]
                
                # Создаем перевод товара
                cursor.execute("""
                    INSERT INTO products_product_translation (master_id, language_code, name, description)
                    VALUES (%s, %s, %s, %s)
                """, [product_id, 'ru', name, description])
                
                # Создаем характеристики
                characteristics = [
                    ("Бренд", "Официальный поставщик"),
                    ("Страна производства", "Россия"),
                    ("Гарантия", "12 месяцев"),
                    ("Доставка", "По всей России"),
                    ("Оплата", "Наличные, карта, рассрочка"),
                ]
                
                for i, (char_name, char_value) in enumerate(characteristics):
                    cursor.execute("""
                        INSERT INTO products_productcharacteristic (product_id, name, value, unit, "order")
                        VALUES (%s, %s, %s, %s, %s)
                    """, [product_id, char_name, char_value, "шт", i + 1])
                
                # Связь с магазином не создаем, так как таблица products_product_shops не существует
                
                products_created += 1
                print(f"✅ Создан товар: {name} - {price} ₽")
                
            except Exception as e:
                print(f"❌ Ошибка при создании товара {product_data['name']}: {e}")
        
        print(f"\n🎉 Создано {products_created} товаров!")
        return products_created

def main():
    """Основная функция"""
    print("🚀 Создаем реальные товары...")
    
    # Создаем категории
    create_categories()
    
    # Создаем продавца и магазин
    create_seller_and_shop()
    
    # Создаем товары
    create_products()
    
    print("\n✅ Все товары успешно созданы!")

if __name__ == '__main__':
    main()
