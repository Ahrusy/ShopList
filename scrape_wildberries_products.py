#!/usr/bin/env python
"""
Скрипт для парсинга реальных товаров с Wildberries
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

class WildberriesScraper:
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
        self.base_url = 'https://www.wildberries.ru'
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
                    time.sleep(random.uniform(3, 6))
                else:
                    return None
    
    def parse_search_results(self, search_url):
        """Парсинг результатов поиска"""
        try:
            response = self.get_page(search_url)
            if not response:
                return []
            
            soup = BeautifulSoup(response.content, 'html.parser')
            products = []
            
            # Ищем карточки товаров
            product_cards = soup.find_all('div', class_='product-card') or soup.find_all('article', class_='product-card')
            
            if not product_cards:
                # Альтернативные селекторы
                product_cards = soup.find_all('div', {'data-testid': 'product-card'}) or soup.find_all('div', class_='card-product')
            
            print(f"Найдено {len(product_cards)} карточек товаров")
            
            for card in product_cards[:20]:  # Берем первые 20 товаров
                try:
                    product_data = {}
                    
                    # Название товара
                    name_elem = card.find('span', class_='product-card__name') or card.find('h3') or card.find('a', class_='product-card__name')
                    if name_elem:
                        product_data['name'] = name_elem.get_text().strip()
                    
                    # Цена
                    price_elem = card.find('span', class_='price') or card.find('ins', class_='price') or card.find('span', class_='price__lower-price')
                    if price_elem:
                        price_text = price_elem.get_text().strip()
                        # Извлекаем числа из цены
                        price_match = re.search(r'[\d\s]+', price_text.replace(' ', ''))
                        if price_match:
                            product_data['price'] = int(price_match.group().replace(' ', ''))
                    
                    # Ссылка на товар
                    link_elem = card.find('a', class_='product-card__link') or card.find('a')
                    if link_elem:
                        href = link_elem.get('href')
                        if href:
                            if href.startswith('/'):
                                href = self.base_url + href
                            product_data['url'] = href
                    
                    # Изображение
                    img_elem = card.find('img', class_='product-card__img') or card.find('img')
                    if img_elem:
                        src = img_elem.get('src') or img_elem.get('data-src')
                        if src:
                            if src.startswith('//'):
                                src = 'https:' + src
                            elif src.startswith('/'):
                                src = self.base_url + src
                            product_data['image'] = src
                    
                    # Рейтинг
                    rating_elem = card.find('span', class_='product-card__rating') or card.find('div', class_='rating')
                    if rating_elem:
                        rating_text = rating_elem.get_text().strip()
                        rating_match = re.search(r'[\d,]+', rating_text)
                        if rating_match:
                            product_data['rating'] = float(rating_match.group().replace(',', '.'))
                    
                    # Количество отзывов
                    reviews_elem = card.find('span', class_='product-card__review') or card.find('div', class_='review')
                    if reviews_elem:
                        reviews_text = reviews_elem.get_text().strip()
                        reviews_match = re.search(r'[\d]+', reviews_text)
                        if reviews_match:
                            product_data['reviews_count'] = int(reviews_match.group())
                    
                    if product_data.get('name') and product_data.get('price'):
                        products.append(product_data)
                        
                except Exception as e:
                    print(f"Ошибка при парсинге карточки товара: {e}")
                    continue
            
            return products
            
        except Exception as e:
            print(f"Ошибка при парсинге результатов поиска {search_url}: {e}")
            return []
    
    def scrape_products(self):
        """Основной метод парсинга"""
        print("🚀 Начинаем парсинг товаров с Wildberries...")
        
        # Поисковые запросы для разных категорий
        search_queries = [
            'смартфон',
            'ноутбук',
            'одежда мужская',
            'одежда женская',
            'обувь мужская',
            'обувь женская',
            'бытовая техника',
            'красота и здоровье',
            'спорт',
            'книги',
            'игрушки',
            'дом и сад',
            'автотовары',
            'зоотовары',
            'канцтовары',
            'продукты питания',
            'ювелирные изделия',
            'часы',
            'сумки',
            'аксессуары',
            'мебель',
            'освещение',
            'текстиль',
            'посуда',
            'инструменты'
        ]
        
        all_products = []
        
        for query in search_queries:
            if self.scraped_count >= self.target_count:
                break
                
            search_url = f"{self.base_url}/catalog/0/search.aspx?search={query}"
            print(f"\n🔍 Поиск: {query}")
            
            products = self.parse_search_results(search_url)
            all_products.extend(products)
            self.scraped_count = len(all_products)
            
            print(f"Спарсено товаров: {self.scraped_count}/{self.target_count}")
            
            # Задержка между запросами
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
                """, [category_id, 'ru', "Парсенные товары", "Товары, спарсенные с Wildberries", category_id, 'ru'])
                
                # Создаем продавца
                cursor.execute("""
                    INSERT INTO products_seller (company_name, description, created_at, updated_at)
                    SELECT %s, %s, NOW(), NOW()
                    WHERE NOT EXISTS (SELECT 1 FROM products_seller WHERE company_name = %s)
                """, ["Wildberries Парсер", "Товары с Wildberries", "Wildberries Парсер"])
                
                cursor.execute("SELECT id FROM products_seller WHERE company_name = %s", ["Wildberries Парсер"])
                seller_id = cursor.fetchone()[0]
                
                # Создаем товар
                name = product_data.get('name', 'Товар без названия')
                price = product_data.get('price', 1000)
                description = f"Товар спарсен с Wildberries. {name}"
                sku = f"WB-{fake.unique.random_number(digits=6)}"
                rating = product_data.get('rating', round(random.uniform(3.5, 5.0), 2))
                reviews_count = product_data.get('reviews_count', random.randint(0, 50))
                
                cursor.execute("""
                    INSERT INTO products_product (category_id, seller_id, currency, price, sku, stock_quantity, is_active, rating, reviews_count, views_count, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                    RETURNING id
                """, [category_id, seller_id, 'RUB', price, sku, random.randint(10, 100), True, rating, reviews_count, random.randint(50, 500)])
                
                product_id = cursor.fetchone()[0]
                
                # Создаем перевод товара
                cursor.execute("""
                    INSERT INTO products_product_translation (master_id, language_code, name, description)
                    VALUES (%s, %s, %s, %s)
                """, [product_id, 'ru', name, description])
                
                # Сохраняем характеристики
                characteristics = [
                    ("Источник", "Wildberries"),
                    ("Тип", "Парсенный товар"),
                    ("Статус", "В наличии"),
                    ("Доставка", "Доступна"),
                    ("Гарантия", "Стандартная"),
                ]
                
                for i, (char_name, char_value) in enumerate(characteristics):
                    cursor.execute("""
                        INSERT INTO products_productcharacteristic (product_id, name, value, unit, "order")
                        VALUES (%s, %s, %s, %s, %s)
                    """, [product_id, char_name, char_value, "шт", i + 1])
                
                # Создаем магазин
                cursor.execute("""
                    INSERT INTO products_shop (phone, email, created_at, updated_at)
                    SELECT %s, %s, NOW(), NOW()
                    WHERE NOT EXISTS (SELECT 1 FROM products_shop WHERE phone = %s)
                """, ["+7 (495) 232-32-32", "store@wildberries.ru", "+7 (495) 232-32-32"])
                
                cursor.execute("SELECT id FROM products_shop WHERE phone = %s", ["+7 (495) 232-32-32"])
                shop_id = cursor.fetchone()[0]
                
                cursor.execute("""
                    INSERT INTO products_shop_translation (master_id, language_code, name, address, city)
                    SELECT %s, %s, %s, %s, %s
                    WHERE NOT EXISTS (SELECT 1 FROM products_shop_translation WHERE master_id = %s AND language_code = %s)
                """, [shop_id, 'ru', "Wildberries Store", "Москва, ул. Льва Толстого, 16", "Москва", shop_id, 'ru'])
                
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
    scraper = WildberriesScraper()
    
    # Парсим товары
    products = scraper.scrape_products()
    
    if products:
        # Сохраняем в базу данных
        save_products_to_db(products)
    else:
        print("❌ Не удалось спарсить товары")

if __name__ == '__main__':
    main()
