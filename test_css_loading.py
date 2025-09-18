#!/usr/bin/env python
"""
Тест для проверки загрузки CSS файла товарного слайдера
"""

import os
import sys
import django
from django.conf import settings

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shoplist.settings')
django.setup()

from django.test import Client
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
import requests

def test_css_file_access():
    """Тест доступности CSS файла"""
    print("🎯 Проверка доступности CSS файла товарного слайдера...")
    
    # Проверяем, что файл существует в staticfiles
    css_path = os.path.join(settings.STATIC_ROOT, 'css', 'product-slider.css')
    if os.path.exists(css_path):
        print(f"✅ CSS файл найден: {css_path}")
        
        # Проверяем размер файла
        file_size = os.path.getsize(css_path)
        print(f"📊 Размер файла: {file_size} байт")
        
        if file_size > 0:
            print("✅ Файл не пустой")
        else:
            print("❌ Файл пустой")
    else:
        print(f"❌ CSS файл не найден: {css_path}")
        return False
    
    # Проверяем доступность через HTTP
    try:
        client = Client()
        response = client.get('/static/css/product-slider.css')
        
        if response.status_code == 200:
            print("✅ CSS файл доступен через HTTP")
            # Для FileResponse используем streaming_content
            content = b''.join(response.streaming_content) if hasattr(response, 'streaming_content') else response.content
            print(f"📊 Размер ответа: {len(content)} байт")
            return True
        else:
            print(f"❌ CSS файл недоступен через HTTP. Статус: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка при проверке HTTP: {e}")
        return False

def test_main_page_with_css():
    """Тест главной страницы с CSS"""
    print("\n🎯 Проверка главной страницы с CSS...")
    
    try:
        client = Client()
        response = client.get('/ru/')
        
        if response.status_code == 200:
            print("✅ Главная страница загружается")
            
            # Проверяем, что CSS подключается в HTML
            content = response.content.decode('utf-8')
            if 'product-slider.css' in content:
                print("✅ CSS файл подключается в HTML")
                return True
            else:
                print("❌ CSS файл не найден в HTML")
                return False
        else:
            print(f"❌ Главная страница не загружается. Статус: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка при проверке главной страницы: {e}")
        return False

if __name__ == '__main__':
    print("🚀 Запуск тестов CSS файла товарного слайдера...\n")
    
    css_ok = test_css_file_access()
    page_ok = test_main_page_with_css()
    
    print(f"\n📋 Результаты:")
    print(f"   CSS файл: {'✅ OK' if css_ok else '❌ ОШИБКА'}")
    print(f"   Главная страница: {'✅ OK' if page_ok else '❌ ОШИБКА'}")
    
    if css_ok and page_ok:
        print("\n🎉 Все тесты пройдены! Товарный слайдер должен работать корректно.")
    else:
        print("\n⚠️  Есть проблемы с загрузкой CSS файла.")
