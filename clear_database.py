#!/usr/bin/env python
"""
Скрипт для полной очистки базы данных от товаров
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shoplist.settings')
django.setup()

from django.db import connection

def clear_database():
    """Очистка всей базы данных от товаров"""
    print("🧹 Начинаем очистку базы данных...")
    
    with connection.cursor() as cursor:
        # Удаляем все товары и связанные данные
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
        ]
        
        for table in tables_to_clear:
            try:
                cursor.execute(f"DELETE FROM {table}")
                print(f"✅ Очищена таблица: {table}")
            except Exception as e:
                print(f"❌ Ошибка при очистке {table}: {e}")
        
        # Сбрасываем счетчики автоинкремента
        cursor.execute("ALTER SEQUENCE products_product_id_seq RESTART WITH 1")
        cursor.execute("ALTER SEQUENCE products_category_id_seq RESTART WITH 1")
        cursor.execute("ALTER SEQUENCE products_seller_id_seq RESTART WITH 1")
        cursor.execute("ALTER SEQUENCE products_shop_id_seq RESTART WITH 1")
        cursor.execute("ALTER SEQUENCE products_tag_id_seq RESTART WITH 1")
        
        print("✅ Счетчики автоинкремента сброшены")
        
        # Проверяем количество записей
        cursor.execute("SELECT COUNT(*) FROM products_product")
        product_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM products_category")
        category_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM products_seller")
        seller_count = cursor.fetchone()[0]
        
        print(f"\n📊 Статистика после очистки:")
        print(f"  - Товары: {product_count}")
        print(f"  - Категории: {category_count}")
        print(f"  - Продавцы: {seller_count}")
        
        print("\n🎉 База данных полностью очищена!")

if __name__ == '__main__':
    clear_database()

