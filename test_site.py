#!/usr/bin/env python
import os
import sys
import django

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shoplist.settings')
django.setup()

from products.models import Product, Category, User

print("=== ПРОВЕРКА БАЗЫ ДАННЫХ ===")
print(f"Категории: {Category.objects.count()}")
print(f"Товары: {Product.objects.count()}")
print(f"Пользователи: {User.objects.count()}")

# Создаем тестовые данные если их нет
if Category.objects.count() == 0:
    print("Создаем тестовые категории...")
    Category.objects.create(name="Электроника", slug="electronics")
    Category.objects.create(name="Одежда", slug="clothing")
    Category.objects.create(name="Книги", slug="books")

if User.objects.count() == 0:
    print("Создаем тестового пользователя...")
    User.objects.create_superuser('admin', 'admin@test.com', 'admin123')

print("=== ДАННЫЕ СОЗДАНЫ ===")
print(f"Категории: {Category.objects.count()}")
print(f"Товары: {Product.objects.count()}")
print(f"Пользователи: {User.objects.count()}")
