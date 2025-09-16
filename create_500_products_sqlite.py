#!/usr/bin/env python
"""
Изолированный скрипт для создания 500 товаров
Использует только SQLite без Django ORM
"""
import sqlite3
import random
import logging
from decimal import Decimal
from datetime import datetime

# Настройка логгера
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('create_500_products_sqlite.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

logger.info("=== СОЗДАНИЕ 500 ТОВАРОВ ===")

# Реальные данные товаров
REAL_PRODUCTS_DATA = [
    {
        "name": "iPhone 15 Pro Max 256GB Natural Titanium",
        "description": "Новейший смартфон Apple с титановым корпусом, чипом A17 Pro и камерой 48 МП. Поддержка 5G, Face ID, беспроводная зарядка. Дисплей Super Retina XDR 6.7 дюйма с технологией ProMotion.",
        "price": 99990.00,
        "category": "Смартфоны",
        "characteristics": [
            {"name": "Диагональ экрана", "value": "6.7", "unit": "дюйма"},
            {"name": "Разрешение экрана", "value": "2796x1290", "unit": "пикселей"},
            {"name": "Процессор", "value": "Apple A17 Pro"},
            {"name": "Объем памяти", "value": "256", "unit": "ГБ"},
            {"name": "Оперативная память", "value": "8", "unit": "ГБ"},
            {"name": "Основная камера", "value": "48", "unit": "МП"},
            {"name": "Фронтальная камера", "value": "12", "unit": "МП"},
            {"name": "Аккумулятор", "value": "4422", "unit": "мАч"},
            {"name": "Операционная система", "value": "iOS 17"},
            {"name": "Материал корпуса", "value": "Титан"},
            {"name": "Цвет", "value": "Натуральный титан"},
            {"name": "Водозащита", "value": "IP68"},
            {"name": "Беспроводная зарядка", "value": "Да"},
            {"name": "5G", "value": "Да"},
            {"name": "Face ID", "value": "Да"}
        ]
    },
    {
        "name": "Samsung Galaxy S24 Ultra 512GB Titanium Black",
        "description": "Флагманский смартфон Samsung с S Pen, камерой 200 МП и экраном Dynamic AMOLED 2X. Искусственный интеллект Galaxy AI. Процессор Snapdragon 8 Gen 3 для Galaxy.",
        "price": 119990.00,
        "category": "Смартфоны",
        "characteristics": [
            {"name": "Диагональ экрана", "value": "6.8", "unit": "дюйма"},
            {"name": "Разрешение экрана", "value": "3120x1440", "unit": "пикселей"},
            {"name": "Процессор", "value": "Snapdragon 8 Gen 3"},
            {"name": "Объем памяти", "value": "512", "unit": "ГБ"},
            {"name": "Оперативная память", "value": "12", "unit": "ГБ"},
            {"name": "Основная камера", "value": "200", "unit": "МП"},
            {"name": "Фронтальная камера", "value": "12", "unit": "МП"},
            {"name": "Аккумулятор", "value": "5000", "unit": "мАч"},
            {"name": "Операционная система", "value": "Android 14"},
            {"name": "Материал корпуса", "value": "Титан"},
            {"name": "Цвет", "value": "Титан черный"},
            {"name": "S Pen", "value": "Да"},
            {"name": "Водозащита", "value": "IP68"},
            {"name": "Беспроводная зарядка", "value": "Да"},
            {"name": "5G", "value": "Да"}
        ]
    },
    {
        "name": "MacBook Pro 16 M3 Max 1TB Space Gray",
        "description": "Профессиональный ноутбук Apple с чипом M3 Max, дисплеем Liquid Retina XDR и до 22 часов работы от батареи. Идеален для профессиональной работы с видео, графикой и разработки.",
        "price": 299990.00,
        "category": "Ноутбуки",
        "characteristics": [
            {"name": "Диагональ экрана", "value": "16.2", "unit": "дюйма"},
            {"name": "Разрешение экрана", "value": "3456x2234", "unit": "пикселей"},
            {"name": "Процессор", "value": "Apple M3 Max"},
            {"name": "Объем памяти", "value": "1", "unit": "ТБ SSD"},
            {"name": "Оперативная память", "value": "32", "unit": "ГБ"},
            {"name": "Графический процессор", "value": "40-ядерный GPU"},
            {"name": "Время работы от батареи", "value": "22", "unit": "часов"},
            {"name": "Операционная система", "value": "macOS Sonoma"},
            {"name": "Материал корпуса", "value": "Алюминий"},
            {"name": "Цвет", "value": "Серый космос"},
            {"name": "Вес", "value": "2.16", "unit": "кг"},
            {"name": "Порты", "value": "3x Thunderbolt 4, HDMI, SDXC"},
            {"name": "Wi-Fi", "value": "Wi-Fi 6E"},
            {"name": "Bluetooth", "value": "5.3"}
        ]
    },
    {
        "name": "Sony BRAVIA XR-65A95L 65 OLED 4K Smart TV",
        "description": "OLED телевизор Sony с процессором Cognitive Processor XR, технологией XR OLED Contrast Pro и поддержкой Dolby Vision. Идеальное качество изображения и звука.",
        "price": 199990.00,
        "category": "Телевизоры",
        "characteristics": [
            {"name": "Диагональ экрана", "value": "65", "unit": "дюймов"},
            {"name": "Разрешение экрана", "value": "4K UHD", "unit": "3840x2160"},
            {"name": "Технология экрана", "value": "OLED"},
            {"name": "Процессор", "value": "Cognitive Processor XR"},
            {"name": "HDR", "value": "Dolby Vision, HDR10, HLG"},
            {"name": "Частота обновления", "value": "120", "unit": "Гц"},
            {"name": "Операционная система", "value": "Google TV"},
            {"name": "Поддержка Wi-Fi", "value": "Wi-Fi 6E"},
            {"name": "Порты", "value": "4x HDMI 2.1, 2x USB"},
            {"name": "Цвет", "value": "Черный"},
            {"name": "Вес", "value": "28.5", "unit": "кг"},
            {"name": "Размеры", "value": "144.7x83.1x3.2", "unit": "см"},
            {"name": "Звук", "value": "Acoustic Surface Audio+"},
            {"name": "Smart TV", "value": "Да"}
        ]
    },
    {
        "name": "iPad Pro 12.9 M2 256GB Space Gray",
        "description": "Профессиональный планшет Apple с чипом M2, дисплеем Liquid Retina XDR и поддержкой Apple Pencil 2-го поколения. Идеален для творчества и профессиональной работы.",
        "price": 89990.00,
        "category": "Планшеты",
        "characteristics": [
            {"name": "Диагональ экрана", "value": "12.9", "unit": "дюйма"},
            {"name": "Разрешение экрана", "value": "2732x2048", "unit": "пикселей"},
            {"name": "Процессор", "value": "Apple M2"},
            {"name": "Объем памяти", "value": "256", "unit": "ГБ"},
            {"name": "Оперативная память", "value": "8", "unit": "ГБ"},
            {"name": "Камера", "value": "12 МП + 10 МП"},
            {"name": "Фронтальная камера", "value": "12", "unit": "МП"},
            {"name": "Аккумулятор", "value": "10", "unit": "часов"},
            {"name": "Операционная система", "value": "iPadOS 16"},
            {"name": "Материал корпуса", "value": "Алюминий"},
            {"name": "Цвет", "value": "Серый космос"},
            {"name": "Вес", "value": "682", "unit": "г"},
            {"name": "Apple Pencil", "value": "Поддержка 2-го поколения"},
            {"name": "Magic Keyboard", "value": "Поддержка"}
        ]
    }
]

# Шаблоны для генерации дополнительных товаров
PRODUCT_TEMPLATES = {
    "Смартфоны": [
        {"name": "OnePlus 12", "base_price": 59990, "brand": "OnePlus"},
        {"name": "Google Pixel 8", "base_price": 79990, "brand": "Google"},
        {"name": "Huawei P60 Pro", "base_price": 89990, "brand": "Huawei"},
        {"name": "Nothing Phone 2", "base_price": 39990, "brand": "Nothing"},
        {"name": "Realme GT 5", "base_price": 34990, "brand": "Realme"},
        {"name": "Vivo X100 Pro", "base_price": 69990, "brand": "Vivo"},
        {"name": "Oppo Find X6", "base_price": 79990, "brand": "Oppo"},
    ],
    "Ноутбуки": [
        {"name": "Dell XPS 15", "base_price": 199990, "brand": "Dell"},
        {"name": "HP Spectre x360", "base_price": 179990, "brand": "HP"},
        {"name": "Lenovo ThinkPad X1", "base_price": 249990, "brand": "Lenovo"},
        {"name": "MSI Creator 15", "base_price": 159990, "brand": "MSI"},
        {"name": "Acer Swift 5", "base_price": 99990, "brand": "Acer"},
        {"name": "Razer Blade 15", "base_price": 199990, "brand": "Razer"},
        {"name": "Gigabyte Aero 16", "base_price": 189990, "brand": "Gigabyte"},
    ],
    "Телевизоры": [
        {"name": "LG OLED C3", "base_price": 149990, "brand": "LG"},
        {"name": "Samsung QLED Q80C", "base_price": 129990, "brand": "Samsung"},
        {"name": "TCL QLED 55C735", "base_price": 79990, "brand": "TCL"},
        {"name": "Hisense U8K", "base_price": 89990, "brand": "Hisense"},
        {"name": "Xiaomi TV A2", "base_price": 59990, "brand": "Xiaomi"},
        {"name": "Philips OLED 806", "base_price": 139990, "brand": "Philips"},
        {"name": "Panasonic LZ2000", "base_price": 179990, "brand": "Panasonic"},
    ],
    "Планшеты": [
        {"name": "Samsung Galaxy Tab S9", "base_price": 69990, "brand": "Samsung"},
        {"name": "Huawei MatePad Pro", "base_price": 59990, "brand": "Huawei"},
        {"name": "Lenovo Tab P11 Pro", "base_price": 49990, "brand": "Lenovo"},
        {"name": "Xiaomi Pad 6", "base_price": 39990, "brand": "Xiaomi"},
        {"name": "Honor Pad 9", "base_price": 29990, "brand": "Honor"},
        {"name": "Realme Pad 2", "base_price": 34990, "brand": "Realme"},
        {"name": "Oppo Pad Air", "base_price": 24990, "brand": "Oppo"},
    ]
}

def create_database():
    """Создает базу данных и таблицы"""
    logger.info("Создание базы данных...")
    
    conn = sqlite3.connect('marketplace_500_products.db')
    cursor = conn.cursor()
    
    # Создаем таблицу пользователей
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username VARCHAR(150) NOT NULL UNIQUE,
            email VARCHAR(254) NOT NULL,
            password VARCHAR(128) NOT NULL,
            first_name VARCHAR(150) NOT NULL,
            last_name VARCHAR(150) NOT NULL,
            is_superuser BOOLEAN NOT NULL DEFAULT 0,
            is_staff BOOLEAN NOT NULL DEFAULT 0,
            is_active BOOLEAN NOT NULL DEFAULT 1,
            date_joined DATETIME NOT NULL,
            role VARCHAR(20) NOT NULL DEFAULT 'user'
        )
    """)
    
    # Создаем таблицу категорий
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(100) NOT NULL,
            description TEXT NOT NULL,
            slug VARCHAR(100) NOT NULL UNIQUE,
            parent_id INTEGER REFERENCES categories(id),
            is_active BOOLEAN NOT NULL DEFAULT 1,
            sort_order INTEGER NOT NULL DEFAULT 0,
            created_at DATETIME NOT NULL,
            updated_at DATETIME NOT NULL
        )
    """)
    
    # Создаем таблицу продавцов
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sellers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL UNIQUE REFERENCES users(id),
            company_name VARCHAR(255) NOT NULL,
            description TEXT NOT NULL,
            commission_rate DECIMAL(5,2) NOT NULL DEFAULT 5.00,
            is_verified BOOLEAN NOT NULL DEFAULT 0,
            rating DECIMAL(3,2) NOT NULL DEFAULT 0.00,
            created_at DATETIME NOT NULL,
            updated_at DATETIME NOT NULL
        )
    """)
    
    # Создаем таблицу товаров
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(255) NOT NULL,
            description TEXT NOT NULL,
            price DECIMAL(10,2) NOT NULL,
            discount_price DECIMAL(10,2),
            category_id INTEGER REFERENCES categories(id),
            seller_id INTEGER REFERENCES sellers(id),
            sku VARCHAR(100) UNIQUE,
            stock_quantity INTEGER NOT NULL DEFAULT 0,
            is_active BOOLEAN NOT NULL DEFAULT 1,
            rating DECIMAL(3,2) NOT NULL DEFAULT 0.00,
            reviews_count INTEGER NOT NULL DEFAULT 0,
            created_at DATETIME NOT NULL,
            updated_at DATETIME NOT NULL
        )
    """)
    
    # Создаем таблицу характеристик
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS product_characteristics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL REFERENCES products(id),
            name VARCHAR(100) NOT NULL,
            value VARCHAR(255) NOT NULL,
            unit VARCHAR(20) NOT NULL DEFAULT '',
            order_field INTEGER NOT NULL DEFAULT 0
        )
    """)
    
    conn.commit()
    logger.info("База данных создана успешно")
    return conn

def create_categories(conn):
    """Создает 3-уровневую иерархию категорий"""
    logger.info("Создание иерархии категорий...")
    
    categories_data = {
        "Электроника": {
            "subcategories": {
                "Смартфоны": {},
                "Ноутбуки": {},
                "Телевизоры": {},
                "Планшеты": {},
                "Наушники": {},
                "Часы": {}
            }
        },
        "Одежда и обувь": {
            "subcategories": {
                "Мужская одежда": {},
                "Женская одежда": {},
                "Детская одежда": {},
                "Обувь": {},
                "Аксессуары": {}
            }
        },
        "Дом и сад": {
            "subcategories": {
                "Мебель": {},
                "Декор": {},
                "Кухня": {},
                "Спальня": {},
                "Ванная": {}
            }
        },
        "Спорт и отдых": {
            "subcategories": {
                "Фитнес": {},
                "Игры": {},
                "Туризм": {},
                "Водные виды спорта": {},
                "Зимние виды спорта": {}
            }
        },
        "Красота и здоровье": {
            "subcategories": {
                "Косметика": {},
                "Парфюмерия": {},
                "Уход за кожей": {},
                "Витамины": {},
                "Здоровье": {}
            }
        }
    }
    
    created_categories = {}
    cursor = conn.cursor()
    
    for root_name, root_data in categories_data.items():
        # Создаем корневую категорию
        cursor.execute("""
            INSERT OR IGNORE INTO categories 
            (name, description, slug, parent_id, is_active, sort_order, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (root_name, f"Товары категории {root_name}", 
              root_name.lower().replace(" ", "-").replace("и", "i"), None, True, 0, 
              datetime.now().isoformat(), datetime.now().isoformat()))
        
        # Получаем ID корневой категории
        cursor.execute("SELECT id FROM categories WHERE name = ?", (root_name,))
        root_id = cursor.fetchone()[0]
        created_categories[root_name] = root_id
        
        # Создаем подкатегории 2-го уровня
        for sub_name in root_data['subcategories']:
            cursor.execute("""
                INSERT OR IGNORE INTO categories 
                (name, description, slug, parent_id, is_active, sort_order, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (sub_name, f"Товары подкатегории {sub_name}", 
                  sub_name.lower().replace(" ", "-").replace("и", "i"), root_id, True, 0,
                  datetime.now().isoformat(), datetime.now().isoformat()))
            
            # Получаем ID подкатегории
            cursor.execute("SELECT id FROM categories WHERE name = ? AND parent_id = ?", (sub_name, root_id))
            sub_id = cursor.fetchone()[0]
            created_categories[sub_name] = sub_id
    
    conn.commit()
    logger.info(f"Создано {len(created_categories)} категорий")
    return created_categories

def create_seller(conn):
    """Создает продавца"""
    logger.info("Создание продавца...")
    
    cursor = conn.cursor()
    
    # Создаем пользователя
    cursor.execute("""
        INSERT OR IGNORE INTO users 
        (username, email, password, first_name, last_name, is_superuser, is_staff, is_active, date_joined, role)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, ('marketplace_seller', 'seller@marketplace.ru', 'pbkdf2_sha256$test', 
          'Marketplace', 'Seller', False, False, True, datetime.now().isoformat(), 'seller'))
    
    # Получаем ID пользователя
    cursor.execute("SELECT id FROM users WHERE username = ?", ('marketplace_seller',))
    user_id = cursor.fetchone()[0]
    
    # Создаем продавца
    cursor.execute("""
        INSERT OR IGNORE INTO sellers 
        (user_id, company_name, description, commission_rate, is_verified, rating, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (user_id, 'Marketplace Store', 'Официальный продавец маркетплейса', 5.0, True, 5.0,
          datetime.now().isoformat(), datetime.now().isoformat()))
    
    # Получаем ID продавца
    cursor.execute("SELECT id FROM sellers WHERE user_id = ?", (user_id,))
    seller_id = cursor.fetchone()[0]
    
    conn.commit()
    logger.info("Продавец создан")
    return seller_id

def create_products(conn, categories, seller_id, target_count=500):
    """Создает товары"""
    logger.info(f"Создание {target_count} товаров...")
    
    created = 0
    cursor = conn.cursor()
    
    # Создаем реальные товары
    for product_data in REAL_PRODUCTS_DATA:
        try:
            category_id = categories[product_data["category"]]
            
            # Создаем товар
            cursor.execute("""
                INSERT INTO products 
                (name, description, price, category_id, seller_id, sku, stock_quantity, is_active, rating, reviews_count, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                product_data["name"],
                product_data["description"],
                product_data["price"],
                category_id,
                seller_id,
                f"PRD-{random.randint(100000, 999999)}",
                random.randint(10, 100),
                True,
                round(random.uniform(4.0, 5.0), 2),
                random.randint(10, 500),
                datetime.now().isoformat(),
                datetime.now().isoformat()
            ))
            
            product_id = cursor.lastrowid
            
            # Добавляем характеристики
            for char_data in product_data["characteristics"]:
                cursor.execute("""
                    INSERT INTO product_characteristics 
                    (product_id, name, value, unit, order_field)
                    VALUES (?, ?, ?, ?, ?)
                """, (product_id, char_data["name"], char_data["value"], char_data.get("unit", ""), 0))
            
            created += 1
            logger.info(f"Создан товар: {product_data['name']} (цена: {product_data['price']}₽)")
            
        except Exception as e:
            logger.error(f"Ошибка при создании товара {product_data['name']}: {e}")
    
    # Создаем дополнительные товары
    for category_name, category_id in categories.items():
        if created >= target_count:
            break
            
        if category_name not in PRODUCT_TEMPLATES:
            continue
            
        template_list = PRODUCT_TEMPLATES[category_name]
        
        for i in range(min(target_count - created, len(template_list) * 20)):
            template = template_list[i % len(template_list)]
            
            try:
                # Генерируем вариации названия
                variations = ["", " Plus", " Pro", " Max", " Ultra", " SE", " Lite", " 256GB", " 512GB", " 1TB"]
                variation = random.choice(variations)
                name = template["name"] + variation
                
                # Генерируем цену с вариацией
                price_variation = random.uniform(0.7, 1.3)
                price = int(template["base_price"] * price_variation)
                
                # Создаем товар
                cursor.execute("""
                    INSERT INTO products 
                    (name, description, price, category_id, seller_id, sku, stock_quantity, is_active, rating, reviews_count, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    name,
                    f"Высококачественный {category_name.lower()} {template['brand']} с отличными характеристиками и современным дизайном. Идеально подходит для повседневного использования.",
                    price,
                    category_id,
                    seller_id,
                    f"PRD-{random.randint(100000, 999999)}",
                    random.randint(5, 100),
                    True,
                    round(random.uniform(3.5, 5.0), 2),
                    random.randint(5, 300),
                    datetime.now().isoformat(),
                    datetime.now().isoformat()
                ))
                
                product_id = cursor.lastrowid
                
                # Добавляем базовые характеристики
                base_characteristics = [
                    {"name": "Бренд", "value": template["brand"]},
                    {"name": "Модель", "value": name},
                    {"name": "Цвет", "value": random.choice(["Черный", "Белый", "Серый", "Синий", "Красный", "Золотой", "Серебряный"])},
                    {"name": "Гарантия", "value": "12 месяцев"},
                    {"name": "Страна производства", "value": random.choice(["Китай", "Южная Корея", "США", "Япония", "Германия"])},
                    {"name": "Вес", "value": f"{random.randint(100, 2000)}", "unit": "г"},
                    {"name": "Размеры", "value": f"{random.randint(50, 300)}x{random.randint(50, 300)}x{random.randint(5, 50)}", "unit": "мм"},
                ]
                
                # Добавляем специфичные характеристики для категории
                if category_name == "Смартфоны":
                    base_characteristics.extend([
                        {"name": "Диагональ экрана", "value": f"{random.uniform(5.0, 7.0):.1f}", "unit": "дюйма"},
                        {"name": "Разрешение экрана", "value": random.choice(["1080x2400", "1440x3200", "1179x2556"])},
                        {"name": "Процессор", "value": random.choice(["Snapdragon 8 Gen 3", "Apple A17 Pro", "MediaTek Dimensity 9000"])},
                        {"name": "Объем памяти", "value": random.choice(["128", "256", "512", "1"]), "unit": "ГБ"},
                        {"name": "Оперативная память", "value": random.choice(["8", "12", "16"]), "unit": "ГБ"},
                    ])
                elif category_name == "Ноутбуки":
                    base_characteristics.extend([
                        {"name": "Диагональ экрана", "value": random.choice(["13.3", "14", "15.6", "16", "17.3"]), "unit": "дюйма"},
                        {"name": "Разрешение экрана", "value": random.choice(["1920x1080", "2560x1440", "2880x1800", "3456x2234"])},
                        {"name": "Процессор", "value": random.choice(["Intel Core i7", "Intel Core i9", "AMD Ryzen 7", "Apple M3"])},
                        {"name": "Видеокарта", "value": random.choice(["NVIDIA RTX 4060", "NVIDIA RTX 4070", "AMD Radeon RX 7600", "Intel Iris Xe"])},
                        {"name": "Объем памяти", "value": random.choice(["512", "1", "2"]), "unit": "ТБ SSD"},
                    ])
                elif category_name == "Телевизоры":
                    base_characteristics.extend([
                        {"name": "Диагональ экрана", "value": random.choice(["43", "55", "65", "75", "85"]), "unit": "дюймов"},
                        {"name": "Разрешение экрана", "value": random.choice(["4K UHD", "8K UHD", "Full HD"])},
                        {"name": "Технология экрана", "value": random.choice(["OLED", "QLED", "LED", "Mini LED"])},
                        {"name": "HDR", "value": random.choice(["HDR10", "Dolby Vision", "HDR10+", "HLG"])},
                        {"name": "Частота обновления", "value": random.choice(["60", "120", "240"]), "unit": "Гц"},
                    ])
                elif category_name == "Планшеты":
                    base_characteristics.extend([
                        {"name": "Диагональ экрана", "value": random.choice(["10.1", "10.9", "11", "12.9"]), "unit": "дюйма"},
                        {"name": "Разрешение экрана", "value": random.choice(["1920x1200", "2560x1600", "2732x2048"])},
                        {"name": "Процессор", "value": random.choice(["Apple M2", "Snapdragon 8 Gen 2", "MediaTek Dimensity 9000"])},
                        {"name": "Объем памяти", "value": random.choice(["64", "128", "256", "512"]), "unit": "ГБ"},
                        {"name": "Операционная система", "value": random.choice(["iPadOS", "Android", "Windows"])},
                    ])
                
                for char_data in base_characteristics:
                    cursor.execute("""
                        INSERT INTO product_characteristics 
                        (product_id, name, value, unit, order_field)
                        VALUES (?, ?, ?, ?, ?)
                    """, (product_id, char_data["name"], char_data["value"], char_data.get("unit", ""), 0))
                
                created += 1
                
                if created % 50 == 0:
                    logger.info(f"Создано {created} товаров...")
                
            except Exception as e:
                logger.error(f"Ошибка при создании дополнительного товара: {e}")
    
    conn.commit()
    return created

def check_results(conn):
    """Проверяет результаты"""
    logger.info("Проверка результатов...")
    
    cursor = conn.cursor()
    
    # Подсчитываем товары
    cursor.execute("SELECT COUNT(*) FROM products")
    total_products = cursor.fetchone()[0]
    
    # Подсчитываем категории
    cursor.execute("SELECT COUNT(*) FROM categories")
    total_categories = cursor.fetchone()[0]
    
    # Подсчитываем характеристики
    cursor.execute("SELECT COUNT(*) FROM product_characteristics")
    total_characteristics = cursor.fetchone()[0]
    
    # Подсчитываем продавцов
    cursor.execute("SELECT COUNT(*) FROM sellers")
    total_sellers = cursor.fetchone()[0]
    
    logger.info(f"\n=== ИТОГОВАЯ СТАТИСТИКА ===")
    logger.info(f"Товаров: {total_products}")
    logger.info(f"Категорий: {total_categories}")
    logger.info(f"Характеристик: {total_characteristics}")
    logger.info(f"Продавцов: {total_sellers}")
    
    if total_products >= 500:
        logger.info("✅ Цель достигнута: создано 500+ товаров")
    else:
        logger.warning(f"⚠️ Создано только {total_products} товаров из 500")
    
    return total_products, total_categories, total_characteristics

def main():
    logger.info("🎯 НАЧАЛО СОЗДАНИЯ 500 ТОВАРОВ")
    logger.info("=" * 60)
    
    try:
        # Создаем базу данных
        conn = create_database()
        
        # Создаем категории
        categories = create_categories(conn)
        
        # Создаем продавца
        seller_id = create_seller(conn)
        
        # Создаем товары
        created_products = create_products(conn, categories, seller_id, 500)
        
        # Проверяем результаты
        total_products, total_categories, total_characteristics = check_results(conn)
        
        # Закрываем соединение
        conn.close()
        
        logger.info("🎉 СОЗДАНИЕ ТОВАРОВ ЗАВЕРШЕНО!")
        logger.info("=" * 60)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ КРИТИЧЕСКАЯ ОШИБКА: {e}")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n✅ Все задачи выполнены успешно!")
        print("📊 Проверьте базу данных marketplace_500_products.db")
    else:
        print("\n❌ Процесс завершился с ошибками")
        print("📋 Проверьте логи для деталей")
    
    exit(0 if success else 1)
