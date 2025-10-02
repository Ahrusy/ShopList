#!/usr/bin/env python
"""
Скрипт для проверки структуры категорий в базе данных
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shoplist.settings')
django.setup()

from products.models import Category

def check_category_structure():
    print("🔍 Проверяем структуру категорий...")
    
    # Получаем все категории
    categories = Category.objects.all()
    print(f"✅ Всего категорий в БД: {categories.count()}")
    
    # Анализируем уровни вложенности
    level_counts = {0: 0, 1: 0, 2: 0, 3: 0}
    
    for category in categories:
        level = category.level
        if level > 3:
            level = 3  # Группируем всё выше 3 уровня
        level_counts[level] = level_counts.get(level, 0) + 1
    
    print("\n📊 Распределение по уровням:")
    print(f"• Корневые категории (уровень 0): {level_counts[0]}")
    print(f"• Подкатегории 1-го уровня: {level_counts[1]}")
    print(f"• Подкатегории 2-го уровня: {level_counts[2]}")
    print(f"• Подкатегории 3-го уровня и глубже: {level_counts[3]}")
    
    # Проверяем наличие категорий всех уровней
    if level_counts[0] > 0 and level_counts[1] > 0 and level_counts[2] > 0:
        print("\n✅ Структура категорий подходит для загрузки товаров")
    else:
        print("\n⚠️ Внимание: Недостаточно категорий для загрузки товаров!")
        print("Пожалуйста, создайте категории всех уровней перед загрузкой товаров")

if __name__ == '__main__':
    check_category_structure()