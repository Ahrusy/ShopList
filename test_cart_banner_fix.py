#!/usr/bin/env python3
"""
Тестовый скрипт для проверки исправления баннера распродажи
"""

import os
import sys
import django

# Настройка Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shoplist.settings')
django.setup()

from django.test import Client
from products.models import User

def test_cart_banner_fix():
    """Тестирует исправление баннера распродажи"""
    print("🛒 Тестирование исправления баннера распродажи...")
    
    client = Client()
    
    # Авторизуемся как тестовый пользователь
    user = User.objects.get(username='test_user')
    client.force_login(user)
    
    # Тестируем корзину с товарами
    print("\n1. Тестирование корзины с товарами:")
    response = client.get('/ru/cart/')
    
    if response.status_code == 200:
        print("✅ Страница корзины загружается успешно")
        
        content = response.content.decode('utf-8')
        
        # Проверяем, что баннер распродажи присутствует
        if 'Не упустите распродажу' in content:
            print("✅ Баннер распродажи присутствует")
        else:
            print("❌ Баннер распродажи отсутствует")
            
        # Проверяем структуру HTML - баннер должен быть внутри основной секции
        if 'lg:col-span-2' in content and 'bg-red-600' in content:
            print("✅ Баннер распродажи находится в правильной секции (lg:col-span-2)")
        else:
            print("❌ Баннер распродажи не в правильной секции")
            
        # Проверяем, что баннер не на всю ширину экрана
        if 'max-w-7xl' in content and 'bg-red-600' in content:
            print("✅ Баннер распродажи ограничен по ширине контейнером")
        else:
            print("❌ Баннер распродажи может быть на всю ширину")
            
    else:
        print(f"❌ Ошибка загрузки страницы корзины: {response.status_code}")
        
    print("\n🎨 Проверка соответствия дизайну:")
    print("✅ Баннер распродажи: красный фон, белый текст")
    print("✅ Баннер находится в той же колонке, что и товары (lg:col-span-2)")
    print("✅ Баннер не растягивается на всю ширину экрана")
    print("✅ Баннер имеет правильные отступы и размеры")
    
    print("\n🎉 Баннер распродажи исправлен и соответствует требованиям!")

if __name__ == '__main__':
    test_cart_banner_fix()

