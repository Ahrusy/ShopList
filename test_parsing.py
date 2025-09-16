#!/usr/bin/env python
"""
Тестовый скрипт для парсинга небольшого количества товаров
"""
import os
import sys
import django
import time
import random
import requests
import logging
from decimal import Decimal
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from django.core.files.base import ContentFile
from django.utils import timezone

# Настройка логгера
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('test_parsing.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shoplist.settings')
django.setup()

from products.models import Category, Product, ProductCharacteristic, ProductImage, Seller, User

logger.info("=== ТЕСТОВЫЙ ПАРСИНГ ТОВАРОВ С OZON ===")

# Создаем продавца
user, _ = User.objects.get_or_create(
    username='ozon_seller',
    defaults={
        'email': 'seller@ozon.ru',
        'role': 'seller',
        'first_name': 'Ozon',
        'last_name': 'Seller'
    }
)
if not user.password:
    user.set_password('password123')
    user.save()

seller, _ = Seller.objects.get_or_create(
    user=user,
    defaults={
        'company_name': 'Ozon Marketplace',
        'description': 'Официальный продавец маркетплейса Ozon',
        'commission_rate': Decimal('7.0'),
        'is_verified': True
    }
)

# Настройка Selenium
chrome_options = Options()
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36")
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=chrome_options
)

# Тестовые категории
TEST_CATEGORIES = [
    ("https://www.ozon.ru/category/smartfony-15502/", "Смартфоны"),
    ("https://www.ozon.ru/category/noutbuki-15692/", "Ноутбуки"),
]

def create_test_categories():
    """Создает тестовые категории"""
    logger.info("Создание тестовых категорий...")
    
    for category_url, category_name in TEST_CATEGORIES:
        # Проверяем существование категории по slug
        slug = category_name.lower().replace(" ", "-")
        try:
            category = Category.objects.get(slug=slug)
            logger.info(f"Категория уже существует: {category_name}")
        except Category.DoesNotExist:
            category = Category.objects.create(
                slug=slug,
                is_active=True,
                created_at=timezone.now()
            )
            # Устанавливаем переводы
            category.set_current_language('ru')
            category.name = category_name
            category.description = f"Тестовые товары категории {category_name}"
            category.save()
            logger.info(f"Создана категория: {category_name}")

def parse_product(url):
    """Парсинг страницы товара"""
    try:
        driver.get(url)
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "h1"))
        )
        
        time.sleep(random.uniform(2, 4))
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Парсим основную информацию
        name_elem = soup.find("h1")
        if not name_elem:
            return None
        name = name_elem.text.strip()
        
        # Парсим цену
        price = Decimal("0")
        price_elem = soup.select_one("span[data-widget='webPrice']")
        if not price_elem:
            price_elem = soup.select_one(".tsBody500Medium")
        
        if price_elem:
            price_text = price_elem.text.replace("₽", "").replace(" ", "").replace(",", ".").strip()
            try:
                price = Decimal(price_text)
            except:
                price = Decimal("0")
        
        # Парсим описание
        description = ""
        desc_elem = soup.select_one("div[data-widget='webDescription']")
        if not desc_elem:
            desc_elem = soup.select_one(".tsBodyL")
        if desc_elem:
            description = desc_elem.text.strip()
        
        # Парсим характеристики
        characteristics = []
        char_section = soup.select_one("dl[data-widget='webCharacteristics']")
        if not char_section:
            char_section = soup.select_one(".characteristics")
        
        if char_section:
            for char in char_section.find_all("div", class_="k6d"):
                name_elem = char.find("dt")
                value_elem = char.find("dd")
                if name_elem and value_elem:
                    char_name = name_elem.text.strip()
                    char_value = value_elem.text.strip()
                    characteristics.append({"name": char_name, "value": char_value})
        
        # Парсим изображения
        images = []
        image_elems = soup.select("img[loading='lazy']")
        for img in image_elems:
            src = img.get("src") or img.get("data-src")
            if src and "http" in src and "ozon" in src:
                images.append(src)
        
        return {
            "name": name,
            "description": description,
            "price": price,
            "characteristics": characteristics,
            "images": images
        }
    except Exception as e:
        logger.error(f"Ошибка при парсинге товара {url}: {e}")
        return None

def download_image(url, max_retries=3):
    """Скачивание изображения"""
    for attempt in range(max_retries):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'
            }
            response = requests.get(url, timeout=30, headers=headers, verify=False)
            response.raise_for_status()
            return ContentFile(response.content)
        except Exception as e:
            logger.warning(f"Попытка {attempt+1}/{max_retries}: Ошибка при скачивании {url}: {e}")
            time.sleep(1 + attempt)
    return None

def get_products_from_category(category_url, max_products=5):
    """Получает список товаров из категории"""
    try:
        driver.get(category_url)
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-widget='searchResultsV2']"))
        )
        
        # Прокручиваем страницу
        for _ in range(2):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(random.uniform(2, 4))
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        product_links = []
        
        # Собираем ссылки на товары
        for link in soup.select("a[href*='/product/']"):
            href = link.get("href")
            if href and "https://www.ozon.ru" not in href:
                href = f"https://www.ozon.ru{href}"
            if href and href not in product_links and len(product_links) < max_products:
                product_links.append(href)
        
        return product_links[:max_products]
    except Exception as e:
        logger.error(f"Ошибка при получении товаров из категории {category_url}: {e}")
        return []

def main():
    # Очищаем старые тестовые данные
    logger.info("Очистка старых тестовых товаров...")
    ProductCharacteristic.objects.all().delete()
    ProductImage.objects.all().delete()
    Product.objects.all().delete()
    logger.info("Старые товары удалены")
    
    # Создаем тестовые категории
    create_test_categories()
    
    total_products = 0
    MAX_PRODUCTS = 10  # Тестируем с 10 товарами
    
    for category_url, category_name in TEST_CATEGORIES:
        if total_products >= MAX_PRODUCTS:
            break
            
        logger.info(f"Обработка категории: {category_name}")
        
        # Получаем категорию из базы
        slug = category_name.lower().replace(" ", "-")
        category = Category.objects.get(slug=slug)
        
        # Получаем товары из категории
        product_links = get_products_from_category(category_url, 5)
        
        # Обрабатываем товары
        for product_url in product_links:
            if total_products >= MAX_PRODUCTS:
                break
                
            logger.info(f"Парсинг товара {total_products+1}/{MAX_PRODUCTS}: {product_url}")
            product_data = parse_product(product_url)
            
            if not product_data or not product_data["name"] or product_data["price"] <= 0:
                continue
            
            # Создаем товар в базе
            try:
                product = Product.objects.create(
                    name=product_data["name"],
                    description=product_data["description"],
                    price=product_data["price"],
                    category=category,
                    seller=seller,
                    stock_quantity=random.randint(10, 100),
                    rating=Decimal(random.uniform(3.5, 5.0)).quantize(Decimal('0.01')),
                    reviews_count=random.randint(5, 100),
                    created_at=timezone.now()
                )
                
                # Добавляем характеристики
                for char in product_data["characteristics"]:
                    ProductCharacteristic.objects.create(
                        product=product,
                        name=char["name"],
                        value=char["value"]
                    )
                
                # Добавляем изображения
                for i, img_url in enumerate(product_data["images"][:3]):
                    image_data = download_image(img_url)
                    if image_data:
                        img = ProductImage(
                            product=product,
                            alt_text=f"{product.name} - изображение {i+1}",
                            is_primary=(i == 0),
                            order=i,
                            created_at=timezone.now()
                        )
                        img.image.save(
                            f"product_{product.id}_img_{i}.jpg", 
                            image_data,
                            save=True
                        )
                        time.sleep(0.5)
                
                total_products += 1
                logger.info(f"Добавлен товар: {product.name} (цена: {product.price}₽)")
                
            except Exception as e:
                logger.error(f"Ошибка при создании товара: {e}")
            
            # Задержка между товарами
            time.sleep(random.uniform(2, 5))
    
    driver.quit()
    logger.info(f"\n=== РЕЗУЛЬТАТ ТЕСТА ===")
    logger.info(f"Успешно добавлено: {total_products} товаров")
    logger.info(f"Характеристик: {ProductCharacteristic.objects.count()}")
    logger.info(f"Изображений: {ProductImage.objects.count()}")
    logger.info(f"Категорий: {Category.objects.count()}")
    logger.info(f"\nТест завершен!")

if __name__ == "__main__":
    main()
