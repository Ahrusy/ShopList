#!/usr/bin/env python
"""
Мощный скрипт для полной очистки базы данных
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shoplist.settings')
django.setup()

from django.db import connection
from django.contrib.auth import get_user_model

User = get_user_model()

def clear_all_database():
    """Полная очистка базы данных"""
    print("🧹 Начинаем ПОЛНУЮ очистку базы данных...")
    
    with connection.cursor() as cursor:
        # Отключаем проверки внешних ключей
        cursor.execute("SET session_replication_role = replica;")
        
        # Список всех таблиц для очистки
        tables_to_clear = [
            'products_productcharacteristic',
            'products_productimage', 
            'products_product_translation',
            'products_product_tags',
            'products_product',
            'products_category_translation',
            'products_category',
            'products_seller',
            'products_shop_translation',
            'products_shop',
            'products_tag_translation',
            'products_tag',
            'products_review',
            'products_orderitem',
            'products_order',
            'products_cartitem',
            'products_cart',
            'products_commission',
            'products_promocode',
            'products_notification',
            'products_userlocation',
            'products_location',
            'products_page_translation',
            'products_page',
            'products_pagecategory_translation',
            'products_pagecategory',
        ]
        
        for table in tables_to_clear:
            try:
                cursor.execute(f"TRUNCATE TABLE {table} RESTART IDENTITY CASCADE;")
                print(f"✅ Очищена таблица: {table}")
            except Exception as e:
                print(f"❌ Ошибка при очистке {table}: {e}")
        
        # Очищаем пользователей (кроме суперпользователя)
        try:
            cursor.execute("DELETE FROM products_user WHERE is_superuser = FALSE;")
            print("✅ Очищены обычные пользователи")
        except Exception as e:
            print(f"❌ Ошибка при очистке пользователей: {e}")
        
        # Включаем обратно проверки внешних ключей
        cursor.execute("SET session_replication_role = DEFAULT;")
        
        # Проверяем количество записей
        cursor.execute("SELECT COUNT(*) FROM products_product")
        product_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM products_category")
        category_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM products_seller")
        seller_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM products_user")
        user_count = cursor.fetchone()[0]
        
        print(f"\n📊 Статистика после ПОЛНОЙ очистки:")
        print(f"  - Товары: {product_count}")
        print(f"  - Категории: {category_count}")
        print(f"  - Продавцы: {seller_count}")
        print(f"  - Пользователи: {user_count}")
        
        print("\n🎉 База данных ПОЛНОСТЬЮ очищена!")

if __name__ == '__main__':
    clear_all_database()

