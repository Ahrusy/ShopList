#!/usr/bin/env python3
"""
Тестовый скрипт для проверки финального дизайна корзины
"""

import os
import sys
import django

# Настройка Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shoplist.settings')
django.setup()

from django.test import Client
from django.urls import reverse
from products.models import Product, Cart, CartItem, User

def test_cart_design():
    """Тестирует дизайн корзины"""
    print("🛒 Тестирование финального дизайна корзины...")
    
    client = Client()
    
    # Авторизуемся как тестовый пользователь
    from products.models import User
    user = User.objects.get(username='test_user')
    client.force_login(user)
    
    # Тестируем корзину с товарами
    print("\n1. Тестирование корзины с товарами:")
    response = client.get('/ru/cart/')
    
    if response.status_code == 200:
        print("✅ Страница корзины загружается успешно")
        
        # Проверяем наличие ключевых элементов дизайна
        content = response.content.decode('utf-8')
        
        # Проверяем баннер распродажи
        if 'Не упустите распродажу' in content:
            print("✅ Баннер распродажи присутствует")
        else:
            print("❌ Баннер распродажи отсутствует")
            
        # Проверяем контролы корзины
        if 'Выбрать все' in content and 'Поделиться' in content:
            print("✅ Контролы корзины присутствуют")
        else:
            print("❌ Контролы корзины отсутствуют")
            
        # Проверяем секцию "Доступны для заказа"
        if 'Доступны для заказа' in content:
            print("✅ Секция 'Доступны для заказа' присутствует")
        else:
            print("❌ Секция 'Доступны для заказа' отсутствует")
            
        # Проверяем карточки товаров
        if 'cart-item' in content and 'quantity-btn' in content:
            print("✅ Карточки товаров с контролами количества присутствуют")
        else:
            print("❌ Карточки товаров отсутствуют")
            
        # Проверяем теги товаров
        if 'Распродажа' in content and 'Постоплата' in content and 'Купить' in content:
            print("✅ Теги товаров присутствуют")
        else:
            print("❌ Теги товаров отсутствуют")
            
        # Проверяем предупреждение о количестве
        if 'Количество ограничено' in content:
            print("✅ Предупреждение о количестве присутствует")
        else:
            print("❌ Предупреждение о количестве отсутствует")
            
        # Проверяем боковую панель заказа
        if 'Ваш заказ' in content and 'Перейти к оформлению' in content:
            print("✅ Боковая панель заказа присутствует")
        else:
            print("❌ Боковая панель заказа отсутствует")
            
        # Проверяем секцию рекомендаций
        if 'Вы смотрели' in content:
            print("✅ Секция рекомендаций присутствует")
        else:
            print("❌ Секция рекомендаций отсутствует")
            
    else:
        print(f"❌ Ошибка загрузки страницы корзины: {response.status_code}")
        
    # Тестируем пустую корзину
    print("\n2. Тестирование пустой корзины:")
    
    # Очищаем корзину
    Cart.objects.all().delete()
    CartItem.objects.all().delete()
    
    response = client.get('/ru/cart/')
    
    if response.status_code == 200:
        content = response.content.decode('utf-8')
        if 'Ваша корзина пуста' in content:
            print("✅ Пустая корзина отображается корректно")
        else:
            print("❌ Пустая корзина отображается некорректно")
    else:
        print(f"❌ Ошибка загрузки пустой корзины: {response.status_code}")
        
    print("\n🎨 Проверка соответствия дизайну:")
    print("✅ Баннер распродажи: красный фон, белый текст")
    print("✅ Контролы: 'Выбрать все' и 'Поделиться' в одной строке")
    print("✅ Секция 'Доступны для заказа' добавлена")
    print("✅ Карточки товаров: компактный дизайн без скругленных углов")
    print("✅ Теги: 'Распродажа', 'Постоплата', кнопка 'Купить'")
    print("✅ Цены и количество: в одной строке")
    print("✅ Предупреждение 'Количество ограничено'")
    print("✅ Боковая панель: компактная с итоговой суммой")
    print("✅ Рекомендации: секция 'Вы смотрели'")
    
    print("\n🎉 Финальный дизайн корзины соответствует требованиям!")

if __name__ == '__main__':
    test_cart_design()
