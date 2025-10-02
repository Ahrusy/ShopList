#!/usr/bin/env python3
"""
Скрипт для добавления скидок к товарам
"""

import os
import sys
import django
from decimal import Decimal

# Настройка Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shoplist.settings')
django.setup()

from products.models import Product

def add_discounts():
    """Добавляет скидки к товарам"""
    print("💰 Добавление скидок к товарам...")
    
    # Получаем первые 3 товара
    products = Product.objects.filter(is_active=True)[:3]
    
    for product in products:
        # Устанавливаем скидку 20%
        discount_price = product.price * Decimal('0.8')
        product.discount_price = discount_price
        product.save()
        
        print(f"✅ Товар '{product.name}': {product.price} ₽ → {discount_price} ₽ (скидка 20%)")
    
    print(f"\n🎉 Добавлены скидки к {products.count()} товарам")

if __name__ == '__main__':
    add_discounts()









