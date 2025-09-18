#!/usr/bin/env python3
"""
Скрипт для добавления тестовых товаров в корзину
"""

import os
import sys
import django

# Настройка Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shoplist.settings')
django.setup()

from products.models import Product, Cart, CartItem, User

def add_test_cart_items():
    """Добавляет тестовые товары в корзину"""
    print("🛒 Добавление тестовых товаров в корзину...")
    
    # Получаем несколько товаров
    products = Product.objects.filter(is_active=True)[:5]
    
    if not products:
        print("❌ Нет активных товаров в базе данных")
        return
        
    print(f"✅ Найдено {products.count()} товаров")
    
    # Создаем корзину (для неавторизованного пользователя используем сессию)
    # Для тестирования создадим корзину в базе данных
    
    # Создаем тестового пользователя если его нет
    user, created = User.objects.get_or_create(
        username='test_user',
        defaults={'email': 'test@example.com'}
    )
    
    if created:
        print("✅ Создан тестовый пользователь")
    else:
        print("✅ Используется существующий тестовый пользователь")
    
    # Создаем корзину
    cart, created = Cart.objects.get_or_create(user=user)
    
    if created:
        print("✅ Создана корзина")
    else:
        print("✅ Используется существующая корзина")
        # Очищаем существующие товары
        CartItem.objects.filter(cart=cart).delete()
    
    # Добавляем товары в корзину
    for i, product in enumerate(products):
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': i + 1}
        )
        
        if created:
            print(f"✅ Добавлен товар: {product.name} (количество: {cart_item.quantity})")
        else:
            cart_item.quantity = i + 1
            cart_item.save()
            print(f"✅ Обновлен товар: {product.name} (количество: {cart_item.quantity})")
    
    print(f"\n🎉 В корзину добавлено {CartItem.objects.filter(cart=cart).count()} товаров")
    
    # Показываем содержимое корзины
    print("\n📋 Содержимое корзины:")
    for item in CartItem.objects.filter(cart=cart):
        print(f"  - {item.product.name}: {item.quantity} шт. по {item.product.price} ₽")

if __name__ == '__main__':
    add_test_cart_items()
