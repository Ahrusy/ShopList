#!/usr/bin/env python
"""
Скрипт для проверки созданных 500 товаров
"""
import sqlite3
import logging

# Настройка логгера
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('check_500_products.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def check_database_stats(conn):
    """Проверяет статистику базы данных"""
    print("=== СТАТИСТИКА БАЗЫ ДАННЫХ ===")
    
    cursor = conn.cursor()
    
    # Подсчитываем товары
    cursor.execute("SELECT COUNT(*) FROM products")
    total_products = cursor.fetchone()[0]
    
    # Подсчитываем категории
    cursor.execute("SELECT COUNT(*) FROM categories")
    total_categories = cursor.fetchone()[0]
    
    # Подсчитываем характеристики
    cursor.execute("SELECT COUNT(*) FROM product_characteristics")
    total_characteristics = cursor.fetchone()[0]
    
    # Подсчитываем продавцов
    cursor.execute("SELECT COUNT(*) FROM sellers")
    total_sellers = cursor.fetchone()[0]
    
    print(f"Товаров: {total_products}")
    print(f"Категорий: {total_categories}")
    print(f"Характеристик: {total_characteristics}")
    print(f"Продавцов: {total_sellers}")
    
    return total_products, total_categories, total_characteristics

def check_categories_hierarchy(conn):
    """Проверяет иерархию категорий"""
    print("\n=== ИЕРАРХИЯ КАТЕГОРИЙ ===")
    
    cursor = conn.cursor()
    
    # Получаем корневые категории
    cursor.execute("SELECT id, name FROM categories WHERE parent_id IS NULL ORDER BY sort_order, name")
    root_categories = cursor.fetchall()
    
    for root_id, root_name in root_categories:
        print(f"\n📁 {root_name}")
        
        # Получаем подкатегории 2-го уровня
        cursor.execute("SELECT id, name FROM categories WHERE parent_id = ? ORDER BY sort_order, name", (root_id,))
        subcategories = cursor.fetchall()
        
        for sub_id, sub_name in subcategories:
            print(f"  └── 📂 {sub_name}")
            
            # Получаем подкатегории 3-го уровня (если есть)
            cursor.execute("SELECT id, name FROM categories WHERE parent_id = ? ORDER BY sort_order, name", (sub_id,))
            sub_subcategories = cursor.fetchall()
            
            for sub_sub_id, sub_sub_name in sub_subcategories:
                print(f"      └── 📄 {sub_sub_name}")

def check_products_by_category(conn):
    """Проверяет товары по категориям"""
    print("\n=== ТОВАРЫ ПО КАТЕГОРИЯМ ===")
    
    cursor = conn.cursor()
    
    # Получаем корневые категории с количеством товаров
    cursor.execute("""
        SELECT c.id, c.name, COUNT(p.id) as product_count
        FROM categories c
        LEFT JOIN products p ON c.id = p.category_id
        WHERE c.parent_id IS NULL
        GROUP BY c.id, c.name
        ORDER BY c.sort_order, c.name
    """)
    root_categories = cursor.fetchall()
    
    for root_id, root_name, product_count in root_categories:
        print(f"\n📁 {root_name}: {product_count} товаров")
        
        # Получаем подкатегории с количеством товаров
        cursor.execute("""
            SELECT c.id, c.name, COUNT(p.id) as product_count
            FROM categories c
            LEFT JOIN products p ON c.id = p.category_id
            WHERE c.parent_id = ?
            GROUP BY c.id, c.name
            ORDER BY c.sort_order, c.name
        """, (root_id,))
        subcategories = cursor.fetchall()
        
        for sub_id, sub_name, sub_product_count in subcategories:
            if sub_product_count > 0:
                print(f"  └── 📂 {sub_name}: {sub_product_count} товаров")

def check_product_details(conn):
    """Проверяет детали товаров"""
    print("\n=== ДЕТАЛИ ТОВАРОВ ===")
    
    cursor = conn.cursor()
    
    # Показываем первые 5 товаров с характеристиками
    cursor.execute("""
        SELECT p.id, p.name, p.price, c.name as category_name, s.company_name
        FROM products p
        LEFT JOIN categories c ON p.category_id = c.id
        LEFT JOIN sellers s ON p.seller_id = s.id
        ORDER BY p.id
        LIMIT 5
    """)
    products = cursor.fetchall()
    
    for product_id, name, price, category_name, seller_name in products:
        print(f"\n🛍️ {name}")
        print(f"   Цена: {price} руб.")
        print(f"   Категория: {category_name or 'Не указана'}")
        print(f"   Продавец: {seller_name or 'Не указан'}")
        
        # Получаем рейтинг и отзывы
        cursor.execute("SELECT rating, reviews_count, stock_quantity FROM products WHERE id = ?", (product_id,))
        rating, reviews_count, stock_quantity = cursor.fetchone()
        print(f"   Рейтинг: {rating}")
        print(f"   Отзывов: {reviews_count}")
        print(f"   На складе: {stock_quantity}")
        
        # Показываем характеристики
        cursor.execute("""
            SELECT name, value, unit 
            FROM product_characteristics 
            WHERE product_id = ? 
            ORDER BY order_field, name 
            LIMIT 5
        """, (product_id,))
        characteristics = cursor.fetchall()
        
        if characteristics:
            print("   Характеристики:")
            for char_name, char_value, char_unit in characteristics:
                unit = f" {char_unit}" if char_unit else ""
                print(f"     • {char_name}: {char_value}{unit}")

def check_price_ranges(conn):
    """Проверяет диапазоны цен"""
    print("\n=== ДИАПАЗОНЫ ЦЕН ===")
    
    cursor = conn.cursor()
    
    # Получаем статистику цен
    cursor.execute("""
        SELECT 
            MIN(price) as min_price,
            MAX(price) as max_price,
            AVG(price) as avg_price
        FROM products
    """)
    min_price, max_price, avg_price = cursor.fetchone()
    
    print(f"Минимальная цена: {min_price:.2f} руб.")
    print(f"Максимальная цена: {max_price:.2f} руб.")
    print(f"Средняя цена: {avg_price:.2f} руб.")
    
    # Показываем товары в разных ценовых диапазонах
    ranges = [
        (0, 10000, "До 10,000 руб."),
        (10000, 50000, "10,000-50,000 руб."),
        (50000, 100000, "50,000-100,000 руб."),
        (100000, 200000, "100,000-200,000 руб."),
        (200000, float('inf'), "Свыше 200,000 руб.")
    ]
    
    for min_price, max_price, label in ranges:
        if max_price == float('inf'):
            cursor.execute("SELECT COUNT(*) FROM products WHERE price >= ?", (min_price,))
        else:
            cursor.execute("SELECT COUNT(*) FROM products WHERE price >= ? AND price < ?", (min_price, max_price))
        count = cursor.fetchone()[0]
        print(f"{label}: {count} товаров")

def check_top_products(conn):
    """Проверяет топ товары"""
    print("\n=== ТОП ТОВАРЫ ===")
    
    cursor = conn.cursor()
    
    # Топ по рейтингу
    print("\n🏆 Топ-5 товаров по рейтингу:")
    cursor.execute("""
        SELECT name, price, rating, reviews_count
        FROM products
        ORDER BY rating DESC, reviews_count DESC
        LIMIT 5
    """)
    top_rated = cursor.fetchall()
    
    for i, (name, price, rating, reviews_count) in enumerate(top_rated, 1):
        print(f"  {i}. {name} - {price} руб. (рейтинг: {rating}, отзывов: {reviews_count})")
    
    # Топ по цене
    print("\n💰 Топ-5 самых дорогих товаров:")
    cursor.execute("""
        SELECT name, price, rating
        FROM products
        ORDER BY price DESC
        LIMIT 5
    """)
    top_expensive = cursor.fetchall()
    
    for i, (name, price, rating) in enumerate(top_expensive, 1):
        print(f"  {i}. {name} - {price} руб. (рейтинг: {rating})")
    
    # Топ по количеству отзывов
    print("\n💬 Топ-5 товаров по количеству отзывов:")
    cursor.execute("""
        SELECT name, price, rating, reviews_count
        FROM products
        ORDER BY reviews_count DESC
        LIMIT 5
    """)
    top_reviewed = cursor.fetchall()
    
    for i, (name, price, rating, reviews_count) in enumerate(top_reviewed, 1):
        print(f"  {i}. {name} - {price} руб. (отзывов: {reviews_count}, рейтинг: {rating})")

def main():
    print("🔍 ПРОВЕРКА СОЗДАННЫХ 500 ТОВАРОВ")
    print("=" * 60)
    
    try:
        # Подключаемся к базе данных
        conn = sqlite3.connect('marketplace_500_products.db')
        
        # Проверяем статистику
        total_products, total_categories, total_characteristics = check_database_stats(conn)
        
        # Проверяем иерархию категорий
        check_categories_hierarchy(conn)
        
        # Проверяем товары по категориям
        check_products_by_category(conn)
        
        # Проверяем детали товаров
        check_product_details(conn)
        
        # Проверяем диапазоны цен
        check_price_ranges(conn)
        
        # Проверяем топ товары
        check_top_products(conn)
        
        # Закрываем соединение
        conn.close()
        
        print("\n" + "=" * 60)
        if total_products >= 500:
            print("✅ УСПЕХ: Создано 500+ товаров!")
        else:
            print(f"⚠️ ВНИМАНИЕ: Создано только {total_products} товаров из 500")
        
        print(f"📊 Итого: {total_products} товаров, {total_categories} категорий, {total_characteristics} характеристик")
        print("🎉 Проверка завершена успешно!")
        
    except Exception as e:
        print(f"❌ Ошибка при проверке: {e}")

if __name__ == "__main__":
    main()

