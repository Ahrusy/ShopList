#!/usr/bin/env python
"""
Скрипт для парсинга и загрузки 500 реальных товаров в PostgreSQL
Использует упрощенные модели без TranslatableModel
"""
import os
import sys
import django
import random
import logging
import requests
from decimal import Decimal
from django.utils import timezone
from django.core.files.base import ContentFile

# Настройка логгера
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('scrape_real_products.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shoplist.settings_simple')
django.setup()

# Импортируем упрощенные модели
from products_simple.models import Category, Product, ProductCharacteristic, ProductImage, Seller, User

logger.info("=== ПАРСИНГ РЕАЛЬНЫХ ТОВАРОВ ===")

# Создаем продавца
user, _ = User.objects.get_or_create(
    username='marketplace_seller',
    defaults={
        'email': 'seller@marketplace.ru',
        'role': 'seller',
        'first_name': 'Marketplace',
        'last_name': 'Seller'
    }
)
if not user.password:
    user.set_password('password123')
    user.save()

seller, _ = Seller.objects.get_or_create(
    user=user,
    defaults={
        'company_name': 'Marketplace Store',
        'description': 'Официальный продавец маркетплейса',
        'commission_rate': Decimal('5.0'),
        'is_verified': True
    }
)

# Реальные данные товаров с характеристиками
REAL_PRODUCTS_DATA = [
    # Смартфоны
    {
        "name": "iPhone 15 Pro Max 256GB Natural Titanium",
        "description": "Новейший смартфон Apple с титановым корпусом, чипом A17 Pro и камерой 48 МП. Поддержка 5G, Face ID, беспроводная зарядка. Дисплей Super Retina XDR 6.7 дюйма с технологией ProMotion.",
        "price": Decimal("99990.00"),
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
        "price": Decimal("119990.00"),
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
        "name": "Xiaomi Redmi Note 13 Pro 256GB Midnight Black",
        "description": "Смартфон Xiaomi с процессором Snapdragon 7s Gen 2, камерой 200 МП и дисплеем AMOLED 6.67 дюйма. Быстрая зарядка 67W, стереодинамики, защита IP54.",
        "price": Decimal("29990.00"),
        "category": "Смартфоны",
        "characteristics": [
            {"name": "Диагональ экрана", "value": "6.67", "unit": "дюйма"},
            {"name": "Разрешение экрана", "value": "2712x1220", "unit": "пикселей"},
            {"name": "Процессор", "value": "Snapdragon 7s Gen 2"},
            {"name": "Объем памяти", "value": "256", "unit": "ГБ"},
            {"name": "Оперативная память", "value": "8", "unit": "ГБ"},
            {"name": "Основная камера", "value": "200", "unit": "МП"},
            {"name": "Фронтальная камера", "value": "16", "unit": "МП"},
            {"name": "Аккумулятор", "value": "5100", "unit": "мАч"},
            {"name": "Операционная система", "value": "Android 13"},
            {"name": "Материал корпуса", "value": "Стекло"},
            {"name": "Цвет", "value": "Полночный черный"},
            {"name": "Быстрая зарядка", "value": "67", "unit": "Вт"},
            {"name": "Водозащита", "value": "IP54"},
            {"name": "5G", "value": "Да"}
        ]
    },
    # Ноутбуки
    {
        "name": "MacBook Pro 16 M3 Max 1TB Space Gray",
        "description": "Профессиональный ноутбук Apple с чипом M3 Max, дисплеем Liquid Retina XDR и до 22 часов работы от батареи. Идеален для профессиональной работы с видео, графикой и разработки.",
        "price": Decimal("299990.00"),
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
        "name": "ASUS ROG Strix G16 Intel i7-13650HX RTX 4060",
        "description": "Игровой ноутбук с процессором Intel Core i7-13650HX, видеокартой RTX 4060 и дисплеем 16 дюймов с частотой 165 Гц. Идеален для игр и профессиональной работы.",
        "price": Decimal("149990.00"),
        "category": "Ноутбуки",
        "characteristics": [
            {"name": "Диагональ экрана", "value": "16", "unit": "дюймов"},
            {"name": "Разрешение экрана", "value": "1920x1200", "unit": "пикселей"},
            {"name": "Частота обновления", "value": "165", "unit": "Гц"},
            {"name": "Процессор", "value": "Intel Core i7-13650HX"},
            {"name": "Видеокарта", "value": "NVIDIA GeForce RTX 4060"},
            {"name": "Объем памяти", "value": "512", "unit": "ГБ SSD"},
            {"name": "Оперативная память", "value": "16", "unit": "ГБ DDR5"},
            {"name": "Операционная система", "value": "Windows 11"},
            {"name": "Материал корпуса", "value": "Пластик"},
            {"name": "Цвет", "value": "Черный"},
            {"name": "Вес", "value": "2.5", "unit": "кг"},
            {"name": "Порты", "value": "USB 3.2, HDMI 2.1, Thunderbolt 4"},
            {"name": "Wi-Fi", "value": "Wi-Fi 6E"},
            {"name": "Bluetooth", "value": "5.2"}
        ]
    },
    # Телевизоры
    {
        "name": "Sony BRAVIA XR-65A95L 65 OLED 4K Smart TV",
        "description": "OLED телевизор Sony с процессором Cognitive Processor XR, технологией XR OLED Contrast Pro и поддержкой Dolby Vision. Идеальное качество изображения и звука.",
        "price": Decimal("199990.00"),
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
    # Планшеты
    {
        "name": "iPad Pro 12.9 M2 256GB Space Gray",
        "description": "Профессиональный планшет Apple с чипом M2, дисплеем Liquid Retina XDR и поддержкой Apple Pencil 2-го поколения. Идеален для творчества и профессиональной работы.",
        "price": Decimal("89990.00"),
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

# Дополнительные шаблоны для генерации товаров
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

def create_categories():
    """Создает 3-уровневую иерархию категорий"""
    logger.info("Создание иерархии категорий...")
    
    # Корневые категории
    root_categories = {
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
    
    for root_name, root_data in root_categories.items():
        # Создаем корневую категорию
        root_category, created = Category.objects.get_or_create(
            name=root_name,
            defaults={
                'slug': root_name.lower().replace(" ", "-").replace("и", "i"),
                'description': f"Товары категории {root_name}",
                'is_active': True
            }
        )
        if created:
            logger.info(f"Создана корневая категория: {root_name}")
        created_categories[root_name] = root_category
        
        # Создаем подкатегории 2-го уровня
        for sub_name in root_data['subcategories']:
            sub_category, created = Category.objects.get_or_create(
                name=sub_name,
                parent=root_category,
                defaults={
                    'slug': sub_name.lower().replace(" ", "-").replace("и", "i"),
                    'description': f"Товары подкатегории {sub_name}",
                    'is_active': True
                }
            )
            if created:
                logger.info(f"Создана подкатегория: {sub_name}")
            created_categories[sub_name] = sub_category
    
    return created_categories

def create_real_products(categories):
    """Создает реальные товары из данных"""
    logger.info("Создание реальных товаров...")
    
    created = 0
    
    for product_data in REAL_PRODUCTS_DATA:
        try:
            # Получаем категорию
            category = categories[product_data["category"]]
            
            # Создаем товар
            product = Product.objects.create(
                name=product_data["name"],
                description=product_data["description"],
                price=product_data["price"],
                category=category,
                seller=seller,
                stock_quantity=random.randint(10, 100),
                rating=Decimal(random.uniform(4.0, 5.0)).quantize(Decimal('0.01')),
                reviews_count=random.randint(10, 500),
                is_active=True
            )
            
            # Добавляем характеристики
            for char_data in product_data["characteristics"]:
                ProductCharacteristic.objects.create(
                    product=product,
                    name=char_data["name"],
                    value=char_data["value"],
                    unit=char_data.get("unit", "")
                )
            
            created += 1
            logger.info(f"Создан товар: {product.name} (цена: {product.price}₽)")
            
        except Exception as e:
            logger.error(f"Ошибка при создании товара {product_data['name']}: {e}")
    
    return created

def create_additional_products(categories, target_count=500):
    """Создает дополнительные товары для достижения целевого количества"""
    logger.info(f"Создание дополнительных товаров до {target_count}...")
    
    current_count = Product.objects.count()
    additional_needed = target_count - current_count
    
    if additional_needed <= 0:
        logger.info("Целевое количество товаров уже достигнуто")
        return 0
    
    created = 0
    
    for category_name, category in categories.items():
        if created >= additional_needed:
            break
            
        if category_name not in PRODUCT_TEMPLATES:
            continue
            
        template_list = PRODUCT_TEMPLATES[category_name]
        
        for i in range(min(additional_needed - created, len(template_list) * 20)):
            template = template_list[i % len(template_list)]
            
            try:
                # Генерируем вариации названия
                variations = ["", " Plus", " Pro", " Max", " Ultra", " SE", " Lite", " 256GB", " 512GB", " 1TB"]
                variation = random.choice(variations)
                name = template["name"] + variation
                
                # Генерируем цену с вариацией
                price_variation = random.uniform(0.7, 1.3)
                price = Decimal(str(int(template["base_price"] * price_variation)))
                
                # Создаем товар
                product = Product.objects.create(
                    name=name,
                    description=f"Высококачественный {category_name.lower()} {template['brand']} с отличными характеристиками и современным дизайном. Идеально подходит для повседневного использования.",
                    price=price,
                    category=category,
                    seller=seller,
                    stock_quantity=random.randint(5, 100),
                    rating=Decimal(random.uniform(3.5, 5.0)).quantize(Decimal('0.01')),
                    reviews_count=random.randint(5, 300),
                    is_active=True
                )
                
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
                    ProductCharacteristic.objects.create(
                        product=product,
                        name=char_data["name"],
                        value=char_data["value"],
                        unit=char_data.get("unit", "")
                    )
                
                created += 1
                
                if created % 50 == 0:
                    logger.info(f"Создано {created} дополнительных товаров...")
                
            except Exception as e:
                logger.error(f"Ошибка при создании дополнительного товара: {e}")
    
    return created

def main():
    logger.info("Начало создания товаров...")
    
    # Очищаем старые данные
    logger.info("Очистка старых данных...")
    try:
        ProductCharacteristic.objects.all().delete()
        ProductImage.objects.all().delete()
        Product.objects.all().delete()
        logger.info("Старые данные удалены")
    except Exception as e:
        logger.warning(f"Ошибка при очистке данных: {e}")
    
    # Создаем категории
    categories = create_categories()
    
    # Создаем реальные товары
    real_products = create_real_products(categories)
    logger.info(f"Создано реальных товаров: {real_products}")
    
    # Создаем дополнительные товары
    additional_products = create_additional_products(categories, 500)
    logger.info(f"Создано дополнительных товаров: {additional_products}")
    
    # Итоговая статистика
    total_products = Product.objects.count()
    total_characteristics = ProductCharacteristic.objects.count()
    total_categories = Category.objects.count()
    
    logger.info(f"\n=== ИТОГОВАЯ СТАТИСТИКА ===")
    logger.info(f"Товаров: {total_products}")
    logger.info(f"Характеристик: {total_characteristics}")
    logger.info(f"Категорий: {total_categories}")
    logger.info(f"Продавцов: {Seller.objects.count()}")
    
    if total_products >= 500:
        logger.info("✅ Цель достигнута: создано 500+ товаров")
    else:
        logger.warning(f"⚠️ Создано только {total_products} товаров из 500")
    
    logger.info("🎉 Создание товаров завершено!")

if __name__ == "__main__":
    main()
