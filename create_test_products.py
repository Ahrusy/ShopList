#!/usr/bin/env python
"""
Скрипт для создания 500 тестовых товаров с полными данными
"""
import os
import sys
import django
from decimal import Decimal
import random
from faker import Faker
import requests
from io import BytesIO
from PIL import Image

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shoplist.settings')
django.setup()

from products.models import (
    Product, Category, Shop, Tag, Seller, ProductImage, 
    ProductCharacteristic, User
)

fake = Faker('ru_RU')

# Список категорий товаров с подкатегориями
CATEGORIES_DATA = {
    'Электроника': {
        'Смартфоны': ['iPhone', 'Samsung Galaxy', 'Xiaomi', 'Huawei'],
        'Ноутбуки': ['Игровые', 'Офисные', 'Ультрабуки', 'MacBook'],
        'Планшеты': ['iPad', 'Android планшеты', 'Windows планшеты'],
        'Наушники': ['Беспроводные', 'Проводные', 'Игровые', 'Спортивные'],
        'Телевизоры': ['4K', '8K', 'OLED', 'QLED', 'Smart TV'],
    },
    'Одежда': {
        'Мужская одежда': ['Рубашки', 'Джинсы', 'Куртки', 'Футболки'],
        'Женская одежда': ['Платья', 'Блузки', 'Юбки', 'Брюки'],
        'Детская одежда': ['Для мальчиков', 'Для девочек', 'Для малышей'],
        'Обувь': ['Кроссовки', 'Туфли', 'Сапоги', 'Ботинки'],
        'Аксессуары': ['Сумки', 'Ремни', 'Шарфы', 'Шапки'],
    },
    'Дом и сад': {
        'Мебель': ['Диваны', 'Столы', 'Стулья', 'Шкафы'],
        'Бытовая техника': ['Холодильники', 'Стиральные машины', 'Пылесосы'],
        'Кухня': ['Посуда', 'Бытовая техника', 'Столовые приборы'],
        'Сад': ['Садовые инструменты', 'Растения', 'Горшки'],
        'Декор': ['Картины', 'Вазы', 'Свечи', 'Зеркала'],
    },
    'Спорт': {
        'Фитнес': ['Гантели', 'Коврики', 'Эспандеры', 'Велотренажеры'],
        'Туризм': ['Рюкзаки', 'Палатки', 'Спальники', 'Кемпинг'],
        'Зимний спорт': ['Лыжи', 'Сноуборды', 'Коньки', 'Санки'],
        'Летний спорт': ['Велосипеды', 'Ролики', 'Скейтборды'],
        'Командные игры': ['Футбол', 'Баскетбол', 'Волейбол', 'Теннис'],
    },
    'Красота и здоровье': {
        'Косметика': ['Макияж', 'Уход за кожей', 'Парфюмерия'],
        'Уход за волосами': ['Шампуни', 'Кондиционеры', 'Маски'],
        'Гигиена': ['Зубные щетки', 'Мыло', 'Дезодоранты'],
        'Здоровье': ['Витамины', 'Термометры', 'Тонометры'],
        'Маникюр': ['Лаки', 'Инструменты', 'Накладные ногти'],
    },
    'Детские товары': {
        'Игрушки': ['Конструкторы', 'Куклы', 'Машинки', 'Настольные игры'],
        'Детская мебель': ['Кроватки', 'Столики', 'Стульчики'],
        'Питание': ['Смеси', 'Каши', 'Пюре', 'Соки'],
        'Одежда': ['Для новорожденных', 'Для малышей', 'Для школьников'],
        'Развитие': ['Книги', 'Пазлы', 'Обучающие игры'],
    },
    'Автотовары': {
        'Запчасти': ['Двигатель', 'Тормоза', 'Подвеска', 'Электрика'],
        'Масла и жидкости': ['Моторное масло', 'Тормозная жидкость', 'Антифриз'],
        'Аксессуары': ['Чехлы', 'Коврики', 'Автозеркала', 'Автомагнитолы'],
        'Инструменты': ['Домкраты', 'Наборы ключей', 'Компрессоры'],
        'Уход': ['Автошампуни', 'Полироли', 'Воски', 'Щетки'],
    },
    'Книги': {
        'Художественная литература': ['Романы', 'Детективы', 'Фантастика', 'Классика'],
        'Детские книги': ['Сказки', 'Энциклопедии', 'Раскраски'],
        'Учебная литература': ['Школьные учебники', 'ВУЗ', 'Справочники'],
        'Бизнес': ['Маркетинг', 'Финансы', 'Управление', 'Карьера'],
        'Хобби': ['Рукоделие', 'Кулинария', 'Сад', 'Спорт'],
    }
}

# Технические характеристики для разных категорий
TECH_SPECS = {
    'Смартфоны': {
        'Экран': ['6.1"', '6.7"', '5.8"', '6.5"'],
        'Память': ['64 ГБ', '128 ГБ', '256 ГБ', '512 ГБ'],
        'ОЗУ': ['4 ГБ', '6 ГБ', '8 ГБ', '12 ГБ'],
        'Камера': ['12 МП', '48 МП', '64 МП', '108 МП'],
        'Батарея': ['3000 мАч', '4000 мАч', '5000 мАч'],
        'Процессор': ['Snapdragon 888', 'A15 Bionic', 'Exynos 2100']
    },
    'Ноутбуки': {
        'Экран': ['13.3"', '15.6"', '17.3"'],
        'Процессор': ['Intel i5', 'Intel i7', 'AMD Ryzen 5', 'AMD Ryzen 7'],
        'ОЗУ': ['8 ГБ', '16 ГБ', '32 ГБ'],
        'SSD': ['256 ГБ', '512 ГБ', '1 ТБ'],
        'Видеокарта': ['Intel UHD', 'NVIDIA GTX 1650', 'NVIDIA RTX 3060'],
        'ОС': ['Windows 11', 'macOS', 'Linux']
    },
    'Телевизоры': {
        'Диагональ': ['32"', '43"', '55"', '65"', '75"'],
        'Разрешение': ['HD', 'Full HD', '4K', '8K'],
        'Тип экрана': ['LED', 'OLED', 'QLED'],
        'Smart TV': ['Да', 'Нет'],
        'HDR': ['HDR10', 'HDR10+', 'Dolby Vision'],
        'Частота': ['60 Гц', '120 Гц', '240 Гц']
    }
}

def create_categories():
    """Создание категорий и подкатегорий"""
    categories_created = 0
    
    for main_cat, subcats in CATEGORIES_DATA.items():
        # Создаем главную категорию
        main_category, created = Category.objects.get_or_create(
            slug=main_cat.lower().replace(' ', '-'),
            defaults={
                'icon': 'tag'
            }
        )
        if created:
            # Устанавливаем переводы
            main_category.set_current_language('ru')
            main_category.name = main_cat
            main_category.description = f'Категория {main_cat}'
            main_category.save()
            categories_created += 1
            print(f"Создана категория: {main_cat}")
        
        # Создаем подкатегории
        for subcat, items in subcats.items():
            subcat_slug = f"{main_cat.lower().replace(' ', '-')}-{subcat.lower().replace(' ', '-')}"
            sub_category, created = Category.objects.get_or_create(
                slug=subcat_slug,
                parent=main_category,
                defaults={
                    'icon': 'folder'
                }
            )
            if created:
                # Устанавливаем переводы
                sub_category.set_current_language('ru')
                sub_category.name = subcat
                sub_category.description = f'Подкатегория {subcat}'
                sub_category.save()
                categories_created += 1
                print(f"Создана подкатегория: {subcat}")
            
            # Создаем товары в подкатегории
            for item in items:
                item_slug = f"{subcat_slug}-{item.lower().replace(' ', '-')}"
                item_category, created = Category.objects.get_or_create(
                    slug=item_slug,
                    parent=sub_category,
                    defaults={
                        'icon': 'cube'
                    }
                )
                if created:
                    # Устанавливаем переводы
                    item_category.set_current_language('ru')
                    item_category.name = item
                    item_category.description = f'Товар {item}'
                    item_category.save()
                    categories_created += 1
                    print(f"Создана категория товара: {item}")
    
    return categories_created

def create_tags():
    """Создание тегов"""
    tags_data = [
        'новинка', 'скидка', 'хит продаж', 'премиум', 'бюджетный',
        'качественный', 'популярный', 'эксклюзивный', 'топ', 'рекомендуем'
    ]
    
    tags_created = 0
    for tag_name in tags_data:
        # Проверяем, существует ли тег с таким именем
        existing_tags = Tag.objects.filter(translations__name=tag_name)
        if not existing_tags.exists():
            # Создаем новый тег
            tag = Tag.objects.create()
            tag.set_current_language('ru')
            tag.name = tag_name
            tag.save()
            tags_created += 1
    
    return tags_created

def generate_product_data(category):
    """Генерация данных для товара"""
    # Определяем тип товара по категории
    category_path = []
    current = category
    while current:
        category_path.append(current.name)
        current = current.parent
    
    category_path.reverse()
    
    # Генерируем название товара
    if len(category_path) >= 3:
        product_name = f"{category_path[-1]} {fake.word().title()}"
    else:
        product_name = f"{category.name} {fake.word().title()}"
    
    # Генерируем описание
    description = f"""
    {product_name} - это качественный товар, который идеально подходит для ваших потребностей.
    
    Основные особенности:
    • Высокое качество материалов
    • Современный дизайн
    • Долговечность использования
    • Простота в уходе
    
    {fake.text(max_nb_chars=200)}
    """
    
    # Генерируем цену
    base_price = random.randint(500, 50000)
    discount_price = None
    if random.choice([True, False]):
        discount_price = base_price * Decimal('0.8')  # 20% скидка
    
    # Генерируем SKU
    sku = f"SKU-{random.randint(100000, 999999)}"
    
    return {
        'name': product_name,
        'description': description.strip(),
        'price': Decimal(str(base_price)),
        'discount_price': discount_price,
        'sku': sku,
        'stock_quantity': random.randint(0, 100),
        'is_active': True,
        'rating': Decimal(str(round(random.uniform(3.0, 5.0), 2))),
        'reviews_count': random.randint(0, 100)
    }

def create_technical_characteristics(product, category):
    """Создание технических характеристик"""
    category_path = []
    current = category
    while current:
        category_path.append(current.name)
        current = current.parent
    
    category_path.reverse()
    
    # Определяем тип характеристик по категории
    specs = {}
    for cat_name in category_path:
        if cat_name in TECH_SPECS:
            specs.update(TECH_SPECS[cat_name])
            break
    
    # Если специфических характеристик нет, создаем общие
    if not specs:
        specs = {
            'Материал': ['Пластик', 'Металл', 'Дерево', 'Ткань'],
            'Цвет': ['Черный', 'Белый', 'Серый', 'Красный', 'Синий'],
            'Размер': ['S', 'M', 'L', 'XL'],
            'Вес': ['100г', '500г', '1кг', '2кг'],
            'Страна': ['Россия', 'Китай', 'Германия', 'Япония']
        }
    
    # Создаем характеристики
    for spec_name, values in specs.items():
        ProductCharacteristic.objects.create(
            product=product,
            name=spec_name,
            value=random.choice(values)
        )

def create_product_images(product):
    """Создание изображений товара"""
    # Создаем 1-3 изображения для товара
    num_images = random.randint(1, 3)
    
    for i in range(num_images):
        # Создаем простое изображение-заглушку
        img = Image.new('RGB', (400, 400), color=(
            random.randint(100, 255),
            random.randint(100, 255),
            random.randint(100, 255)
        ))
        
        # Сохраняем в BytesIO
        img_io = BytesIO()
        img.save(img_io, format='JPEG')
        img_io.seek(0)
        
        # Создаем объект ProductImage
        ProductImage.objects.create(
            product=product,
            image=f'products/{product.sku}_image_{i+1}.jpg',
            alt_text=f'{product.name} - изображение {i+1}',
            is_main=(i == 0)
        )

def create_products():
    """Создание товаров"""
    # Получаем необходимые объекты
    seller = Seller.objects.first()
    shop = Shop.objects.first()
    tags = list(Tag.objects.all())
    
    if not seller or not shop:
        print("Ошибка: Нет продавца или магазина в базе данных")
        return 0
    
    # Получаем все категории товаров (3-й уровень)
    product_categories = Category.objects.filter(parent__parent__isnull=False)
    
    if not product_categories.exists():
        print("Ошибка: Нет категорий товаров")
        return 0
    
    products_created = 0
    target_products = 500
    
    print(f"Начинаем создание {target_products} товаров...")
    
    for i in range(target_products):
        try:
            # Выбираем случайную категорию
            category = random.choice(product_categories)
            
            # Генерируем данные товара
            product_data = generate_product_data(category)
            
            # Создаем товар
            product = Product.objects.create(
                category=category,
                seller=seller,
                currency='RUB',
                price=product_data['price'],
                discount_price=product_data['discount_price'],
                sku=product_data['sku'],
                stock_quantity=product_data['stock_quantity'],
                is_active=product_data['is_active'],
                rating=product_data['rating'],
                reviews_count=product_data['reviews_count']
            )
            
            # Устанавливаем переводы
            product.set_current_language('ru')
            product.name = product_data['name']
            product.description = product_data['description']
            product.save()
            
            # Добавляем магазин
            product.shops.add(shop)
            
            # Добавляем случайные теги
            product_tags = random.sample(tags, random.randint(1, 3))
            product.tags.set(product_tags)
            
            # Создаем технические характеристики
            create_technical_characteristics(product, category)
            
            # Создаем изображения
            create_product_images(product)
            
            products_created += 1
            
            if products_created % 50 == 0:
                print(f"Создано товаров: {products_created}/{target_products}")
                
        except Exception as e:
            print(f"Ошибка при создании товара {i+1}: {e}")
            continue
    
    return products_created

def main():
    """Основная функция"""
    print("🚀 Начинаем создание тестовых данных...")
    
    # Создаем категории
    print("\n📁 Создание категорий...")
    categories_count = create_categories()
    print(f"Создано категорий: {categories_count}")
    
    # Создаем теги
    print("\n🏷️ Создание тегов...")
    tags_count = create_tags()
    print(f"Создано тегов: {tags_count}")
    
    # Создаем товары
    print("\n📦 Создание товаров...")
    products_count = create_products()
    print(f"Создано товаров: {products_count}")
    
    print(f"\n✅ Готово! Создано:")
    print(f"   - Категорий: {categories_count}")
    print(f"   - Тегов: {tags_count}")
    print(f"   - Товаров: {products_count}")

if __name__ == '__main__':
    main()