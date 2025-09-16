#!/usr/bin/env python
"""
Скрипт для парсинга товаров с сайта Леруа Мерлен
"""
import os
import django
import requests
import time
import random
from bs4 import BeautifulSoup
import re

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shoplist.settings')
django.setup()

from django.db import connection
from faker import Faker

fake = Faker('ru_RU')

def scrape_leroy_merlin():
    """Парсинг товаров с сайта Леруа Мерлен"""
    print("🚀 Начинаем парсинг товаров с Леруа Мерлен...")
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
    })
    
    base_url = 'https://leroymerlin.ru'
    categories = [
        'https://leroymerlin.ru/catalogue/santehnika/',
        'https://leroymerlin.ru/catalogue/elektrika/',
        'https://leroymerlin.ru/catalogue/otoplenie/',
        'https://leroymerlin.ru/catalogue/plitka/',
        'https://leroymerlin.ru/catalogue/klei/',
        'https://leroymerlin.ru/catalogue/instrumenty/',
    ]
    
    all_products = []
    
    for category_url in categories:
        try:
            print(f"Парсинг категории: {category_url}")
            response = session.get(category_url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Ищем карточки товаров
            product_cards = soup.find_all('div', class_='product-item') or soup.find_all('div', class_='product-card')
            
            if not product_cards:
                product_cards = soup.find_all('div', class_='item') or soup.find_all('article', class_='product')
            
            print(f"Найдено {len(product_cards)} карточек товаров")
            
            for card in product_cards[:20]:  # Берем первые 20 товаров
                try:
                    product_data = {}
                    
                    # Название товара
                    name_elem = card.find('a', class_='product-name') or card.find('h3') or card.find('a', class_='name')
                    if name_elem:
                        product_data['name'] = name_elem.get_text().strip()
                    
                    # Цена
                    price_elem = card.find('span', class_='price') or card.find('div', class_='price') or card.find('span', class_='cost')
                    if price_elem:
                        price_text = price_elem.get_text().strip()
                        price_match = re.search(r'[\d\s]+', price_text.replace(' ', ''))
                        if price_match:
                            product_data['price'] = int(price_match.group().replace(' ', ''))
                    
                    if product_data.get('name') and product_data.get('price'):
                        all_products.append(product_data)
                        print(f"Найден товар: {product_data['name']} - {product_data['price']} ₽")
                        
                except Exception as e:
                    print(f"Ошибка при парсинге карточки: {e}")
                    continue
            
            time.sleep(random.uniform(2, 4))
            
        except Exception as e:
            print(f"Ошибка при парсинге категории {category_url}: {e}")
            continue
    
    print(f"\n✅ Парсинг завершен! Получено {len(all_products)} товаров")
    return all_products

def save_to_db(products):
    """Сохранение товаров в базу данных"""
    print("💾 Сохраняем товары в базу данных...")
    
    with connection.cursor() as cursor:
        # Создаем категорию
        cursor.execute("""
            INSERT INTO products_category (slug, icon, is_active, created_at, updated_at)
            SELECT %s, %s, %s, NOW(), NOW()
            WHERE NOT EXISTS (SELECT 1 FROM products_category WHERE slug = %s)
        """, ["leroy-merlin", "wrench", True, "leroy-merlin"])
        
        cursor.execute("SELECT id FROM products_category WHERE slug = %s", ["leroy-merlin"])
        category_id = cursor.fetchone()[0]
        
        cursor.execute("""
            INSERT INTO products_category_translation (master_id, language_code, name, description)
            SELECT %s, %s, %s, %s
            WHERE NOT EXISTS (SELECT 1 FROM products_category_translation WHERE master_id = %s AND language_code = %s)
        """, [category_id, 'ru', "Леруа Мерлен", "Товары для дома и ремонта", category_id, 'ru'])
        
        # Создаем продавца
        cursor.execute("""
            INSERT INTO products_seller (company_name, description, commission_rate, is_verified, rating, total_sales, total_revenue, created_at, updated_at)
            SELECT %s, %s, %s, %s, %s, %s, %s, NOW(), NOW()
            WHERE NOT EXISTS (SELECT 1 FROM products_seller WHERE company_name = %s)
        """, ["Леруа Мерлен", "Сеть магазинов для дома и ремонта", 5.0, True, 4.5, 0, 0.0, "Леруа Мерлен"])
        
        cursor.execute("SELECT id FROM products_seller WHERE company_name = %s", ["Леруа Мерлен"])
        seller_id = cursor.fetchone()[0]
        
        saved_count = 0
        
        for product_data in products:
            try:
                name = product_data['name']
                price = product_data['price']
                sku = f"LM-{fake.unique.random_number(digits=6)}"
                
                cursor.execute("""
                    INSERT INTO products_product (category_id, seller_id, currency, price, sku, stock_quantity, is_active, rating, reviews_count, views_count, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                    RETURNING id
                """, [category_id, seller_id, 'RUB', price, sku, random.randint(5, 50), True, round(random.uniform(4.0, 5.0), 2), random.randint(0, 30), random.randint(20, 200)])
                
                product_id = cursor.fetchone()[0]
                
                cursor.execute("""
                    INSERT INTO products_product_translation (master_id, language_code, name, description)
                    VALUES (%s, %s, %s, %s)
                """, [product_id, 'ru', name, f"Товар спарсен с сайта Леруа Мерлен. {name}"])
                
                saved_count += 1
                print(f"✅ Сохранен товар: {name} - {price} ₽")
                
            except Exception as e:
                print(f"❌ Ошибка при сохранении товара: {e}")
        
        print(f"\n🎉 Сохранено {saved_count} товаров в базу данных!")

def main():
    """Основная функция"""
    products = scrape_leroy_merlin()
    
    if products:
        save_to_db(products)
    else:
        print("❌ Не удалось спарсить товары")

if __name__ == '__main__':
    main()
