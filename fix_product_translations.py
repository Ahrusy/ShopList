#!/usr/bin/env python
"""
Скрипт для исправления переводов товаров
"""
import os
import sys
import django
from faker import Faker

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shoplist.settings')
django.setup()

from products.models import Product

fake = Faker('ru_RU')

def fix_translations():
    """Исправление переводов товаров"""
    products = Product.objects.all()
    fixed_count = 0
    
    print(f"Найдено товаров: {products.count()}")
    
    for product in products:
        try:
            # Проверяем, есть ли перевод
            try:
                name = product.name
                if not name or name.strip() == '':
                    raise Exception("No translation")
            except:
                # Создаем перевод
                product.set_current_language('ru')
                product.name = f"Товар {product.id}"
                product.description = f"Описание товара {product.id}. Качественный товар для ваших потребностей."
                product.save()
                fixed_count += 1
                
                if fixed_count % 100 == 0:
                    print(f"Исправлено товаров: {fixed_count}")
                    
        except Exception as e:
            print(f"Ошибка при исправлении товара {product.id}: {e}")
            continue
    
    return fixed_count

def main():
    """Основная функция"""
    print("🚀 Начинаем исправление переводов товаров...")
    
    fixed_count = fix_translations()
    
    print(f"\n✅ Готово! Исправлено товаров: {fixed_count}")

if __name__ == '__main__':
    main()
