#!/usr/bin/env python
"""
Скрипт для создания реальных товаров с настоящими фотографиями
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

fake = Faker('ru_RU')

# Реальные товары с настоящими названиями
REAL_PRODUCTS = [
    # Электроника
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
    
    # Одежда
    {"name": "Джинсы Levi's 501", "category": "Джинсы", "price": 5990, "description": "Классические джинсы Levi's 501 из денима премиум качества"},
    {"name": "Кроссовки Nike Air Max 270", "category": "Обувь", "price": 12990, "description": "Спортивные кроссовки Nike с технологией Air Max"},
    {"name": "Куртка The North Face", "category": "Верхняя одежда", "price": 15990, "description": "Зимняя куртка The North Face с мембраной Gore-Tex"},
    {"name": "Рубашка Ralph Lauren", "category": "Рубашки", "price": 7990, "description": "Классическая рубашка Ralph Lauren из хлопка премиум качества"},
    {"name": "Платье Zara", "category": "Платья", "price": 3990, "description": "Элегантное платье Zara для особых случаев"},
    {"name": "Свитер Uniqlo", "category": "Свитеры", "price": 2990, "description": "Теплый свитер Uniqlo из мериносовой шерсти"},
    {"name": "Ботинки Timberland", "category": "Обувь", "price": 11990, "description": "Классические ботинки Timberland из натуральной кожи"},
    {"name": "Шорты Adidas", "category": "Шорты", "price": 1990, "description": "Спортивные шорты Adidas с технологией ClimaLite"},
    
    # Дом и сад
    {"name": "Кофемашина De'Longhi", "category": "Кухонная техника", "price": 24990, "description": "Автоматическая кофемашина De'Longhi с капучинатором"},
    {"name": "Пылесос Dyson V15", "category": "Бытовая техника", "price": 39990, "description": "Беспроводной пылесос Dyson V15 с лазерной технологией"},
    {"name": "Холодильник Samsung", "category": "Крупная техника", "price": 89990, "description": "Двухкамерный холодильник Samsung с технологией No Frost"},
    {"name": "Стиральная машина LG", "category": "Крупная техника", "price": 49990, "description": "Стиральная машина LG с загрузкой 7 кг и технологией Direct Drive"},
    {"name": "Микроволновка Panasonic", "category": "Кухонная техника", "price": 8990, "description": "Микроволновая печь Panasonic с функцией гриль"},
    {"name": "Блендер Philips", "category": "Кухонная техника", "price": 5990, "description": "Мощный блендер Philips для приготовления смузи и коктейлей"},
    {"name": "Утюг Tefal", "category": "Бытовая техника", "price": 3990, "description": "Паровой утюг Tefal с технологией самоочистки"},
    {"name": "Фен Dyson Supersonic", "category": "Красота и здоровье", "price": 29990, "description": "Фен Dyson Supersonic с технологией цифрового двигателя"},
    
    # Спорт
    {"name": "Гантели 20кг", "category": "Спортивные товары", "price": 4990, "description": "Разборные гантели 20кг для домашних тренировок"},
    {"name": "Беговая дорожка NordicTrack", "category": "Кардио тренажеры", "price": 79990, "description": "Электрическая беговая дорожка NordicTrack с наклоном"},
    {"name": "Велосипед Trek", "category": "Велосипеды", "price": 59990, "description": "Горный велосипед Trek с алюминиевой рамой"},
    {"name": "Йога-мат Liforme", "category": "Йога и фитнес", "price": 3990, "description": "Профессиональный йога-мат Liforme с анатомическими линиями"},
    {"name": "Кроссовки Adidas Ultraboost", "category": "Спортивная обувь", "price": 14990, "description": "Беговые кроссовки Adidas Ultraboost с технологией Boost"},
    {"name": "Спортивный костюм Nike", "category": "Спортивная одежда", "price": 7990, "description": "Спортивный костюм Nike из дышащей ткани Dri-FIT"},
    {"name": "Гиря 16кг", "category": "Спортивные товары", "price": 2990, "description": "Чугунная гиря 16кг для силовых тренировок"},
    {"name": "Скакалка Adidas", "category": "Спортивные товары", "price": 990, "description": "Скоростная скакалка Adidas с регулируемой длиной"},
    
    # Книги
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

def get_or_create_category(name):
    """Создание категории"""
    category, created = Category.objects.get_or_create(
        slug=name.lower().replace(' ', '-').replace('ё', 'e'),
        defaults={'icon': 'tag'}
    )
    if created:
        category.set_current_language('ru')
        category.name = name
        category.description = f'Категория {name}'
        category.save()
        print(f"Создана категория: {name}")
    return category

def get_or_create_seller():
    """Создание продавца"""
    seller, created = Seller.objects.get_or_create(
        company_name="OZON Marketplace",
        defaults={
            'description': 'Официальный маркетплейс OZON',
        }
    )
    if created:
        print(f"Создан продавец: {seller.company_name}")
    return seller

def get_or_create_shop():
    """Создание магазина"""
    shop, created = Shop.objects.get_or_create(
        phone="+7 (495) 232-32-32",
        defaults={
            'email': 'store@ozon.ru',
        }
    )
    if created:
        shop.set_current_language('ru')
        shop.name = "OZON Store"
        shop.address = "Москва, ул. Льва Толстого, 16"
        shop.city = "Москва"
        shop.save()
        print(f"Создан магазин: {shop.name}")
    return shop

def download_image(url):
    """Загрузка изображения"""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        img_data = BytesIO(response.content)
        Image.open(img_data).verify()
        return img_data
    except (requests.exceptions.RequestException, IOError, Image.UnidentifiedImageError) as e:
        print(f"Ошибка при загрузке изображения с {url}: {e}")
        return None

def create_real_products():
    """Создание реальных товаров"""
    print("🚀 Начинаем создание реальных товаров...")
    
    # Создаем продавца и магазин
    seller = get_or_create_seller()
    shop = get_or_create_shop()
    
    products_created = 0
    
    for i, product_data in enumerate(REAL_PRODUCTS):
        try:
            # Создаем категорию
            category = get_or_create_category(product_data['category'])
            
            # Генерируем SKU
            sku = f"OZON-{fake.unique.random_number(digits=6)}"
            
            # Создаем товар
            product = Product.objects.create(
                category=category,
                seller=seller,
                currency='RUB',
                price=Decimal(product_data['price']),
                discount_price=Decimal(product_data['price'] * 0.8) if random.random() < 0.3 else None,
                sku=sku,
                stock_quantity=random.randint(10, 100),
                is_active=True,
                rating=Decimal(random.uniform(4.0, 5.0)).quantize(Decimal('0.01')),
                reviews_count=random.randint(5, 150),
                views_count=random.randint(100, 1000),
            )
            
            # Устанавливаем переводы
            product.set_current_language('ru')
            product.name = product_data['name']
            product.description = product_data['description']
            product.save()
            
            # Добавляем магазин
            product.shops.add(shop)
            
            # Добавляем характеристики
            characteristics = [
                ("Бренд", product_data['name'].split()[0]),
                ("Страна", random.choice(["Россия", "Китай", "Германия", "Япония", "США", "Южная Корея"])),
                ("Гарантия", random.choice(["6 месяцев", "1 год", "2 года", "3 года"])),
                ("Вес", f"{random.randint(100, 5000)} г"),
                ("Цвет", random.choice(["Черный", "Белый", "Серый", "Красный", "Синий", "Зеленый"])),
            ]
            
            for char_name, char_value in characteristics:
                ProductCharacteristic.objects.create(
                    product=product,
                    name=char_name,
                    value=char_value
                )
            
            # Добавляем изображения
            image_url = REAL_IMAGE_URLS[i % len(REAL_IMAGE_URLS)]
            img_data = download_image(image_url)
            if img_data:
                image_name = f"{product.slug}_{fake.uuid4()}.jpg"
                product_image = ProductImage(product=product)
                product_image.image.save(image_name, img_data, save=True)
                product_image.save()
                print(f"✅ Добавлено изображение для {product.name}")
            
            products_created += 1
            print(f"✅ Создан товар: {product.name} - {product.price} ₽")
            
        except Exception as e:
            print(f"❌ Ошибка при создании товара {product_data['name']}: {e}")
    
    print(f"\n🎉 Готово! Создано {products_created} реальных товаров с настоящими фотографиями!")
    return products_created

if __name__ == '__main__':
    create_real_products()
