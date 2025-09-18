#!/usr/bin/env python
import os
import sys
import django

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shoplist.settings')
django.setup()

from products.models import Category
from django.utils.text import slugify

def fix_category_slugs():
    """Исправляет пустые slug'и для категорий"""
    categories = Category.objects.all()
    
    print(f"Найдено категорий: {categories.count()}")
    
    for category in categories:
        if not category.slug:
            # Создаем slug из названия
            category.slug = slugify(category.name)
            print(f"Исправляем категорию ID {category.id}: '{category.name}' -> slug: '{category.slug}'")
            category.save()
        else:
            print(f"Категория ID {category.id}: '{category.name}' уже имеет slug: '{category.slug}'")

if __name__ == "__main__":
    fix_category_slugs()
    print("Готово!")


