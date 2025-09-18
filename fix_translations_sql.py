#!/usr/bin/env python
"""
Скрипт для исправления переводов товаров через raw SQL
"""
import os
import sys
import django
from faker import Faker

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shoplist.settings')
django.setup()

from django.db import connection

fake = Faker('ru_RU')

def fix_translations_with_sql():
    """Исправление переводов товаров через raw SQL"""
    with connection.cursor() as cursor:
        # Получаем все товары без переводов
        cursor.execute("""
            SELECT p.id, p.sku, p.price 
            FROM products_product p
            LEFT JOIN products_product_translation pt ON p.id = pt.master_id AND pt.language_code = 'ru'
            WHERE pt.master_id IS NULL
            LIMIT 100
        """)
        
        products = cursor.fetchall()
        print(f"Найдено товаров без переводов: {len(products)}")
        
        fixed_count = 0
        
        for product_id, sku, price in products:
            try:
                # Генерируем название и описание
                product_name = f"Товар {product_id}"
                description = f"Описание товара {product_id}. Качественный товар для ваших потребностей. Цена: {price} руб."
                
                # Создаем перевод через raw SQL
                cursor.execute("""
                    INSERT INTO products_product_translation (master_id, language_code, name, description)
                    VALUES (%s, %s, %s, %s)
                """, [product_id, 'ru', product_name, description])
                
                fixed_count += 1
                
                if fixed_count % 50 == 0:
                    print(f"Исправлено товаров: {fixed_count}")
                    
            except Exception as e:
                print(f"Ошибка при исправлении товара {product_id}: {e}")
                continue
        
        return fixed_count

def main():
    """Основная функция"""
    print("🚀 Начинаем исправление переводов товаров через SQL...")
    
    fixed_count = fix_translations_with_sql()
    
    print(f"\n✅ Готово! Исправлено товаров: {fixed_count}")

if __name__ == '__main__':
    main()

