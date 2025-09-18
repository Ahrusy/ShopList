#!/usr/bin/env python
"""
Скрипт для создания 500 товаров с характеристиками и изображениями
"""
import os
import django
import random
from faker import Faker
import uuid

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shoplist.settings')
django.setup()

from products.models import Category, Product, ProductCharacteristic, ProductImage, Seller, User

fake = Faker('ru_RU')

def create_products():
    print("🚀 Создаем 500 товаров...")
    
    # Создаем пользователя для продавца
    user, user_created = User.objects.get_or_create(
        username="seller_user",
        defaults={
            'email': 'seller@example.com',
            'first_name': 'Продавец',
            'last_name': 'Магазин',
            'role': 'seller'
        }
    )
    
    # Получаем продавца по умолчанию
    seller, seller_created = Seller.objects.get_or_create(
        user=user,
        defaults={
            'company_name': "Интернет-магазин",
            'description': "Онлайн магазин с широким ассортиментом",
            'commission_rate': 5.0
        }
    )
    
    # Получаем все категории 2-го уровня
    categories = Category.objects.all()
    level2_categories = [cat for cat in categories if cat.level == 2]
    
    if not level2_categories:
        print("⚠️ Нет категорий 2-го уровня! Создайте их перед запуском скрипта")
        return
    
    from django.db.models.signals import post_save
    from products.models import update_product_search_vector, update_product_rating

    # Отключаем сигналы, которые вызывают ошибки
    post_save.disconnect(update_product_search_vector, sender=Product)
    post_save.disconnect(update_product_rating, sender=Review)

    products_created = 0
    
    for _ in range(500):
        try:
            # Выбираем случайную категорию 2-го уровня
            category = random.choice(level2_categories)
            
            # Генерируем данные товара
            product_name = fake.catch_phrase()
            
            # Создаем товар с обязательными полями
            product = Product(
                name=product_name,
                description=fake.paragraph(nb_sentences=5),
                price=random.randint(100, 100000),
                currency='RUB',
                category=category,
                seller=seller,
                sku=f"PRD-{uuid.uuid4().hex[:8].upper()}",
                stock_quantity=random.randint(5, 100),
                is_active=True,
                rating=round(random.uniform(3.5, 5.0), 2),
                reviews_count=0,
                views_count=0
            )
            product.save()
            
            # Создаем характеристики
            characteristics = [
                {"name": "Материал", "value": fake.word(), "unit": ""},
                {"name": "Размер", "value": f"{random.randint(1, 100)}x{random.randint(1, 100)}", "unit": "см"},
                {"name": "Вес", "value": random.randint(100, 5000), "unit": "г"},
                {"name": "Цвет", "value": fake.color_name(), "unit": ""}
            ]
            
            for char in characteristics:
                ProductCharacteristic.objects.create(
                    product=product,
                    name=char["name"],
                    value=char["value"],
                    unit=char["unit"]
                )
            
            # Создаем изображения-заглушки
            for i in range(random.randint(1, 5)):
                ProductImage.objects.create(
                    product=product,
                    alt_text=f"Изображение товара {product_name}",
                    is_primary=(i == 0),
                    order=i
                )
            
            products_created += 1
            print(f"✅ Создан товар: {product_name}")
            
        except Exception as e:
            print(f"❌ Ошибка при создании товара: {e}")
    
    print(f"\n🎉 Успешно создано {products_created} товаров!")

    # Включаем сигналы обратно
    post_save.connect(update_product_search_vector, sender=Product)
    post_save.connect(update_product_rating, sender=Review)

if __name__ == '__main__':
    create_products()