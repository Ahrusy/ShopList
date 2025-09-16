#!/usr/bin/env python
"""
Скрипт для проверки результатов парсинга
"""
import os
import sys
import django
import logging

# Настройка логгера
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('check_results.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shoplist.settings')
django.setup()

from products.models import Category, Product, ProductCharacteristic, ProductImage, Seller

def check_database_stats():
    """Проверяет статистику базы данных"""
    logger.info("=== СТАТИСТИКА БАЗЫ ДАННЫХ ===")
    
    # Общая статистика
    total_products = Product.objects.count()
    total_categories = Category.objects.count()
    total_characteristics = ProductCharacteristic.objects.count()
    total_images = ProductImage.objects.count()
    total_sellers = Seller.objects.count()
    
    logger.info(f"📊 Товаров: {total_products}")
    logger.info(f"📊 Категорий: {total_categories}")
    logger.info(f"📊 Характеристик: {total_characteristics}")
    logger.info(f"📊 Изображений: {total_images}")
    logger.info(f"📊 Продавцов: {total_sellers}")
    
    return total_products, total_categories, total_characteristics, total_images

def check_categories_hierarchy():
    """Проверяет иерархию категорий"""
    logger.info("\n=== ИЕРАРХИЯ КАТЕГОРИЙ ===")
    
    # Корневые категории
    root_categories = Category.objects.filter(parent__isnull=True)
    logger.info(f"🌳 Корневых категорий: {root_categories.count()}")
    
    for root in root_categories:
        logger.info(f"  📁 {root.name}")
        
        # Подкатегории 2-го уровня
        sub_categories = root.children.all()
        for sub in sub_categories:
            logger.info(f"    📂 {sub.name}")
            
            # Подкатегории 3-го уровня
            sub_sub_categories = sub.children.all()
            for sub_sub in sub_sub_categories:
                logger.info(f"      📄 {sub_sub.name}")

def check_products_by_category():
    """Проверяет товары по категориям"""
    logger.info("\n=== ТОВАРЫ ПО КАТЕГОРИЯМ ===")
    
    categories = Category.objects.filter(level=2)  # Подкатегории 2-го уровня
    
    for category in categories:
        products_count = Product.objects.filter(category=category).count()
        logger.info(f"📦 {category.name}: {products_count} товаров")
        
        # Показываем несколько примеров товаров
        products = Product.objects.filter(category=category)[:3]
        for product in products:
            logger.info(f"    - {product.name} ({product.price}₽)")

def check_product_details():
    """Проверяет детали товаров"""
    logger.info("\n=== ДЕТАЛИ ТОВАРОВ ===")
    
    # Берем несколько товаров для детального анализа
    products = Product.objects.all()[:5]
    
    for product in products:
        logger.info(f"\n🛍️ Товар: {product.name}")
        logger.info(f"   💰 Цена: {product.price}₽")
        logger.info(f"   📝 Описание: {product.description[:100]}...")
        logger.info(f"   📊 Рейтинг: {product.rating}")
        logger.info(f"   📈 Отзывов: {product.reviews_count}")
        logger.info(f"   📦 На складе: {product.stock_quantity}")
        logger.info(f"   🏷️ Категория: {product.category.name}")
        
        # Характеристики
        characteristics = product.characteristics.all()[:3]
        if characteristics:
            logger.info("   🔧 Характеристики:")
            for char in characteristics:
                logger.info(f"      - {char.name}: {char.value}")
        
        # Изображения
        images = product.images.all()
        logger.info(f"   🖼️ Изображений: {images.count()}")

def check_database_health():
    """Проверяет здоровье базы данных"""
    logger.info("\n=== ПРОВЕРКА ЗДОРОВЬЯ БД ===")
    
    # Проверяем товары без категорий
    products_without_category = Product.objects.filter(category__isnull=True).count()
    if products_without_category > 0:
        logger.warning(f"⚠️ Товаров без категории: {products_without_category}")
    else:
        logger.info("✅ Все товары имеют категории")
    
    # Проверяем товары без изображений
    products_without_images = Product.objects.filter(images__isnull=True).count()
    if products_without_images > 0:
        logger.warning(f"⚠️ Товаров без изображений: {products_without_images}")
    else:
        logger.info("✅ Все товары имеют изображения")
    
    # Проверяем товары без характеристик
    products_without_characteristics = Product.objects.filter(characteristics__isnull=True).count()
    if products_without_characteristics > 0:
        logger.warning(f"⚠️ Товаров без характеристик: {products_without_characteristics}")
    else:
        logger.info("✅ Все товары имеют характеристики")
    
    # Проверяем товары с нулевой ценой
    products_with_zero_price = Product.objects.filter(price=0).count()
    if products_with_zero_price > 0:
        logger.warning(f"⚠️ Товаров с нулевой ценой: {products_with_zero_price}")
    else:
        logger.info("✅ Все товары имеют цену")

def main():
    logger.info("=== ПРОВЕРКА РЕЗУЛЬТАТОВ ПАРСИНГА ===")
    
    try:
        # Проверяем статистику
        total_products, total_categories, total_characteristics, total_images = check_database_stats()
        
        # Проверяем иерархию категорий
        check_categories_hierarchy()
        
        # Проверяем товары по категориям
        check_products_by_category()
        
        # Проверяем детали товаров
        check_product_details()
        
        # Проверяем здоровье базы данных
        check_database_health()
        
        logger.info("\n🎉 Проверка завершена!")
        
        if total_products >= 500:
            logger.info("✅ Цель достигнута: загружено 500+ товаров")
        else:
            logger.warning(f"⚠️ Загружено только {total_products} товаров из 500")
        
    except Exception as e:
        logger.error(f"❌ Ошибка при проверке результатов: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main()
