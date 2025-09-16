#!/usr/bin/env python
"""
Скрипт для проверки загруженных товаров
"""
import os
import sys
import django

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shoplist.settings_simple')
django.setup()

from products_simple.models import Category, Product, ProductCharacteristic, ProductImage, Seller

def check_database_stats():
    """Проверяет статистику базы данных"""
    print("=== СТАТИСТИКА БАЗЫ ДАННЫХ ===")
    
    total_products = Product.objects.count()
    total_categories = Category.objects.count()
    total_characteristics = ProductCharacteristic.objects.count()
    total_images = ProductImage.objects.count()
    total_sellers = Seller.objects.count()
    
    print(f"Товаров: {total_products}")
    print(f"Категорий: {total_categories}")
    print(f"Характеристик: {total_characteristics}")
    print(f"Изображений: {total_images}")
    print(f"Продавцов: {total_sellers}")
    
    return total_products, total_categories, total_characteristics

def check_categories_hierarchy():
    """Проверяет иерархию категорий"""
    print("\n=== ИЕРАРХИЯ КАТЕГОРИЙ ===")
    
    root_categories = Category.objects.filter(parent__isnull=True)
    
    for root in root_categories:
        print(f"\n📁 {root.name} (уровень {root.level})")
        
        # Подкатегории 2-го уровня
        subcategories = root.get_children()
        for sub in subcategories:
            print(f"  └── 📂 {sub.name} (уровень {sub.level})")
            
            # Подкатегории 3-го уровня (если есть)
            sub_subcategories = sub.get_children()
            for sub_sub in sub_subcategories:
                print(f"      └── 📄 {sub_sub.name} (уровень {sub_sub.level})")

def check_products_by_category():
    """Проверяет товары по категориям"""
    print("\n=== ТОВАРЫ ПО КАТЕГОРИЯМ ===")
    
    categories = Category.objects.filter(parent__isnull=True)
    
    for category in categories:
        products_count = Product.objects.filter(category=category).count()
        print(f"\n📁 {category.name}: {products_count} товаров")
        
        # Показываем подкатегории с количеством товаров
        subcategories = category.get_children()
        for sub in subcategories:
            sub_products_count = Product.objects.filter(category=sub).count()
            if sub_products_count > 0:
                print(f"  └── 📂 {sub.name}: {sub_products_count} товаров")

def check_product_details():
    """Проверяет детали товаров"""
    print("\n=== ДЕТАЛИ ТОВАРОВ ===")
    
    # Показываем первые 5 товаров с характеристиками
    products = Product.objects.all()[:5]
    
    for product in products:
        print(f"\n🛍️ {product.name}")
        print(f"   Цена: {product.price}₽")
        print(f"   Категория: {product.category.name if product.category else 'Не указана'}")
        print(f"   Продавец: {product.seller.company_name if product.seller else 'Не указан'}")
        print(f"   Рейтинг: {product.rating}")
        print(f"   Отзывов: {product.reviews_count}")
        print(f"   На складе: {product.stock_quantity}")
        
        # Показываем характеристики
        characteristics = ProductCharacteristic.objects.filter(product=product)[:5]
        if characteristics:
            print("   Характеристики:")
            for char in characteristics:
                unit = f" {char.unit}" if char.unit else ""
                print(f"     • {char.name}: {char.value}{unit}")

def check_price_ranges():
    """Проверяет диапазоны цен"""
    print("\n=== ДИАПАЗОНЫ ЦЕН ===")
    
    from django.db.models import Min, Max, Avg
    
    price_stats = Product.objects.aggregate(
        min_price=Min('price'),
        max_price=Max('price'),
        avg_price=Avg('price')
    )
    
    print(f"Минимальная цена: {price_stats['min_price']}₽")
    print(f"Максимальная цена: {price_stats['max_price']}₽")
    print(f"Средняя цена: {price_stats['avg_price']:.2f}₽")
    
    # Показываем товары в разных ценовых диапазонах
    ranges = [
        (0, 10000, "До 10,000₽"),
        (10000, 50000, "10,000-50,000₽"),
        (50000, 100000, "50,000-100,000₽"),
        (100000, 200000, "100,000-200,000₽"),
        (200000, float('inf'), "Свыше 200,000₽")
    ]
    
    for min_price, max_price, label in ranges:
        if max_price == float('inf'):
            count = Product.objects.filter(price__gte=min_price).count()
        else:
            count = Product.objects.filter(price__gte=min_price, price__lt=max_price).count()
        print(f"{label}: {count} товаров")

def main():
    print("🔍 ПРОВЕРКА ЗАГРУЖЕННЫХ ТОВАРОВ")
    print("=" * 50)
    
    # Проверяем статистику
    total_products, total_categories, total_characteristics = check_database_stats()
    
    # Проверяем иерархию категорий
    check_categories_hierarchy()
    
    # Проверяем товары по категориям
    check_products_by_category()
    
    # Проверяем детали товаров
    check_product_details()
    
    # Проверяем диапазоны цен
    check_price_ranges()
    
    print("\n" + "=" * 50)
    if total_products >= 500:
        print("✅ УСПЕХ: Создано 500+ товаров!")
    else:
        print(f"⚠️ ВНИМАНИЕ: Создано только {total_products} товаров из 500")
    
    print(f"📊 Итого: {total_products} товаров, {total_categories} категорий, {total_characteristics} характеристик")

if __name__ == "__main__":
    main()
