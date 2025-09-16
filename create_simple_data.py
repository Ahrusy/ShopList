#!/usr/bin/env python
"""
Упрощенный скрипт для создания тестовых данных без переводов
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
        logging.FileHandler('create_simple_data.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shoplist.settings')
django.setup()

from products.models import Category, Product, ProductCharacteristic, ProductImage, Seller, User

logger.info("=== СОЗДАНИЕ УПРОЩЕННЫХ ТЕСТОВЫХ ДАННЫХ ===")

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

def create_simple_categories():
    """Создает простые категории без переводов"""
    logger.info("Создание простых категорий...")
    
    categories_data = [
        {"name": "Смартфоны", "slug": "smartfony", "description": "Мобильные телефоны и смартфоны"},
        {"name": "Ноутбуки", "slug": "noutbuki", "description": "Портативные компьютеры"},
        {"name": "Телевизоры", "slug": "televizory", "description": "Телевизоры и мониторы"},
        {"name": "Планшеты", "slug": "planshety", "description": "Планшетные компьютеры"},
        {"name": "Наушники", "slug": "naushniki", "description": "Наушники и гарнитуры"},
        {"name": "Часы", "slug": "chasy", "description": "Умные часы и фитнес-трекеры"},
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
            # Устанавливаем переводы
            category.set_current_language('ru')
            category.name = cat_data["name"]
            category.description = cat_data["description"]
            category.save()
            logger.info(f"Создана категория: {cat_data['name']}")
        
        created_categories[cat_data["name"]] = category
    
    return created_categories

def create_simple_products(categories, target_count=500):
    """Создает простые товары без переводов"""
    logger.info(f"Создание {target_count} простых товаров...")
    
    # Шаблоны товаров
    product_templates = {
        "Смартфоны": [
            {"name": "iPhone 15 Pro Max", "base_price": 99990, "brand": "Apple"},
            {"name": "Samsung Galaxy S24 Ultra", "base_price": 119990, "brand": "Samsung"},
            {"name": "Xiaomi Redmi Note 13 Pro", "base_price": 29990, "brand": "Xiaomi"},
            {"name": "OnePlus 12", "base_price": 59990, "brand": "OnePlus"},
            {"name": "Google Pixel 8", "base_price": 79990, "brand": "Google"},
            {"name": "Huawei P60 Pro", "base_price": 89990, "brand": "Huawei"},
            {"name": "Nothing Phone 2", "base_price": 39990, "brand": "Nothing"},
        ],
        "Ноутбуки": [
            {"name": "MacBook Pro 16 M3 Max", "base_price": 299990, "brand": "Apple"},
            {"name": "Dell XPS 15", "base_price": 199990, "brand": "Dell"},
            {"name": "HP Spectre x360", "base_price": 179990, "brand": "HP"},
            {"name": "Lenovo ThinkPad X1", "base_price": 249990, "brand": "Lenovo"},
            {"name": "MSI Creator 15", "base_price": 159990, "brand": "MSI"},
            {"name": "ASUS ROG Strix G16", "base_price": 149990, "brand": "ASUS"},
            {"name": "Acer Swift 5", "base_price": 99990, "brand": "Acer"},
        ],
        "Телевизоры": [
            {"name": "Sony BRAVIA XR-65A95L", "base_price": 199990, "brand": "Sony"},
            {"name": "LG OLED C3", "base_price": 149990, "brand": "LG"},
            {"name": "Samsung QLED Q80C", "base_price": 129990, "brand": "Samsung"},
            {"name": "TCL QLED 55C735", "base_price": 79990, "brand": "TCL"},
            {"name": "Hisense U8K", "base_price": 89990, "brand": "Hisense"},
            {"name": "Xiaomi TV A2", "base_price": 59990, "brand": "Xiaomi"},
        ],
        "Планшеты": [
            {"name": "iPad Pro 12.9 M2", "base_price": 89990, "brand": "Apple"},
            {"name": "Samsung Galaxy Tab S9", "base_price": 69990, "brand": "Samsung"},
            {"name": "Huawei MatePad Pro", "base_price": 59990, "brand": "Huawei"},
            {"name": "Lenovo Tab P11 Pro", "base_price": 49990, "brand": "Lenovo"},
            {"name": "Xiaomi Pad 6", "base_price": 39990, "brand": "Xiaomi"},
            {"name": "Honor Pad 9", "base_price": 29990, "brand": "Honor"},
        ],
        "Наушники": [
            {"name": "AirPods Pro 2", "base_price": 24990, "brand": "Apple"},
            {"name": "Sony WH-1000XM5", "base_price": 39990, "brand": "Sony"},
            {"name": "Bose QuietComfort 45", "base_price": 34990, "brand": "Bose"},
            {"name": "Sennheiser HD 660S", "base_price": 49990, "brand": "Sennheiser"},
            {"name": "JBL Live Pro 2", "base_price": 12990, "brand": "JBL"},
        ],
        "Часы": [
            {"name": "Apple Watch Series 9", "base_price": 39990, "brand": "Apple"},
            {"name": "Samsung Galaxy Watch 6", "base_price": 29990, "brand": "Samsung"},
            {"name": "Garmin Fenix 7", "base_price": 59990, "brand": "Garmin"},
            {"name": "Fitbit Versa 4", "base_price": 19990, "brand": "Fitbit"},
            {"name": "Huawei Watch GT 4", "base_price": 24990, "brand": "Huawei"},
        ]
    }
    
    created = 0
    
    for category_name, category in categories.items():
        if created >= target_count:
            break
            
        if category_name not in product_templates:
            continue
            
        template_list = product_templates[category_name]
        
        # Создаем товары для этой категории
        products_per_category = min(target_count - created, len(template_list) * 20)
        
        for i in range(products_per_category):
            if created >= target_count:
                break
                
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
                    category=category,
                    seller=seller,
                    price=price,
                    stock_quantity=random.randint(5, 100),
                    rating=Decimal(random.uniform(3.5, 5.0)).quantize(Decimal('0.01')),
                    reviews_count=random.randint(5, 500),
                    created_at=timezone.now()
                )
                
                # Устанавливаем переводы
                product.set_current_language('ru')
                product.name = name
                product.description = f"Высококачественный {category_name.lower()} {template['brand']} с отличными характеристиками и современным дизайном. Идеально подходит для повседневного использования."
                product.save()
                
                # Добавляем характеристики
                characteristics = [
                    {"name": "Бренд", "value": template["brand"]},
                    {"name": "Модель", "value": name},
                    {"name": "Цвет", "value": random.choice(["Черный", "Белый", "Серый", "Синий", "Красный", "Золотой", "Серебряный"])},
                    {"name": "Гарантия", "value": "12 месяцев"},
                    {"name": "Страна производства", "value": random.choice(["Китай", "Южная Корея", "США", "Япония", "Германия"])},
                    {"name": "Вес", "value": f"{random.randint(100, 2000)} г"},
                    {"name": "Размеры", "value": f"{random.randint(50, 300)}x{random.randint(50, 300)}x{random.randint(5, 50)} мм"},
                ]
                
                # Добавляем специфичные характеристики для категории
                if category_name == "Смартфоны":
                    characteristics.extend([
                        {"name": "Диагональ экрана", "value": f"{random.uniform(5.0, 7.0):.1f} дюйма"},
                        {"name": "Разрешение экрана", "value": random.choice(["1080x2400", "1440x3200", "1179x2556"])},
                        {"name": "Процессор", "value": random.choice(["Snapdragon 8 Gen 3", "Apple A17 Pro", "MediaTek Dimensity 9000"])},
                        {"name": "Объем памяти", "value": random.choice(["128 ГБ", "256 ГБ", "512 ГБ", "1 ТБ"])},
                        {"name": "Оперативная память", "value": random.choice(["8 ГБ", "12 ГБ", "16 ГБ"])},
                    ])
                elif category_name == "Ноутбуки":
                    characteristics.extend([
                        {"name": "Диагональ экрана", "value": random.choice(["13.3", "14", "15.6", "16", "17.3"]) + " дюйма"},
                        {"name": "Разрешение экрана", "value": random.choice(["1920x1080", "2560x1440", "2880x1800", "3456x2234"])},
                        {"name": "Процессор", "value": random.choice(["Intel Core i7", "Intel Core i9", "AMD Ryzen 7", "Apple M3"])},
                        {"name": "Видеокарта", "value": random.choice(["NVIDIA RTX 4060", "NVIDIA RTX 4070", "AMD Radeon RX 7600", "Intel Iris Xe"])},
                        {"name": "Объем памяти", "value": random.choice(["512 ГБ SSD", "1 ТБ SSD", "2 ТБ SSD"])},
                    ])
                elif category_name == "Телевизоры":
                    characteristics.extend([
                        {"name": "Диагональ экрана", "value": random.choice(["43", "55", "65", "75", "85"]) + " дюймов"},
                        {"name": "Разрешение экрана", "value": random.choice(["4K UHD", "8K UHD", "Full HD"])},
                        {"name": "Технология экрана", "value": random.choice(["OLED", "QLED", "LED", "Mini LED"])},
                        {"name": "HDR", "value": random.choice(["HDR10", "Dolby Vision", "HDR10+", "HLG"])},
                        {"name": "Частота обновления", "value": random.choice(["60 Гц", "120 Гц", "240 Гц"])},
                    ])
                elif category_name == "Планшеты":
                    characteristics.extend([
                        {"name": "Диагональ экрана", "value": random.choice(["10.1", "10.9", "11", "12.9"]) + " дюйма"},
                        {"name": "Разрешение экрана", "value": random.choice(["1920x1200", "2560x1600", "2732x2048"])},
                        {"name": "Процессор", "value": random.choice(["Apple M2", "Snapdragon 8 Gen 2", "MediaTek Dimensity 9000"])},
                        {"name": "Объем памяти", "value": random.choice(["64 ГБ", "128 ГБ", "256 ГБ", "512 ГБ"])},
                        {"name": "Операционная система", "value": random.choice(["iPadOS", "Android", "Windows"])},
                    ])
                elif category_name == "Наушники":
                    characteristics.extend([
                        {"name": "Тип", "value": random.choice(["TWS", "Накладные", "Вкладыши", "Полноразмерные"])},
                        {"name": "Подключение", "value": random.choice(["Bluetooth 5.0", "Bluetooth 5.2", "Bluetooth 5.3", "Проводные"])},
                        {"name": "Активное шумоподавление", "value": random.choice(["Да", "Нет"])},
                        {"name": "Время работы", "value": f"{random.randint(5, 30)} часов"},
                        {"name": "Водозащита", "value": random.choice(["IPX4", "IPX5", "IPX7", "Нет"])},
                    ])
                elif category_name == "Часы":
                    characteristics.extend([
                        {"name": "Тип", "value": random.choice(["Умные часы", "Фитнес-трекер", "Спортивные часы"])},
                        {"name": "Диагональ экрана", "value": random.choice(["1.2", "1.4", "1.6", "1.8", "2.0"]) + " дюйма"},
                        {"name": "Операционная система", "value": random.choice(["watchOS", "Wear OS", "Proprietary"])},
                        {"name": "Водозащита", "value": random.choice(["5 ATM", "10 ATM", "IP68", "IPX7"])},
                        {"name": "Время работы", "value": f"{random.randint(1, 14)} дней"},
                    ])
                
                for char_data in characteristics:
                    ProductCharacteristic.objects.create(
                        product=product,
                        name=char_data["name"],
                        value=char_data["value"]
                    )
                
                created += 1
                
                if created % 50 == 0:
                    logger.info(f"Создано {created} товаров...")
                
            except Exception as e:
                logger.error(f"Ошибка при создании товара: {e}")
    
    return created

def main():
    logger.info("Начало создания упрощенных тестовых данных...")
    
    # Очищаем старые данные
    logger.info("Очистка старых данных...")
    try:
        ProductCharacteristic.objects.all().delete()
        ProductImage.objects.all().delete()
        # Удаляем товары по одному, чтобы избежать проблем с ManyToMany
        for product in Product.objects.all():
            product.delete()
        logger.info("Старые данные удалены")
    except Exception as e:
        logger.warning(f"Ошибка при очистке данных: {e}")
        logger.info("Продолжаем без очистки...")
    
    # Создаем категории
    categories = create_simple_categories()
    
    # Создаем товары
    total_products = create_simple_products(categories, 500)
    
    # Итоговая статистика
    total_characteristics = ProductCharacteristic.objects.count()
    total_categories = Category.objects.count()
    
    logger.info(f"\n=== ИТОГОВАЯ СТАТИСТИКА ===")
    logger.info(f"Товаров: {total_products}")
    logger.info(f"Характеристик: {total_characteristics}")
    logger.info(f"Категорий: {total_categories}")
    logger.info(f"Продавцов: {Seller.objects.count()}")
    
    if total_products >= 500:
        logger.info("Цель достигнута: создано 500+ товаров")
    else:
        logger.warning(f"Создано только {total_products} товаров из 500")
    
    logger.info("Создание тестовых данных завершено!")

if __name__ == "__main__":
    main()
