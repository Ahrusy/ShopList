#!/usr/bin/env python
import os
import sys
import django
import requests
import json
import random
import logging
from decimal import Decimal
from django.core.files.base import ContentFile
from time import sleep

# Настройка логгера
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('add_products.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shoplist.settings')
django.setup()

from products.models import Category, Shop, Seller, Product, User, Tag, ProductCharacteristic, ProductImage

logger.info("=== НАЧАЛО ДОБАВЛЕНИЯ ТОВАРОВ ===")

# Создаем иерархию категорий
# Корневые категории
electronics = Category.objects.get_or_create(
    slug='electronics',
    defaults={'name': 'Электроника', 'icon': 'laptop', 'description': 'Электронные товары'}
)[0]

clothing = Category.objects.get_or_create(
    slug='clothing',
    defaults={'name': 'Одежда', 'icon': 'tshirt', 'description': 'Одежда и обувь'}
)[0]

# Подкатегории 2-го уровня для Электроники
smartphones = Category.objects.get_or_create(
    slug='smartphones',
    defaults={'name': 'Смартфоны', 'parent': electronics}
)[0]

laptops = Category.objects.get_or_create(
    slug='laptops',
    defaults={'name': 'Ноутбуки', 'parent': electronics}
)[0]

# Подкатегории 3-го уровня для Смартфонов
android = Category.objects.get_or_create(
    slug='android',
    defaults={'name': 'Android', 'parent': smartphones}
)[0]

ios = Category.objects.get_or_create(
    slug='ios',
    defaults={'name': 'iOS', 'parent': smartphones}
)[0]

# Подкатегории 3-го уровня для Ноутбуков
gaming_laptops = Category.objects.get_or_create(
    slug='gaming-laptops',
    defaults={'name': 'Игровые ноутбуки', 'parent': laptops}
)[0]

ultrabooks = Category.objects.get_or_create(
    slug='ultrabooks',
    defaults={'name': 'Ультрабуки', 'parent': laptops}
)[0]

# Подкатегории 2-го уровня для Одежды
mens_clothing = Category.objects.get_or_create(
    slug='mens-clothing',
    defaults={'name': 'Мужская одежда', 'parent': clothing}
)[0]

womens_clothing = Category.objects.get_or_create(
    slug='womens-clothing',
    defaults={'name': 'Женская одежда', 'parent': clothing}
)[0]

# Подкатегории 3-го уровня для Мужской одежды
mens_shirts = Category.objects.get_or_create(
    slug='mens-shirts',
    defaults={'name': 'Рубашки', 'parent': mens_clothing}
)[0]

mens_jeans = Category.objects.get_or_create(
    slug='mens-jeans',
    defaults={'name': 'Джинсы', 'parent': mens_clothing}
)[0]

# Подкатегории 3-го уровня для Женской одежды
womens_dresses = Category.objects.get_or_create(
    slug='womens-dresses',
    defaults={'name': 'Платья', 'parent': womens_clothing}
)[0]

womens_blouses = Category.objects.get_or_create(
    slug='womens-blouses',
    defaults={'name': 'Блузки', 'parent': womens_clothing}
)[0]

# Словарь категорий для использования в товарах
categories = {
    'android': android,
    'ios': ios,
    'gaming_laptops': gaming_laptops,
    'ultrabooks': ultrabooks,
    'mens_shirts': mens_shirts,
    'mens_jeans': mens_jeans,
    'womens_dresses': womens_dresses,
    'womens_blouses': womens_blouses
}

# Создаем теги
tags = {
    'Популярное': Tag.objects.get_or_create(name='Популярное')[0],
    'Новинка': Tag.objects.get_or_create(name='Новинка')[0],
    'Скидка': Tag.objects.get_or_create(name='Скидка')[0],
    'Хит': Tag.objects.get_or_create(name='Хит')[0],
    'Эксклюзив': Tag.objects.get_or_create(name='Эксклюзив')[0]
}

# Создаем магазин
shop, _ = Shop.objects.get_or_create(
    name='Ozon Маркетплейс',
    defaults={
        'address': 'Москва, ул. Льва Толстого, 16',
        'city': 'Москва',
        'phone': '+7 (495) 232-10-00',
        'email': 'info@ozon.ru'
    }
)

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

# Функция для получения товаров с Ozon API
def fetch_ozon_products():
    logger.info("Попытка получения данных от Ozon API...")
    url = "https://api-seller.ozon.ru/v2/product/list"
    headers = {
        "Client-Id": "YOUR_CLIENT_ID",
        "Api-Key": "YOUR_API_KEY",
        "Content-Type": "application/json"
    }
    payload = {
        "filter": {
            "visibility": "ALL"
        },
        "limit": 500,
        "sort_dir": "ASC"
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        items = data.get('result', {}).get('items', [])
        logger.info(f"Получено {len(items)} товаров от Ozon API")
        return items
    except Exception as e:
        logger.error(f"Ошибка при получении данных от Ozon: {e}")
        return []

# Функция для скачивания изображения с повторными попытками
def download_image(url, max_retries=5):
    for attempt in range(max_retries):
        try:
            # Увеличиваем таймаут и игнорируем SSL ошибки
            response = requests.get(url, timeout=30, verify=False)
            response.raise_for_status()
            return ContentFile(response.content)
        except Exception as e:
            logger.warning(f"Попытка {attempt+1}/{max_retries}: Ошибка при скачивании {url}: {e}")
            sleep(1 + attempt)  # Увеличиваем задержку с каждой попыткой
    logger.error(f"Не удалось скачать изображение после {max_retries} попыток: {url}")
    return None

# Получаем товары с Ozon
logger.info("Получаем данные о товарах...")
ozon_products = fetch_ozon_products()

if not ozon_products:
    logger.info("Не удалось получить данные от Ozon. Используем локальные данные.")
    # Генерируем 500 реалистичных товаров по категориям
    logger.info("Генерируем реалистичные товары для 500 позиций...")
    ozon_products = []
    
    # Шаблоны товаров по категориям
    product_templates = {
        'android': [
            {
                'name': "Смартфон {brand} {model}",
                'models': ["Galaxy S23", "Pixel 8", "Xiaomi 13", "OnePlus 11", "Redmi Note 12"],
                'brands': ["Samsung", "Google", "Xiaomi", "OnePlus", "Realme"],
                'characteristics': [
                    {"name": "Экран", "value": ["6.1 дюйм", "6.4 дюйм", "6.7 дюйм"]},
                    {"name": "Память", "value": ["128 ГБ", "256 ГБ", "512 ГБ"]},
                    {"name": "ОЗУ", "value": ["8 ГБ", "12 ГБ", "16 ГБ"]},
                    {"name": "Процессор", "value": ["Snapdragon 8 Gen 2", "Tensor G3", "Dimensity 9200"]},
                    {"name": "Камера", "value": ["50 МП", "108 МП", "200 МП"]}
                ]
            }
        ],
        'ios': [
            {
                'name': "iPhone {model}",
                'models': ["15 Pro", "15", "14 Pro", "14", "13"],
                'brands': ["Apple"],
                'characteristics': [
                    {"name": "Экран", "value": ["6.1 дюйм", "6.7 дюйм"]},
                    {"name": "Память", "value": ["128 ГБ", "256 ГБ", "512 ГБ", "1 ТБ"]},
                    {"name": "Процессор", "value": ["A16 Bionic", "A15 Bionic"]},
                    {"name": "Камера", "value": ["12 МП", "48 МП"]}
                ]
            }
        ],
        'gaming_laptops': [
            {
                'name': "Игровой ноутбук {brand} {model}",
                'models': ["ROG Strix", "Legion Pro", "Predator", "Nitro", "TUF Gaming"],
                'brands': ["ASUS", "Lenovo", "Acer", "MSI", "HP"],
                'characteristics': [
                    {"name": "Экран", "value": ["15.6 дюйм", "17.3 дюйм"]},
                    {"name": "Процессор", "value": ["Intel Core i7", "Intel Core i9", "AMD Ryzen 7", "AMD Ryzen 9"]},
                    {"name": "Видеокарта", "value": ["RTX 4060", "RTX 4070", "RTX 4080", "RX 7600M", "RX 7700M"]},
                    {"name": "ОЗУ", "value": ["16 ГБ", "32 ГБ", "64 ГБ"]},
                    {"name": "SSD", "value": ["512 ГБ", "1 ТБ", "2 ТБ"]}
                ]
            }
        ],
        'ultrabooks': [
            {
                'name': "Ультрабук {brand} {model}",
                'models': ["Zenbook", "XPS", "Spectre", "Swift", "Envy"],
                'brands': ["ASUS", "Dell", "HP", "Acer", "Lenovo"],
                'characteristics': [
                    {"name": "Экран", "value": ["13.3 дюйм", "14 дюйм", "15.6 дюйм"]},
                    {"name": "Процессор", "value": ["Intel Core i5", "Intel Core i7", "AMD Ryzen 5", "AMD Ryzen 7"]},
                    {"name": "ОЗУ", "value": ["8 ГБ", "16 ГБ", "32 ГБ"]},
                    {"name": "SSD", "value": ["256 ГБ", "512 ГБ", "1 ТБ"]},
                    {"name": "Вес", "value": ["1.2 кг", "1.5 кг", "1.8 кг"]}
                ]
            }
        ],
        'mens_shirts': [
            {
                'name': "Мужская рубашка {brand}",
                'models': ["Классическая", "Оксфорд", "Фланелевая", "Джинсовая"],
                'brands': ["H&M", "Zara", "Bershka", "Lacoste", "Tommy Hilfiger"],
                'characteristics': [
                    {"name": "Размер", "value": ["S", "M", "L", "XL"]},
                    {"name": "Цвет", "value": ["Белый", "Голубой", "Черный", "Клетка", "Полоска"]},
                    {"name": "Материал", "value": ["Хлопок", "Лен", "Вискоза", "Смесовый"]},
                    {"name": "Стиль", "value": ["Повседневная", "Офисная", "Вечерняя"]}
                ]
            }
        ],
        'mens_jeans': [
            {
                'name': "Мужские джинсы {brand}",
                'models': ["Слим", "Прямые", "Расклешенные", "Брюки-джинсы"],
                'brands': ["Levi's", "Wrangler", "Lee", "Diesel", "Calvin Klein"],
                'characteristics': [
                    {"name": "Размер", "value": ["S", "M", "L", "XL"]},
                    {"name": "Цвет", "value": ["Синий", "Черный", "Серый", "Светлый"]},
                    {"name": "Материал", "value": ["Деним", "Стрейч"]},
                    {"name": "Посадка", "value": ["Завышенная", "Классическая", "Заниженная"]}
                ]
            }
        ],
        'womens_dresses': [
            {
                'name': "Женское платье {brand}",
                'models': ["Вечернее", "Повседневное", "Летнее", "Коктейльное"],
                'brands': ["Mango", "Zara", "H&M", "Reserved", "Ostin"],
                'characteristics': [
                    {"name": "Размер", "value": ["XS", "S", "M", "L"]},
                    {"name": "Цвет", "value": ["Красный", "Черный", "Белый", "Цветочный"]},
                    {"name": "Материал", "value": ["Хлопок", "Шифон", "Шелк", "Вискоза"]},
                    {"name": "Длина", "value": ["Мини", "Миди", "Макси"]}
                ]
            }
        ],
        'womens_blouses': [
            {
                'name': "Женская блузка {brand}",
                'models': ["Классическая", "Рубашка", "Батик", "Кружевная"],
                'brands': ["Mango", "Zara", "H&M", "Reserved", "Ostin"],
                'characteristics': [
                    {"name": "Размер", "value": ["XS", "S", "M", "L"]},
                    {"name": "Цвет", "value": ["Белый", "Голубой", "Розовый", "Черный"]},
                    {"name": "Материал", "value": ["Шелк", "Хлопок", "Вискоза", "Шифон"]},
                    {"name": "Стиль", "value": ["Офисный", "Повседневный", "Вечерний"]}
                ]
            }
        ]
    }
    
    # Генерируем товары
    for i in range(500):
        try:
            # Выбираем случайную категорию
            category_key = random.choice(list(categories.keys()))
            category = categories[category_key]
            
            # Выбираем шаблон для категории
            template = random.choice(product_templates[category_key])
            
            # Генерируем характеристики товара
            characteristics = []
            for char_template in template['characteristics']:
                char_value = random.choice(char_template['value'])
                characteristics.append({
                    "name": char_template['name'],
                    "value": char_value
                })
            
            # Формируем название
            brand = random.choice(template['brands'])
            model = random.choice(template['models'])
            name = template['name'].format(brand=brand, model=model)
            
            # Формируем описание
            description = f"{name} - качественный товар от бренда {brand}. Отличное сочетание стиля и функциональности."
            
            # Генерируем цену
            price = Decimal(random.randint(2000, 50000) / 100).quantize(Decimal('0.01'))
            old_price = price * Decimal('1.2') if random.random() > 0.5 else None
            
            # Генерируем изображения
            images = []
            for j in range(random.randint(1, 5)):
                images.append(f"https://picsum.photos/800/600?fashion={i}{j}")
            
            ozon_products.append({
                "product_id": 100000 + i,
                "name": name,
                "description": description,
                "price": str(price),
                "old_price": str(old_price) if old_price else None,
                "category": category_key,
                "characteristics": characteristics,
                "images": images
            })
        except Exception as e:
            logger.error(f"Ошибка при генерации товара {i}: {e}")
    
    logger.info(f"Сгенерировано {len(ozon_products)} демо-товаров")

# Добавляем товары в базу данных
logger.info(f"Найдено {len(ozon_products)} товаров. Начинаем добавление...")
total_count = len(ozon_products)
success_count = 0
error_count = 0

for i, ozon_product in enumerate(ozon_products[:500]):  # Ограничиваем 500 товарами
    try:
        # Выбираем случайную категорию из нашего словаря
        category = random.choice(list(categories.values()))
        
        # Создаем товар
        price_str = ozon_product.get('price', '1000.00')
        old_price_str = ozon_product.get('old_price')
        
        price = Decimal(price_str) if price_str else Decimal('1000.00')
        discount_price = Decimal(old_price_str) if old_price_str else None
        
        product = Product.objects.create(
            name=ozon_product.get('name', f'Товар {i+1}'),
            description=ozon_product.get('description', 'Описание отсутствует'),
            price=price,
            discount_price=discount_price,
            category=category,
            seller=seller,
            stock_quantity=random.randint(10, 100),
            rating=Decimal(random.uniform(3.5, 5.0)).quantize(Decimal('0.01')),
            reviews_count=random.randint(5, 100)
        )
        
        # Добавляем теги
        product_tags = random.sample(list(tags.values()), k=random.randint(1, 3))
        product.tags.set(product_tags)
        
        # Добавляем характеристики
        characteristics = ozon_product.get('characteristics', [])
        for char in characteristics:
            ProductCharacteristic.objects.create(
                product=product,
                name=char.get('name', 'Характеристика'),
                value=char.get('value', 'Значение')
            )
        
        # Добавляем изображения с ограничением скорости
        image_urls = ozon_product.get('images', [])
        for j, img_url in enumerate(image_urls[:5]):  # Максимум 5 изображений
            try:
                image_data = download_image(img_url)
                if image_data:
                    img = ProductImage(
                        product=product,
                        alt_text=f"{product.name} - изображение {j+1}",
                        is_primary=(j == 0),
                        order=j
                    )
                    img.image.save(
                        f"product_{product.id}_img_{j}.jpg",
                        image_data,
                        save=True
                    )
                    sleep(0.5)  # Задержка между загрузками изображений
            except Exception as e:
                logger.error(f"Ошибка при загрузке изображения: {e}")
        
        success_count += 1
        if (i+1) % 50 == 0 or i == total_count - 1:
            logger.info(f"✅ Обработано {i+1}/{total_count} товаров")
        
    except Exception as e:
        error_count += 1
        logger.error(f"❌ Ошибка при добавлении товара {i+1}: {e}")

logger.info(f"\n=== РЕЗУЛЬТАТ ===")
logger.info(f"Успешно добавлено: {success_count} товаров")
logger.info(f"Ошибок: {error_count}")
logger.info(f"Всего товаров в базе: {Product.objects.count()}")
logger.info(f"Характеристик: {ProductCharacteristic.objects.count()}")
logger.info(f"Изображений: {ProductImage.objects.count()}")
logger.info(f"Продавцы: {Seller.objects.count()}")
logger.info(f"Теги: {Tag.objects.count()}")
logger.info(f"\n🎉 Товары успешно добавлены!")
logger.info(f"🌐 Откройте: http://127.0.0.1:8000/")
logger.info(f"🔧 Админка: http://127.0.0.1:8000/admin/ (admin/admin123)")
logger.info("Подробный лог сохранен в add_products.log")
