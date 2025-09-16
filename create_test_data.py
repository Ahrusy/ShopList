#!/usr/bin/env python
"""
Скрипт для создания тестовых данных товаров без парсинга
"""
import os
import sys
import django
import random
import logging
from decimal import Decimal
from django.utils import timezone

# Настройка логгера
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('create_test_data.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shoplist.settings')
django.setup()

from products.models import Category, Product, ProductCharacteristic, ProductImage, Seller, User

logger.info("=== СОЗДАНИЕ ТЕСТОВЫХ ДАННЫХ ===")

# Создаем продавца
user, _ = User.objects.get_or_create(
    username='ozon_seller',
    defaults={
        'email': 'seller@ozon.ru',
        'role': 'seller',
        'first_name': 'Ozon',
        'last_name': 'Seller'
    }
)
if not user.password:
    user.set_password('password123')
    user.save()

seller, _ = Seller.objects.get_or_create(
    user=user,
    defaults={
        'company_name': 'Ozon Marketplace',
        'description': 'Официальный продавец маркетплейса Ozon',
        'commission_rate': Decimal('7.0'),
        'is_verified': True
    }
)

# Тестовые данные товаров
TEST_PRODUCTS = [
    {
        "name": "iPhone 15 Pro Max 256GB",
        "description": "Новейший смартфон Apple с титановым корпусом, чипом A17 Pro и камерой 48 МП. Поддержка 5G, Face ID, беспроводная зарядка.",
        "price": Decimal("99990.00"),
        "category": "Смартфоны",
        "characteristics": [
            {"name": "Диагональ экрана", "value": "6.7 дюйма"},
            {"name": "Разрешение экрана", "value": "2796x1290 пикселей"},
            {"name": "Процессор", "value": "Apple A17 Pro"},
            {"name": "Объем памяти", "value": "256 ГБ"},
            {"name": "Основная камера", "value": "48 МП"},
            {"name": "Фронтальная камера", "value": "12 МП"},
            {"name": "Аккумулятор", "value": "4422 мАч"},
            {"name": "Операционная система", "value": "iOS 17"},
            {"name": "Материал корпуса", "value": "Титан"},
            {"name": "Цвет", "value": "Натуральный титан"}
        ]
    },
    {
        "name": "Samsung Galaxy S24 Ultra 512GB",
        "description": "Флагманский смартфон Samsung с S Pen, камерой 200 МП и экраном Dynamic AMOLED 2X. Искусственный интеллект Galaxy AI.",
        "price": Decimal("119990.00"),
        "category": "Смартфоны",
        "characteristics": [
            {"name": "Диагональ экрана", "value": "6.8 дюйма"},
            {"name": "Разрешение экрана", "value": "3120x1440 пикселей"},
            {"name": "Процессор", "value": "Snapdragon 8 Gen 3"},
            {"name": "Объем памяти", "value": "512 ГБ"},
            {"name": "Оперативная память", "value": "12 ГБ"},
            {"name": "Основная камера", "value": "200 МП"},
            {"name": "Фронтальная камера", "value": "12 МП"},
            {"name": "Аккумулятор", "value": "5000 мАч"},
            {"name": "Операционная система", "value": "Android 14"},
            {"name": "Материал корпуса", "value": "Титан"},
            {"name": "Цвет", "value": "Титан черный"}
        ]
    },
    {
        "name": "MacBook Pro 16 M3 Max",
        "description": "Профессиональный ноутбук Apple с чипом M3 Max, дисплеем Liquid Retina XDR и до 22 часов работы от батареи.",
        "price": Decimal("299990.00"),
        "category": "Ноутбуки",
        "characteristics": [
            {"name": "Диагональ экрана", "value": "16.2 дюйма"},
            {"name": "Разрешение экрана", "value": "3456x2234 пикселей"},
            {"name": "Процессор", "value": "Apple M3 Max"},
            {"name": "Объем памяти", "value": "1 ТБ SSD"},
            {"name": "Оперативная память", "value": "32 ГБ"},
            {"name": "Графический процессор", "value": "40-ядерный GPU"},
            {"name": "Время работы от батареи", "value": "до 22 часов"},
            {"name": "Операционная система", "value": "macOS Sonoma"},
            {"name": "Материал корпуса", "value": "Алюминий"},
            {"name": "Цвет", "value": "Серый космос"}
        ]
    },
    {
        "name": "ASUS ROG Strix G16",
        "description": "Игровой ноутбук с процессором Intel Core i7-13650HX, видеокартой RTX 4060 и дисплеем 16 дюймов с частотой 165 Гц.",
        "price": Decimal("149990.00"),
        "category": "Ноутбуки",
        "characteristics": [
            {"name": "Диагональ экрана", "value": "16 дюймов"},
            {"name": "Разрешение экрана", "value": "1920x1200 пикселей"},
            {"name": "Частота обновления", "value": "165 Гц"},
            {"name": "Процессор", "value": "Intel Core i7-13650HX"},
            {"name": "Видеокарта", "value": "NVIDIA GeForce RTX 4060"},
            {"name": "Объем памяти", "value": "512 ГБ SSD"},
            {"name": "Оперативная память", "value": "16 ГБ DDR5"},
            {"name": "Операционная система", "value": "Windows 11"},
            {"name": "Материал корпуса", "value": "Пластик"},
            {"name": "Цвет", "value": "Черный"}
        ]
    },
    {
        "name": "Sony BRAVIA XR-65A95L",
        "description": "OLED телевизор Sony с процессором Cognitive Processor XR, технологией XR OLED Contrast Pro и поддержкой Dolby Vision.",
        "price": Decimal("199990.00"),
        "category": "Телевизоры",
        "characteristics": [
            {"name": "Диагональ экрана", "value": "65 дюймов"},
            {"name": "Разрешение экрана", "value": "4K UHD (3840x2160)"},
            {"name": "Технология экрана", "value": "OLED"},
            {"name": "Процессор", "value": "Cognitive Processor XR"},
            {"name": "HDR", "value": "Dolby Vision, HDR10, HLG"},
            {"name": "Частота обновления", "value": "120 Гц"},
            {"name": "Операционная система", "value": "Google TV"},
            {"name": "Поддержка Wi-Fi", "value": "Wi-Fi 6E"},
            {"name": "Порты", "value": "4x HDMI 2.1, 2x USB"},
            {"name": "Цвет", "value": "Черный"}
        ]
    },
    {
        "name": "iPad Pro 12.9 M2",
        "description": "Профессиональный планшет Apple с чипом M2, дисплеем Liquid Retina XDR и поддержкой Apple Pencil 2-го поколения.",
        "price": Decimal("89990.00"),
        "category": "Планшеты",
        "characteristics": [
            {"name": "Диагональ экрана", "value": "12.9 дюйма"},
            {"name": "Разрешение экрана", "value": "2732x2048 пикселей"},
            {"name": "Процессор", "value": "Apple M2"},
            {"name": "Объем памяти", "value": "256 ГБ"},
            {"name": "Оперативная память", "value": "8 ГБ"},
            {"name": "Камера", "value": "12 МП + 10 МП"},
            {"name": "Фронтальная камера", "value": "12 МП"},
            {"name": "Аккумулятор", "value": "до 10 часов"},
            {"name": "Операционная система", "value": "iPadOS 16"},
            {"name": "Материал корпуса", "value": "Алюминий"},
            {"name": "Цвет", "value": "Серый космос"}
        ]
    }
]

def create_categories():
    """Создает категории товаров"""
    logger.info("Создание категорий...")
    
    categories_data = [
        {"name": "Смартфоны", "slug": "smartfony", "description": "Мобильные телефоны и смартфоны"},
        {"name": "Ноутбуки", "slug": "noutbuki", "description": "Портативные компьютеры"},
        {"name": "Телевизоры", "slug": "televizory", "description": "Телевизоры и мониторы"},
        {"name": "Планшеты", "slug": "planshety", "description": "Планшетные компьютеры"},
    ]
    
    created_categories = {}
    
    for cat_data in categories_data:
        try:
            category = Category.objects.get(slug=cat_data["slug"])
            logger.info(f"Категория уже существует: {cat_data['name']}")
        except Category.DoesNotExist:
            category = Category.objects.create(
                slug=cat_data["slug"],
                is_active=True,
                created_at=timezone.now()
            )
            category.set_current_language('ru')
            category.name = cat_data["name"]
            category.description = cat_data["description"]
            category.save()
            logger.info(f"Создана категория: {cat_data['name']}")
        
        created_categories[cat_data["name"]] = category
    
    return created_categories

def create_products(categories):
    """Создает товары"""
    logger.info("Создание товаров...")
    
    total_products = 0
    
    for product_data in TEST_PRODUCTS:
        try:
            # Получаем категорию
            category = categories[product_data["category"]]
            
            # Создаем товар
            product = Product.objects.create(
                category=category,
                seller=seller,
                price=product_data["price"],
                stock_quantity=random.randint(10, 100),
                rating=Decimal(random.uniform(4.0, 5.0)).quantize(Decimal('0.01')),
                reviews_count=random.randint(10, 500),
                created_at=timezone.now()
            )
            
            # Устанавливаем переводы
            product.set_current_language('ru')
            product.name = product_data["name"]
            product.description = product_data["description"]
            product.save()
            
            # Добавляем характеристики
            for char_data in product_data["characteristics"]:
                ProductCharacteristic.objects.create(
                    product=product,
                    name=char_data["name"],
                    value=char_data["value"]
                )
            
            total_products += 1
            logger.info(f"Создан товар: {product.name} (цена: {product.price}₽)")
            
        except Exception as e:
            logger.error(f"Ошибка при создании товара {product_data['name']}: {e}")
    
    return total_products

def create_additional_products(categories, target_count=500):
    """Создает дополнительные товары для достижения целевого количества"""
    logger.info(f"Создание дополнительных товаров до {target_count}...")
    
    # Шаблоны для генерации товаров
    templates = {
        "Смартфоны": [
            {"name": "Xiaomi Redmi Note 13 Pro", "base_price": 29990},
            {"name": "OnePlus 12", "base_price": 59990},
            {"name": "Google Pixel 8", "base_price": 79990},
            {"name": "Huawei P60 Pro", "base_price": 89990},
            {"name": "Nothing Phone 2", "base_price": 39990},
        ],
        "Ноутбуки": [
            {"name": "Dell XPS 15", "base_price": 199990},
            {"name": "HP Spectre x360", "base_price": 179990},
            {"name": "Lenovo ThinkPad X1", "base_price": 249990},
            {"name": "MSI Creator 15", "base_price": 159990},
            {"name": "Acer Swift 5", "base_price": 99990},
        ],
        "Телевизоры": [
            {"name": "LG OLED C3", "base_price": 149990},
            {"name": "Samsung QLED Q80C", "base_price": 129990},
            {"name": "TCL QLED 55C735", "base_price": 79990},
            {"name": "Hisense U8K", "base_price": 89990},
            {"name": "Xiaomi TV A2", "base_price": 59990},
        ],
        "Планшеты": [
            {"name": "Samsung Galaxy Tab S9", "base_price": 69990},
            {"name": "Huawei MatePad Pro", "base_price": 59990},
            {"name": "Lenovo Tab P11 Pro", "base_price": 49990},
            {"name": "Xiaomi Pad 6", "base_price": 39990},
            {"name": "Honor Pad 9", "base_price": 29990},
        ]
    }
    
    current_count = Product.objects.count()
    additional_needed = target_count - current_count
    
    if additional_needed <= 0:
        logger.info("Целевое количество товаров уже достигнуто")
        return 0
    
    created = 0
    
    for category_name, category in categories.items():
        if created >= additional_needed:
            break
            
        if category_name not in templates:
            continue
            
        template_list = templates[category_name]
        
        for i in range(min(additional_needed - created, len(template_list) * 10)):
            template = template_list[i % len(template_list)]
            
            try:
                # Генерируем вариации названия
                variation = f" {random.choice(['Plus', 'Pro', 'Max', 'Ultra', 'SE', 'Lite'])}" if random.random() > 0.5 else ""
                name = template["name"] + variation
                
                # Генерируем цену с вариацией
                price_variation = random.uniform(0.8, 1.2)
                price = Decimal(str(int(template["base_price"] * price_variation)))
                
                # Создаем товар
                product = Product.objects.create(
                    category=category,
                    seller=seller,
                    price=price,
                    stock_quantity=random.randint(5, 50),
                    rating=Decimal(random.uniform(3.5, 5.0)).quantize(Decimal('0.01')),
                    reviews_count=random.randint(5, 200),
                    created_at=timezone.now()
                )
                
                # Устанавливаем переводы
                product.set_current_language('ru')
                product.name = name
                product.description = f"Высококачественный {category_name.lower()} с отличными характеристиками и современным дизайном."
                product.save()
                
                # Добавляем базовые характеристики
                base_characteristics = [
                    {"name": "Бренд", "value": name.split()[0]},
                    {"name": "Модель", "value": name},
                    {"name": "Цвет", "value": random.choice(["Черный", "Белый", "Серый", "Синий", "Красный"])},
                    {"name": "Гарантия", "value": "12 месяцев"},
                    {"name": "Страна производства", "value": random.choice(["Китай", "Южная Корея", "США", "Япония"])},
                ]
                
                for char_data in base_characteristics:
                    ProductCharacteristic.objects.create(
                        product=product,
                        name=char_data["name"],
                        value=char_data["value"]
                    )
                
                created += 1
                
                if created % 50 == 0:
                    logger.info(f"Создано {created} дополнительных товаров...")
                
            except Exception as e:
                logger.error(f"Ошибка при создании дополнительного товара: {e}")
    
    return created

def main():
    logger.info("Начало создания тестовых данных...")
    
    # Создаем категории
    categories = create_categories()
    
    # Создаем основные товары
    main_products = create_products(categories)
    logger.info(f"Создано основных товаров: {main_products}")
    
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
    
    logger.info("🎉 Создание тестовых данных завершено!")

if __name__ == "__main__":
    main()
