#!/usr/bin/env python
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
from fake_useragent import UserAgent
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from django.core.files.base import ContentFile
from django.utils import timezone
from django.utils.text import slugify
import random
import string

# Настройка логгера
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('scrape_ozon_products_postgres.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shoplist.settings')
django.setup()

from products.models import Category, Product, ProductCharacteristic, ProductImage, Seller, User

logger.info("=== НАЧАЛО ПАРСИНГА ТОВАРОВ С OZON В POSTGRESQL ===")

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
ua = UserAgent()
chrome_options = Options()
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_argument(f"user-agent={ua.random}")
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--disable-infobars")
chrome_options.add_argument("--ignore-certificate-errors")

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=chrome_options
)

# Расширенный список категорий Ozon с подкатегориями
CATEGORIES_STRUCTURE = {
    "Электроника": {
        "url": "https://www.ozon.ru/category/elektronika-15500/",
        "subcategories": {
            "Смартфоны": {
                "url": "https://www.ozon.ru/category/smartfony-15502/",
                "subcategories": {
                    "iPhone": "https://www.ozon.ru/category/smartfony-apple-15503/",
                    "Samsung": "https://www.ozon.ru/category/smartfony-samsung-15504/",
                    "Xiaomi": "https://www.ozon.ru/category/smartfony-xiaomi-15505/"
                }
            },
            "Ноутбуки": {
                "url": "https://www.ozon.ru/category/noutbuki-15692/",
                "subcategories": {
                    "Игровые ноутбуки": "https://www.ozon.ru/category/igrovye-noutbuki-15693/",
                    "Ультрабуки": "https://www.ozon.ru/category/ultrabuki-15694/",
                    "MacBook": "https://www.ozon.ru/category/noutbuki-apple-15695/"
                }
            },
            "Телевизоры": {
                "url": "https://www.ozon.ru/category/televizory-15567/",
                "subcategories": {
                    "4K телевизоры": "https://www.ozon.ru/category/4k-televizory-15568/",
                    "Smart TV": "https://www.ozon.ru/category/smart-tv-15569/",
                    "OLED телевизоры": "https://www.ozon.ru/category/oled-televizory-15570/"
                }
            },
            "Планшеты": {
                "url": "https://www.ozon.ru/category/planshety-15501/",
                "subcategories": {
                    "iPad": "https://www.ozon.ru/category/planshety-apple-15506/",
                    "Android планшеты": "https://www.ozon.ru/category/planshety-android-15507/"
                }
            }
        }
    },
    "Одежда и обувь": {
        "url": "https://www.ozon.ru/category/odezhda-i-obuv-11500/",
        "subcategories": {
            "Женская одежда": {
                "url": "https://www.ozon.ru/category/zhenskaya-odezhda-11501/",
                "subcategories": {
                    "Платья": "https://www.ozon.ru/category/platiya-11502/",
                    "Блузки": "https://www.ozon.ru/category/bluzki-11503/",
                    "Джинсы": "https://www.ozon.ru/category/dzhinsy-zhenskie-11504/"
                }
            },
            "Мужская одежда": {
                "url": "https://www.ozon.ru/category/muzhskaya-odezhda-11505/",
                "subcategories": {
                    "Рубашки": "https://www.ozon.ru/category/rubashki-11506/",
                    "Футболки": "https://www.ozon.ru/category/futbolki-11507/",
                    "Джинсы": "https://www.ozon.ru/category/dzhinsy-muzhskie-11508/"
                }
            },
            "Обувь": {
                "url": "https://www.ozon.ru/category/obuv-11617/",
                "subcategories": {
                    "Кроссовки": "https://www.ozon.ru/category/krossovki-11618/",
                    "Туфли": "https://www.ozon.ru/category/tufli-11619/",
                    "Сапоги": "https://www.ozon.ru/category/sapogi-11620/"
                }
            }
        }
    },
    "Дом и сад": {
        "url": "https://www.ozon.ru/category/dom-i-sad-14500/",
        "subcategories": {
            "Мебель": {
                "url": "https://www.ozon.ru/category/mebel-14501/",
                "subcategories": {
                    "Диваны": "https://www.ozon.ru/category/divany-14502/",
                    "Кровати": "https://www.ozon.ru/category/krovati-14503/",
                    "Столы": "https://www.ozon.ru/category/stoly-14504/"
                }
            },
            "Бытовая техника": {
                "url": "https://www.ozon.ru/category/bytovaya-tekhnika-14505/",
                "subcategories": {
                    "Холодильники": "https://www.ozon.ru/category/kholodilniki-14506/",
                    "Стиральные машины": "https://www.ozon.ru/category/stiralnye-mashiny-14507/",
                    "Пылесосы": "https://www.ozon.ru/category/pylesosy-14508/"
                }
            }
        }
    },
    "Красота и здоровье": {
        "url": "https://www.ozon.ru/category/krasota-i-zdorove-7500/",
        "subcategories": {
            "Косметика": {
                "url": "https://www.ozon.ru/category/kosmetika-7501/",
                "subcategories": {
                    "Декоративная косметика": "https://www.ozon.ru/category/dekorativnaya-kosmetika-7502/",
                    "Уход за кожей": "https://www.ozon.ru/category/ukhod-za-kozhey-7503/",
                    "Парфюмерия": "https://www.ozon.ru/category/parfyumeriya-7504/"
                }
            },
            "Уход за волосами": {
                "url": "https://www.ozon.ru/category/ukhod-za-volosami-7505/",
                "subcategories": {
                    "Шампуни": "https://www.ozon.ru/category/shampuni-7506/",
                    "Маски для волос": "https://www.ozon.ru/category/maski-dlya-volos-7507/"
                }
            }
        }
    },
    "Детские товары": {
        "url": "https://www.ozon.ru/category/detskie-tovary-7000/",
        "subcategories": {
            "Одежда для детей": {
                "url": "https://www.ozon.ru/category/odezhda-dlya-detey-7001/",
                "subcategories": {
                    "Для мальчиков": "https://www.ozon.ru/category/odezhda-dlya-malchikov-7002/",
                    "Для девочек": "https://www.ozon.ru/category/odezhda-dlya-devochek-7003/"
                }
            },
            "Игрушки": {
                "url": "https://www.ozon.ru/category/igrushki-7004/",
                "subcategories": {
                    "Конструкторы": "https://www.ozon.ru/category/konstruktory-7005/",
                    "Куклы": "https://www.ozon.ru/category/kukly-7006/"
                }
            }
        }
    }
}

def create_category_hierarchy():
    """Создает иерархию категорий в базе данных"""
    logger.info("Создание иерархии категорий...")
    
    for root_name, root_data in CATEGORIES_STRUCTURE.items():
        # Создаем корневую категорию
        slug = generate_unique_slug(root_name, Category)
        root_category, created = Category.objects.get_or_create(
            name=root_name,
            defaults={
                'slug': slug,
                'description': f"Товары категории {root_name} с Ozon",
                'is_active': True,
                'created_at': timezone.now()
            }
        )
        if created:
            logger.info(f"[OK] Создана корневая категория: {root_name}")
        
        # Создаем подкатегории 2-го уровня
        for sub_name, sub_data in root_data['subcategories'].items():
            slug = generate_unique_slug(sub_name, Category)
            sub_category, created = Category.objects.get_or_create(
                name=sub_name,
                parent=root_category,
                defaults={
                    'slug': slug,
                    'description': f"Товары подкатегории {sub_name}",
                    'is_active': True,
                    'created_at': timezone.now()
                }
            )
            if created:
                logger.info(f"[OK] Создана подкатегория 2-го уровня: {sub_name}")
            
            # Создаем подкатегории 3-го уровня
            if 'subcategories' in sub_data:
                for sub_sub_name, sub_sub_url in sub_data['subcategories'].items():
                    slug = generate_unique_slug(sub_sub_name, Category)
                    sub_sub_category, created = Category.objects.get_or_create(
                        name=sub_sub_name,
                        parent=sub_category,
                        defaults={
                            'slug': slug,
                            'description': f"Товары подкатегории {sub_sub_name}",
                            'is_active': True,
                            'created_at': timezone.now()
                        }
                    )
                    if created:
                        logger.info(f"[OK] Создана подкатегория 3-го уровня: {sub_sub_name}")

def parse_product(url):
    """Парсинг страницы товара"""
    try:
        driver.get(url)
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "h1"))
        )
        
        # Даем странице время на загрузку
        time.sleep(random.uniform(1, 2))
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Парсим основную информацию
        name_elem = soup.find("h1")
        if not name_elem:
            return None
        name = name_elem.text.strip()
        
        # Парсим цену - обновленные селекторы
        price = Decimal("0")
        price_elem = soup.select_one("span[data-widget='webPrice'] span.tsHeadline500Medium")
        if not price_elem:
            price_elem = soup.select_one("span[data-widget='webPrice']")
        if not price_elem:
            price_elem = soup.select_one(".tsHeadline500Medium")
        
        if price_elem:
            price_text = price_elem.text.replace("₽", "").replace(" ", "").replace(",", ".").strip()
            try:
                price = Decimal(price_text)
            except:
                # Логгируем ошибку, но продолжаем
                logger.warning(f"Не удалось распознать цену: {price_text}")
                price = Decimal("0")
        
        # Парсим описание - улучшенные селекторы
        description = ""
        desc_elem = soup.select_one("div[data-widget='webDescription']")
        if not desc_elem:
            # Новые селекторы для Ozon
            desc_elem = soup.select_one("div[data-widget='webDescription'] div")
        if not desc_elem:
            desc_elem = soup.select_one(".tsBodyL")
            
        if desc_elem:
            description = desc_elem.text.strip()[:2000]  # Ограничение длины
        
        # Парсим характеристики - обновленные селекторы
        characteristics = []
        char_section = soup.select_one("dl[data-widget='webCharacteristics']")
        if not char_section:
            char_section = soup.select_one("div[data-widget='webCharacteristics']")
        if not char_section:
            char_section = soup.select_one(".characteristics")
        
        if char_section:
            # Новый формат характеристик Ozon
            char_items = char_section.find_all("div", class_="v0v")
            if not char_items:
                char_items = char_section.find_all("div", class_="k6d")
            
            for char in char_items:
                name_elem = char.find("dt") or char.find("span", class_="v0v3")
                value_elem = char.find("dd") or char.find("span", class_="v0v4")
                if name_elem and value_elem:
                    char_name = name_elem.text.strip()
                    char_value = value_elem.text.strip()
                    characteristics.append({"name": char_name, "value": char_value})
        
        # Парсим изображения - более надежные селекторы
        images = []
        image_container = soup.select_one("div[data-widget='webGallery']")
        if image_container:
            image_elems = image_container.select("img")
        else:
            image_elems = soup.select("img[loading='lazy']")
        
        for img in image_elems[:5]:  # Максимум 5 изображений
            src = img.get("src") or img.get("data-src")
            if src and "http" in src and "ozon" in src:
                if src.startswith("//"):
                    src = "https:" + src
                images.append(src)
        
        # Если не нашли изображения, пробуем альтернативные источники
        if not images:
            image_elems = soup.select("img[alt*='товар'], img[alt*='product']")
            for img in image_elems[:3]:
                src = img.get("src") or img.get("data-src")
                if src and "http" in src:
                    if src.startswith("//"):
                        src = "https:" + src
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
    """Скачивание изображения с обработкой ошибок"""
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
    logger.error(f"Не удалось скачать изображение после {max_retries} попыток: {url}")
    return None

def get_products_from_category(category_url, max_products=50):
    """Получает список товаров из категории"""
    try:
        driver.get(category_url)
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-widget='searchResultsV2']"))
        )
        
        # Прокручиваем страницу для загрузки товаров
        for _ in range(3):
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
    # Очищаем старые данные
    logger.info("Очистка старых товаров...")
    # Удаляем только товары от Ozon продавца
    products_to_delete = Product.objects.filter(seller=seller)
    ProductCharacteristic.objects.filter(product__in=products_to_delete).delete()
    ProductImage.objects.filter(product__in=products_to_delete).delete()
    products_to_delete.delete()
    logger.info(f"Удалено {products_to_delete.count()} старых товаров Ozon")
    
    # Создаем иерархию категорий
    create_category_hierarchy()
    
    total_products = 0
    MAX_PRODUCTS = 100  # Требуется 100 товаров
    
    for root_name, root_data in CATEGORIES_STRUCTURE.items():
        if total_products >= MAX_PRODUCTS:
            break
            
        logger.info(f"Обработка корневой категории: {root_name}")
        
        # Получаем корневую категорию из базы
        root_category = Category.objects.get(name=root_name)
        
        # Обрабатываем подкатегории 2-го уровня
        for sub_name, sub_data in root_data['subcategories'].items():
            if total_products >= MAX_PRODUCTS:
                break
                
            logger.info(f"Обработка подкатегории: {sub_name}")
            
            # Получаем подкатегорию 2-го уровня
            sub_category = Category.objects.get(name=sub_name, parent=root_category)
            
            # Обрабатываем подкатегории 3-го уровня
            if 'subcategories' in sub_data:
                for sub_sub_name, sub_sub_url in sub_data['subcategories'].items():
                    if total_products >= MAX_PRODUCTS:
                        break
                        
                    logger.info(f"Обработка подкатегории 3-го уровня: {sub_sub_name}")
                    
                    # Получаем подкатегорию 3-го уровня
                    sub_sub_category = Category.objects.get(name=sub_sub_name, parent=sub_category)
                    
                    # Получаем товары из этой подкатегории
                    product_links = get_products_from_category(sub_sub_url, 10)  # 10 товаров на категорию
                    
                    # Обрабатываем товары
                    for product_url in product_links:
                        if total_products >= MAX_PRODUCTS:
                            break
                            
                        logger.info(f"Парсинг товара {total_products+1}/{MAX_PRODUCTS}: {product_url}")
                        product_data = parse_product(product_url)
                        
                        if not product_data or not product_data["name"] or product_data["price"] <= 0:
                            logger.warning("Пропуск товара из-за отсутствия данных")
                            continue
                        
                        # Создаем товар в базе
                        try:
                            product = Product.objects.create(
                                name=product_data["name"][:255],
                                description=product_data["description"],
                                price=product_data["price"],
                                category=sub_sub_category,
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
                                    name=char["name"][:100],
                                    value=char["value"][:255]
                                )
                            
                            # Добавляем изображения
                            for i, img_url in enumerate(product_data["images"][:3]):  # Макс 3 изображения
                                if not img_url:
                                    continue
                                    
                                image_data = download_image(img_url)
                                if image_data:
                                    img = ProductImage(
                                        product=product,
                                        alt_text=f"{product.name} - изображение {i+1}"[:255],
                                        is_primary=(i == 0),
                                        order=i,
                                        created_at=timezone.now()
                                    )
                                    img.image.save(
                                        f"product_{product.id}_img_{i}.jpg",
                                        image_data,
                                        save=True
                                    )
                                    time.sleep(0.3)  # Уменьшенная задержка
                                else:
                                    logger.warning(f"Не удалось загрузить изображение: {img_url}")
                            
                            total_products += 1
                            logger.info(f"[OK] Добавлен товар: {product.name} (цена: {product.price}₽)")
                            
                        except Exception as e:
                            logger.error(f"Ошибка при создании товара: {str(e)[:200]}")
                        
                        # Уменьшенная задержка между товарами
                        time.sleep(random.uniform(1, 2))
    
    driver.quit()
    logger.info(f"\n=== РЕЗУЛЬТАТ ===")
    logger.info(f"Успешно добавлено: {total_products} товаров")
    logger.info(f"Характеристик: {ProductCharacteristic.objects.count()}")
    logger.info(f"Изображений: {ProductImage.objects.count()}")
    logger.info(f"Категорий: {Category.objects.count()}")
    logger.info(f"\n🎉 Товары успешно добавлены в PostgreSQL!")

if __name__ == "__main__":
    main()
