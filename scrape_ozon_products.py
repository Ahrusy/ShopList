#!/usr/bin/env python
"""
Скрипт для парсинга реальных товаров с OZON
"""
import os
import django
import requests
import time
import random
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import json
from decimal import Decimal
from faker import Faker

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shoplist.settings')
django.setup()

from products.models import Product, Category, Shop, Tag, Seller, ProductImage, ProductCharacteristic
from django.db import connection

fake = Faker('ru_RU')

class OzonScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        self.base_url = 'https://www.ozon.ru'
        self.scraped_count = 0
        self.target_count = 500
        
    def get_page(self, url, retries=3):
        """Получение страницы с повторными попытками"""
        for attempt in range(retries):
            try:
                response = self.session.get(url, timeout=10)
                response.raise_for_status()
                return response
            except requests.exceptions.RequestException as e:
                print(f"Ошибка при загрузке {url} (попытка {attempt + 1}): {e}")
                if attempt < retries - 1:
                    time.sleep(random.uniform(2, 5))
                else:
                    return None
    
    def parse_product_page(self, product_url):
        """Парсинг страницы товара"""
        try:
            response = self.get_page(product_url)
            if not response:
                return None
                
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Извлекаем данные товара
            product_data = {}
            
            # Название товара
            title_elem = soup.find('h1') or soup.find('title')
            if title_elem:
                product_data['name'] = title_elem.get_text().strip()
            
            # Цена
            price_elem = soup.find('span', {'data-widget': 'webPrice'}) or soup.find('span', class_='price')
            if price_elem:
                price_text = price_elem.get_text().strip()
                # Извлекаем числа из цены
                import re
                price_match = re.search(r'[\d\s]+', price_text.replace(' ', ''))
                if price_match:
                    product_data['price'] = int(price_match.group().replace(' ', ''))
            
            # Описание
            desc_elem = soup.find('div', {'data-widget': 'webCharacteristics'}) or soup.find('div', class_='description')
            if desc_elem:
                product_data['description'] = desc_elem.get_text().strip()[:500]
            
            # Изображения
            images = []
            img_elements = soup.find_all('img', {'data-widget': 'webGallery'}) or soup.find_all('img', class_='gallery')
            for img in img_elements[:3]:  # Берем первые 3 изображения
                src = img.get('src') or img.get('data-src')
                if src:
                    if src.startswith('//'):
                        src = 'https:' + src
                    elif src.startswith('/'):
                        src = self.base_url + src
                    images.append(src)
            
            product_data['images'] = images
            
            # Характеристики
            characteristics = {}
            char_elements = soup.find_all('div', class_='characteristic') or soup.find_all('tr')
            for char in char_elements:
                key_elem = char.find('span', class_='key') or char.find('td', class_='key')
                value_elem = char.find('span', class_='value') or char.find('td', class_='value')
                if key_elem and value_elem:
                    key = key_elem.get_text().strip()
                    value = value_elem.get_text().strip()
                    if key and value:
                        characteristics[key] = value
            
            product_data['characteristics'] = characteristics
            
            return product_data
            
        except Exception as e:
            print(f"Ошибка при парсинге товара {product_url}: {e}")
            return None
    
    def get_category_products(self, category_url, max_products=50):
        """Получение товаров из категории"""
        try:
            response = self.get_page(category_url)
            if not response:
                return []
            
            soup = BeautifulSoup(response.content, 'html.parser')
            products = []
            
            # Ищем ссылки на товары
            product_links = []
            
            # Различные селекторы для ссылок на товары
            selectors = [
                'a[href*="/product/"]',
                'a[href*="/goods/"]',
                '.product-card a',
                '.tile-root a',
                'a[data-widget="searchResultsV2"]'
            ]
            
            for selector in selectors:
                links = soup.select(selector)
                for link in links:
                    href = link.get('href')
                    if href and '/product/' in href:
                        if href.startswith('/'):
                            href = self.base_url + href
                        product_links.append(href)
            
            # Убираем дубликаты
            product_links = list(set(product_links))
            
            print(f"Найдено {len(product_links)} товаров в категории")
            
            # Парсим товары
            for i, product_url in enumerate(product_links[:max_products]):
                if self.scraped_count >= self.target_count:
                    break
                    
                print(f"Парсинг товара {self.scraped_count + 1}/{self.target_count}: {product_url}")
                
                product_data = self.parse_product_page(product_url)
                if product_data:
                    products.append(product_data)
                    self.scraped_count += 1
                
                # Задержка между запросами
                time.sleep(random.uniform(1, 3))
            
            return products
            
        except Exception as e:
            print(f"Ошибка при получении товаров из категории {category_url}: {e}")
            return []
    
    def scrape_products(self):
        """Основной метод парсинга"""
        print("🚀 Начинаем парсинг товаров с OZON...")
        
        # URL категорий для парсинга
        categories = [
            'https://www.ozon.ru/category/smartfony-15502/',
            'https://www.ozon.ru/category/noutbuki-15687/',
            'https://www.ozon.ru/category/odezhda-muzhskaya-7502/',
            'https://www.ozon.ru/category/odezhda-zhenskaya-7501/',
            'https://www.ozon.ru/category/obuv-muzhskaya-7503/',
            'https://www.ozon.ru/category/obuv-zhenskaya-7504/',
            'https://www.ozon.ru/category/bytovaya-tehnika-10500/',
            'https://www.ozon.ru/category/krasota-i-zdorove-7500/',
            'https://www.ozon.ru/category/sport-i-otdyh-7505/',
            'https://www.ozon.ru/category/knigi-15500/',
        ]
        
        all_products = []
        
        for category_url in categories:
            if self.scraped_count >= self.target_count:
                break
                
            print(f"\n📂 Парсинг категории: {category_url}")
            products = self.get_category_products(category_url, max_products=50)
            all_products.extend(products)
            
            print(f"Спарсено товаров: {self.scraped_count}/{self.target_count}")
        
        print(f"\n✅ Парсинг завершен! Получено {len(all_products)} товаров")
        return all_products

def save_products_to_db(products):
    """Сохранение товаров в базу данных"""
    print("💾 Сохраняем товары в базу данных...")
    
    with connection.cursor() as cursor:
        saved_count = 0
        
        for product_data in products:
            try:
                # Создаем категорию "Парсенные товары"
                cursor.execute("""
                    INSERT INTO products_category (slug, icon, is_active, created_at, updated_at)
                    SELECT %s, %s, %s, NOW(), NOW()
                    WHERE NOT EXISTS (SELECT 1 FROM products_category WHERE slug = %s)
                """, ["parsed-products", "tag", True, "parsed-products"])
                
                cursor.execute("SELECT id FROM products_category WHERE slug = %s", ["parsed-products"])
                category_id = cursor.fetchone()[0]
                
                cursor.execute("""
                    INSERT INTO products_category_translation (master_id, language_code, name, description)
                    SELECT %s, %s, %s, %s
                    WHERE NOT EXISTS (SELECT 1 FROM products_category_translation WHERE master_id = %s AND language_code = %s)
                """, [category_id, 'ru', "Парсенные товары", "Товары, спарсенные с OZON", category_id, 'ru'])
                
                # Создаем продавца
                cursor.execute("""
                    INSERT INTO products_seller (company_name, description, created_at, updated_at)
                    SELECT %s, %s, NOW(), NOW()
                    WHERE NOT EXISTS (SELECT 1 FROM products_seller WHERE company_name = %s)
                """, ["OZON Парсер", "Товары с OZON", "OZON Парсер"])
                
                cursor.execute("SELECT id FROM products_seller WHERE company_name = %s", ["OZON Парсер"])
                seller_id = cursor.fetchone()[0]
                
                # Создаем товар
                name = product_data.get('name', 'Товар без названия')
                price = product_data.get('price', 1000)
                description = product_data.get('description', 'Описание отсутствует')
                sku = f"OZON-{fake.unique.random_number(digits=6)}"
                
                cursor.execute("""
                    INSERT INTO products_product (category_id, seller_id, currency, price, sku, stock_quantity, is_active, rating, reviews_count, views_count, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                    RETURNING id
                """, [category_id, seller_id, 'RUB', price, sku, random.randint(10, 100), True, round(random.uniform(3.5, 5.0), 2), random.randint(0, 50), random.randint(50, 500)])
                
                product_id = cursor.fetchone()[0]
                
                # Создаем перевод товара
                cursor.execute("""
                    INSERT INTO products_product_translation (master_id, language_code, name, description)
                    VALUES (%s, %s, %s, %s)
                """, [product_id, 'ru', name, description])
                
                # Сохраняем характеристики
                characteristics = product_data.get('characteristics', {})
                for char_name, char_value in list(characteristics.items())[:5]:  # Берем первые 5 характеристик
                    cursor.execute("""
                        INSERT INTO products_productcharacteristic (product_id, name, value, unit, "order")
                        VALUES (%s, %s, %s, %s, %s)
                    """, [product_id, char_name, char_value, "шт", 1])
                
                # Создаем магазин
                cursor.execute("""
                    INSERT INTO products_shop (phone, email, created_at, updated_at)
                    SELECT %s, %s, NOW(), NOW()
                    WHERE NOT EXISTS (SELECT 1 FROM products_shop WHERE phone = %s)
                """, ["+7 (495) 232-32-32", "store@ozon.ru", "+7 (495) 232-32-32"])
                
                cursor.execute("SELECT id FROM products_shop WHERE phone = %s", ["+7 (495) 232-32-32"])
                shop_id = cursor.fetchone()[0]
                
                cursor.execute("""
                    INSERT INTO products_shop_translation (master_id, language_code, name, address, city)
                    SELECT %s, %s, %s, %s, %s
                    WHERE NOT EXISTS (SELECT 1 FROM products_shop_translation WHERE master_id = %s AND language_code = %s)
                """, [shop_id, 'ru', "OZON Store", "Москва, ул. Льва Толстого, 16", "Москва", shop_id, 'ru'])
                
                # Связываем товар с магазином
                cursor.execute("""
                    INSERT INTO products_product_shops (product_id, shop_id)
                    SELECT %s, %s
                    WHERE NOT EXISTS (SELECT 1 FROM products_product_shops WHERE product_id = %s AND shop_id = %s)
                """, [product_id, shop_id, product_id, shop_id])
                
                saved_count += 1
                print(f"✅ Сохранен товар: {name} - {price} ₽")
                
            except Exception as e:
                print(f"❌ Ошибка при сохранении товара: {e}")
        
        print(f"\n🎉 Сохранено {saved_count} товаров в базу данных!")
        return saved_count

def main():
    """Основная функция"""
    scraper = OzonScraper()
    
    # Парсим товары
    products = scraper.scrape_products()
    
    if products:
        # Сохраняем в базу данных
        save_products_to_db(products)
    else:
        print("❌ Не удалось спарсить товары")

if __name__ == '__main__':
    main()