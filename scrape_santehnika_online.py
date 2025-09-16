#!/usr/bin/env python
"""
Скрипт для парсинга товаров с сайта Сантехника онлайн
"""
import os
import django
import requests
import time
import random
from bs4 import BeautifulSoup
import json
from decimal import Decimal
from faker import Faker
import re

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shoplist.settings')
django.setup()

from products.models import Product, Category, Shop, Tag, Seller, ProductImage, ProductCharacteristic
from django.db import connection

fake = Faker('ru_RU')

class SantehnikaOnlineScraper:
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
        self.base_url = 'https://santehnika-online.ru'
        self.scraped_count = 0
        self.target_count = 500
        
    def get_page(self, url, retries=3):
        """Получение страницы с повторными попытками"""
        for attempt in range(retries):
            try:
                response = self.session.get(url, timeout=15)
                response.raise_for_status()
                return response
            except requests.exceptions.RequestException as e:
                print(f"Ошибка при загрузке {url} (попытка {attempt + 1}): {e}")
                if attempt < retries - 1:
                    time.sleep(random.uniform(2, 4))
                else:
                    return None
    
    def parse_category_page(self, category_url):
        """Парсинг страницы категории"""
        try:
            response = self.get_page(category_url)
            if not response:
                return []
            
            soup = BeautifulSoup(response.content, 'html.parser')
            products = []
            
            # Ищем карточки товаров
            product_cards = soup.find_all('div', class_='product-item') or soup.find_all('div', class_='product-card')
            
            if not product_cards:
                # Альтернативные селекторы
                product_cards = soup.find_all('div', class_='item') or soup.find_all('article', class_='product')
            
            print(f"Найдено {len(product_cards)} карточек товаров")
            
            for card in product_cards[:30]:  # Берем первые 30 товаров
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
                        # Извлекаем числа из цены
                        price_match = re.search(r'[\d\s]+', price_text.replace(' ', ''))
                        if price_match:
                            product_data['price'] = int(price_match.group().replace(' ', ''))
                    
                    # Ссылка на товар
                    link_elem = card.find('a', class_='product-link') or card.find('a')
                    if link_elem:
                        href = link_elem.get('href')
                        if href:
                            if href.startswith('/'):
                                href = self.base_url + href
                            product_data['url'] = href
                    
                    # Изображение
                    img_elem = card.find('img', class_='product-image') or card.find('img')
                    if img_elem:
                        src = img_elem.get('src') or img_elem.get('data-src')
                        if src:
                            if src.startswith('//'):
                                src = 'https:' + src
                            elif src.startswith('/'):
                                src = self.base_url + src
                            product_data['image'] = src
                    
                    # Описание
                    desc_elem = card.find('div', class_='description') or card.find('p', class_='desc')
                    if desc_elem:
                        product_data['description'] = desc_elem.get_text().strip()[:300]
                    
                    if product_data.get('name') and product_data.get('price'):
                        products.append(product_data)
                        
                except Exception as e:
                    print(f"Ошибка при парсинге карточки товара: {e}")
                    continue
            
            return products
            
        except Exception as e:
            print(f"Ошибка при парсинге категории {category_url}: {e}")
            return []
    
    def parse_product_detail(self, product_url):
        """Парсинг детальной страницы товара"""
        try:
            response = self.get_page(product_url)
            if not response:
                return {}
            
            soup = BeautifulSoup(response.content, 'html.parser')
            details = {}
            
            # Характеристики
            characteristics = {}
            char_elements = soup.find_all('tr', class_='characteristic') or soup.find_all('div', class_='spec')
            
            for char in char_elements:
                key_elem = char.find('td', class_='name') or char.find('span', class_='name')
                value_elem = char.find('td', class_='value') or char.find('span', class_='value')
                if key_elem and value_elem:
                    key = key_elem.get_text().strip()
                    value = value_elem.get_text().strip()
                    if key and value:
                        characteristics[key] = value
            
            details['characteristics'] = characteristics
            
            # Дополнительные изображения
            images = []
            img_elements = soup.find_all('img', class_='product-image') or soup.find_all('img', class_='gallery')
            for img in img_elements[:5]:  # Берем первые 5 изображений
                src = img.get('src') or img.get('data-src')
                if src:
                    if src.startswith('//'):
                        src = 'https:' + src
                    elif src.startswith('/'):
                        src = self.base_url + src
                    images.append(src)
            
            details['images'] = images
            
            return details
            
        except Exception as e:
            print(f"Ошибка при парсинге деталей товара {product_url}: {e}")
            return {}
    
    def scrape_products(self):
        """Основной метод парсинга"""
        print("🚀 Начинаем парсинг товаров с Сантехника онлайн...")
        
        # URL категорий для парсинга
        categories = [
            'https://santehnika-online.ru/catalog/rakoviny/',
            'https://santehnika-online.ru/catalog/unitazy/',
            'https://santehnika-online.ru/catalog/vanny/',
            'https://santehnika-online.ru/catalog/dushi/',
            'https://santehnika-online.ru/catalog/moyki/',
            'https://santehnika-online.ru/catalog/smesiteli/',
            'https://santehnika-online.ru/catalog/truby/',
            'https://santehnika-online.ru/catalog/fitingi/',
            'https://santehnika-online.ru/catalog/armatura/',
            'https://santehnika-online.ru/catalog/otoplenie/',
            'https://santehnika-online.ru/catalog/elektrika/',
            'https://santehnika-online.ru/catalog/plitka/',
            'https://santehnika-online.ru/catalog/klei/',
            'https://santehnika-online.ru/catalog/instrumenty/',
            'https://santehnika-online.ru/catalog/aksessuary/',
        ]
        
        all_products = []
        
        for category_url in categories:
            if self.scraped_count >= self.target_count:
                break
                
            print(f"\n📂 Парсинг категории: {category_url}")
            products = self.parse_category_page(category_url)
            
            # Парсим детали для каждого товара
            for product in products:
                if self.scraped_count >= self.target_count:
                    break
                    
                if product.get('url'):
                    print(f"Парсинг деталей товара: {product['name']}")
                    details = self.parse_product_detail(product['url'])
                    product.update(details)
                    
                    # Задержка между запросами
                    time.sleep(random.uniform(1, 2))
            
            all_products.extend(products)
            self.scraped_count = len(all_products)
            
            print(f"Спарсено товаров: {self.scraped_count}/{self.target_count}")
            
            # Задержка между категориями
            time.sleep(random.uniform(2, 4))
        
        print(f"\n✅ Парсинг завершен! Получено {len(all_products)} товаров")
        return all_products

def save_products_to_db(products):
    """Сохранение товаров в базу данных"""
    print("💾 Сохраняем товары в базу данных...")
    
    with connection.cursor() as cursor:
        saved_count = 0
        
        for product_data in products:
            try:
                # Создаем категорию "Сантехника"
                cursor.execute("""
                    INSERT INTO products_category (slug, icon, is_active, created_at, updated_at)
                    SELECT %s, %s, %s, NOW(), NOW()
                    WHERE NOT EXISTS (SELECT 1 FROM products_category WHERE slug = %s)
                """, ["santehnika", "wrench", True, "santehnika"])
                
                cursor.execute("SELECT id FROM products_category WHERE slug = %s", ["santehnika"])
                category_id = cursor.fetchone()[0]
                
                cursor.execute("""
                    INSERT INTO products_category_translation (master_id, language_code, name, description)
                    SELECT %s, %s, %s, %s
                    WHERE NOT EXISTS (SELECT 1 FROM products_category_translation WHERE master_id = %s AND language_code = %s)
                """, [category_id, 'ru', "Сантехника", "Товары для сантехники и ремонта", category_id, 'ru'])
                
                # Создаем продавца
                cursor.execute("""
                    INSERT INTO products_seller (company_name, description, created_at, updated_at)
                    SELECT %s, %s, NOW(), NOW()
                    WHERE NOT EXISTS (SELECT 1 FROM products_seller WHERE company_name = %s)
                """, ["Сантехника Онлайн", "Интернет-магазин сантехники", "Сантехника Онлайн"])
                
                cursor.execute("SELECT id FROM products_seller WHERE company_name = %s", ["Сантехника Онлайн"])
                seller_id = cursor.fetchone()[0]
                
                # Создаем товар
                name = product_data.get('name', 'Товар без названия')
                price = product_data.get('price', 1000)
                description = product_data.get('description', f"Товар спарсен с сайта Сантехника онлайн. {name}")
                sku = f"ST-{fake.unique.random_number(digits=6)}"
                
                cursor.execute("""
                    INSERT INTO products_product (category_id, seller_id, currency, price, sku, stock_quantity, is_active, rating, reviews_count, views_count, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                    RETURNING id
                """, [category_id, seller_id, 'RUB', price, sku, random.randint(5, 50), True, round(random.uniform(4.0, 5.0), 2), random.randint(0, 30), random.randint(20, 200)])
                
                product_id = cursor.fetchone()[0]
                
                # Создаем перевод товара
                cursor.execute("""
                    INSERT INTO products_product_translation (master_id, language_code, name, description)
                    VALUES (%s, %s, %s, %s)
                """, [product_id, 'ru', name, description])
                
                # Сохраняем характеристики
                characteristics = product_data.get('characteristics', {})
                char_count = 0
                for char_name, char_value in characteristics.items():
                    if char_count >= 8:  # Ограничиваем количество характеристик
                        break
                    cursor.execute("""
                        INSERT INTO products_productcharacteristic (product_id, name, value, unit, "order")
                        VALUES (%s, %s, %s, %s, %s)
                    """, [product_id, char_name, char_value, "шт", char_count + 1])
                    char_count += 1
                
                # Добавляем стандартные характеристики
                standard_chars = [
                    ("Источник", "Сантехника онлайн"),
                    ("Тип", "Сантехническое оборудование"),
                    ("Статус", "В наличии"),
                    ("Доставка", "Доступна"),
                ]
                
                for char_name, char_value in standard_chars:
                    cursor.execute("""
                        INSERT INTO products_productcharacteristic (product_id, name, value, unit, "order")
                        VALUES (%s, %s, %s, %s, %s)
                    """, [product_id, char_name, char_value, "шт", char_count + 1])
                    char_count += 1
                
                # Создаем магазин
                cursor.execute("""
                    INSERT INTO products_shop (phone, email, created_at, updated_at)
                    SELECT %s, %s, NOW(), NOW()
                    WHERE NOT EXISTS (SELECT 1 FROM products_shop WHERE phone = %s)
                """, ["+7 (495) 123-45-67", "info@santehnika-online.ru", "+7 (495) 123-45-67"])
                
                cursor.execute("SELECT id FROM products_shop WHERE phone = %s", ["+7 (495) 123-45-67"])
                shop_id = cursor.fetchone()[0]
                
                cursor.execute("""
                    INSERT INTO products_shop_translation (master_id, language_code, name, address, city)
                    SELECT %s, %s, %s, %s, %s
                    WHERE NOT EXISTS (SELECT 1 FROM products_shop_translation WHERE master_id = %s AND language_code = %s)
                """, [shop_id, 'ru', "Сантехника Онлайн", "Москва, ул. Строителей, 1", "Москва", shop_id, 'ru'])
                
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
    scraper = SantehnikaOnlineScraper()
    
    # Парсим товары
    products = scraper.scrape_products()
    
    if products:
        # Сохраняем в базу данных
        save_products_to_db(products)
    else:
        print("❌ Не удалось спарсить товары")

if __name__ == '__main__':
    main()
