#!/usr/bin/env python3
"""
Скрипт для тестирования API категорий
"""
import requests
import json

def test_categories_api():
    base_url = "http://127.0.0.1:8000"
    
    print("🧪 Тестирование API категорий...")
    
    # Тест 1: Основные категории
    print("\n1️⃣ Тестируем основные категории...")
    try:
        response = requests.get(f"{base_url}/api/mega-menu/categories/")
        print(f"Статус: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Успешно! Получено категорий: {len(data.get('categories', []))}")
            
            # Показываем первые 3 категории
            for i, cat in enumerate(data.get('categories', [])[:3]):
                print(f"   - {cat['name']} (ID: {cat['id']}, Slug: {cat['slug']})")
                
        else:
            print(f"❌ Ошибка: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Исключение: {e}")
    
    # Тест 2: Подкатегории первой категории
    print("\n2️⃣ Тестируем подкатегории...")
    try:
        # Получаем ID первой категории
        response = requests.get(f"{base_url}/api/mega-menu/categories/")
        if response.status_code == 200:
            data = response.json()
            if data.get('categories'):
                first_cat_id = data['categories'][0]['id']
                
                # Запрашиваем подкатегории
                response = requests.get(f"{base_url}/api/mega-menu/categories/{first_cat_id}/subcategories/")
                print(f"Статус: {response.status_code}")
                
                if response.status_code == 200:
                    subcat_data = response.json()
                    print(f"✅ Успешно! Получено подкатегорий: {len(subcat_data.get('subcategories', []))}")
                    
                    # Показываем первые 3 подкатегории
                    for i, subcat in enumerate(subcat_data.get('subcategories', [])[:3]):
                        print(f"   - {subcat['name']} (ID: {subcat['id']}, Level: {subcat.get('level', 'N/A')})")
                        
                else:
                    print(f"❌ Ошибка: {response.status_code}")
                    print(response.text)
            else:
                print("❌ Нет категорий для тестирования")
                
    except Exception as e:
        print(f"❌ Исключение: {e}")
    
    # Тест 3: Поиск категорий
    print("\n3️⃣ Тестируем поиск категорий...")
    try:
        response = requests.get(f"{base_url}/api/categories/search/?q=электроника")
        print(f"Статус: {response.status_code}")
        
        if response.status_code == 200:
            search_data = response.json()
            print(f"✅ Успешно! Найдено категорий: {len(search_data.get('categories', []))}")
            
            # Показываем результаты поиска
            for cat in search_data.get('categories', [])[:3]:
                print(f"   - {cat['name']} (Path: {cat.get('path', 'N/A')})")
                
        else:
            print(f"❌ Ошибка: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Исключение: {e}")
    
    print("\n🏁 Тестирование завершено!")

if __name__ == "__main__":
    test_categories_api()