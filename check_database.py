#!/usr/bin/env python
import os
import sys
import django

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shoplist.settings')
django.setup()

from products.models import Category, Shop, Seller, Product, User

print("=== ПРОВЕРКА БАЗЫ ДАННЫХ ===")
print(f"Пользователи: {User.objects.count()}")
print(f"Категории: {Category.objects.count()}")
print(f"Магазины: {Shop.objects.count()}")
print(f"Продавцы: {Seller.objects.count()}")
print(f"Товары: {Product.objects.count()}")

print("\n=== ПРОВЕРКА СУПЕРПОЛЬЗОВАТЕЛЯ ===")
try:
    admin = User.objects.get(username='admin')
    print(f"Админ найден: {admin.username} (роль: {admin.role})")
except User.DoesNotExist:
    print("Админ НЕ найден!")

print("\n=== ПРОВЕРКА КАТЕГОРИЙ ===")
for cat in Category.objects.all()[:5]:
    print(f"- {cat.name} ({cat.slug})")

print("\n=== ПРОВЕРКА ТОВАРОВ ===")
for product in Product.objects.all()[:5]:
    print(f"- {product.name} - {product.price} ₽")

print("\n=== ПРОВЕРКА ЗАВЕРШЕНА ===")
