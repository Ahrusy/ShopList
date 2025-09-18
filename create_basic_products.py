#!/usr/bin/env python
"""
Базовый скрипт для создания товаров без сложных запросов
"""
import os
import sys
import django
from decimal import Decimal
import random
from faker import Faker

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shoplist.settings')
django.setup()

from products.models import Product, Category, Shop, Seller, ProductImage, ProductCharacteristic

fake = Faker('ru_RU')

def create_basic_products():
    """Создание базовых товаров"""
    # Получаем необходимые объекты
    seller = Seller.objects.first()
    shop = Shop.objects.first()
    
    if not seller or not shop:
        print("Ошибка: Нет продавца или магазина в базе данных")
        return 0
    
    # Получаем все категории простым способом
    categories = Category.objects.all()
    if not categories.exists():
        print("Ошибка: Нет категорий в базе данных")
        return 0
    
    products_created = 0
    target_products = 500
    
    print(f"Начинаем создание {target_products} товаров...")
    
    # Список названий товаров
    product_names = [
        'Смартфон', 'Ноутбук', 'Планшет', 'Наушники', 'Телевизор',
        'Рубашка', 'Джинсы', 'Куртка', 'Платье', 'Кроссовки',
        'Диван', 'Стол', 'Стул', 'Холодильник', 'Стиральная машина',
        'Гантели', 'Велосипед', 'Лыжи', 'Книга', 'Игрушка',
        'Косметика', 'Шампунь', 'Зубная щетка', 'Витамины', 'Лак для ногтей',
        'Автомобильные запчасти', 'Моторное масло', 'Автомагнитола', 'Домкрат', 'Автошампунь'
    ]
    
    for i in range(target_products):
        try:
            # Выбираем случайную категорию
            category = random.choice(list(categories))
            
            # Генерируем название товара
            base_name = random.choice(product_names)
            product_name = f"{base_name} {fake.word().title()} {random.randint(1, 999)}"
            
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
            
            # Создаем товар
            product = Product.objects.create(
                category=category,
                seller=seller,
                currency='RUB',
                price=Decimal(str(base_price)),
                discount_price=discount_price,
                sku=sku,
                stock_quantity=random.randint(0, 100),
                is_active=True,
                rating=Decimal(str(round(random.uniform(3.0, 5.0), 2))),
                reviews_count=random.randint(0, 100)
            )
            
            # Устанавливаем переводы
            product.set_current_language('ru')
            product.name = product_name
            product.description = description.strip()
            product.save()
            
            # Добавляем магазин через raw SQL
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO products_product_shops (product_id, shop_id) VALUES (%s, %s)",
                    [product.id, shop.id]
                )
            
            # Создаем технические характеристики
            create_characteristics(product)
            
            # Создаем изображения
            create_images(product)
            
            products_created += 1
            
            if products_created % 50 == 0:
                print(f"Создано товаров: {products_created}/{target_products}")
                
        except Exception as e:
            print(f"Ошибка при создании товара {i+1}: {e}")
            continue
    
    return products_created

def create_characteristics(product):
    """Создание технических характеристик"""
    characteristics = [
        ('Материал', ['Пластик', 'Металл', 'Дерево', 'Ткань', 'Стекло']),
        ('Цвет', ['Черный', 'Белый', 'Серый', 'Красный', 'Синий', 'Зеленый']),
        ('Размер', ['S', 'M', 'L', 'XL', 'XXL']),
        ('Вес', ['100г', '500г', '1кг', '2кг', '5кг']),
        ('Страна', ['Россия', 'Китай', 'Германия', 'Япония', 'США']),
        ('Гарантия', ['6 месяцев', '1 год', '2 года', '3 года']),
        ('Бренд', ['Samsung', 'Apple', 'Xiaomi', 'Huawei', 'LG']),
        ('Модель', ['2023', '2024', 'Pro', 'Max', 'Ultra'])
    ]
    
    # Создаем 3-5 характеристик для каждого товара
    num_chars = random.randint(3, 5)
    selected_chars = random.sample(characteristics, num_chars)
    
    for char_name, values in selected_chars:
        ProductCharacteristic.objects.create(
            product=product,
            name=char_name,
            value=random.choice(values)
        )

def create_images(product):
    """Создание изображений товара"""
    # Создаем 1-3 изображения для товара
    num_images = random.randint(1, 3)
    
    for i in range(num_images):
        ProductImage.objects.create(
            product=product,
            image=f'products/{product.sku}_image_{i+1}.jpg',
            alt_text=f'{product.name} - изображение {i+1}',
            is_main=(i == 0)
        )

def main():
    """Основная функция"""
    print("🚀 Начинаем создание товаров...")
    
    products_count = create_basic_products()
    
    print(f"\n✅ Готово! Создано товаров: {products_count}")

if __name__ == '__main__':
    main()

