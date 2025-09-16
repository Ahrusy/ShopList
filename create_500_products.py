#!/usr/bin/env python
"""
Изолированный скрипт для создания 500 товаров
Использует только необходимые компоненты Django
"""
import os
import sys
import django
import random
import logging
from decimal import Decimal

# Настройка логгера
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('create_500_products.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Минимальные настройки Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shoplist.settings_simple')

# Настройка Django
django.setup()

# Импортируем только необходимые компоненты
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import connection
from django.core.management import execute_from_command_line

logger.info("=== СОЗДАНИЕ 500 ТОВАРОВ ===")

# Определяем модели прямо в скрипте
class User(AbstractUser):
    """Кастомная модель пользователя"""
    ROLE_CHOICES = [
        ('user', 'Покупатель'),
        ('seller', 'Продавец'),
        ('manager', 'Менеджер'),
        ('admin', 'Администратор'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user', verbose_name="Роль")

    class Meta:
        db_table = 'products_simple_user'

class Category(models.Model):
    """Модель категории товаров"""
    name = models.CharField(max_length=100, verbose_name="Название")
    description = models.TextField(blank=True, verbose_name="Описание")
    slug = models.SlugField(max_length=100, unique=True, verbose_name="URL-адрес")
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children', verbose_name="Родительская категория")
    is_active = models.BooleanField(default=True, verbose_name="Активна")
    sort_order = models.PositiveIntegerField(default=0, verbose_name="Порядок сортировки")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    def __str__(self):
        return self.name

    @property
    def level(self):
        """Возвращает уровень вложенности категории"""
        level = 0
        parent = self.parent
        while parent:
            level += 1
            parent = parent.parent
        return level

    class Meta:
        db_table = 'products_simple_category'
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ['sort_order', 'slug']

class Seller(models.Model):
    """Модель продавца"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='seller_profile', verbose_name="Пользователь")
    company_name = models.CharField(max_length=255, verbose_name="Название компании")
    description = models.TextField(blank=True, verbose_name="Описание")
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=5.00, verbose_name="Ставка комиссии (%)")
    is_verified = models.BooleanField(default=False, verbose_name="Верифицирован")
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00, verbose_name="Рейтинг")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата регистрации")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    
    def __str__(self):
        return self.company_name
    
    class Meta:
        db_table = 'products_simple_seller'
        verbose_name = "Продавец"
        verbose_name_plural = "Продавцы"
        ordering = ['-created_at']

class Product(models.Model):
    """Модель товара"""
    name = models.CharField(max_length=255, verbose_name="Название")
    description = models.TextField(verbose_name="Описание")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="Цена со скидкой")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='products', verbose_name="Категория")
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE, related_name='products', null=True, blank=True, verbose_name="Продавец")
    sku = models.CharField(max_length=100, unique=True, blank=True, verbose_name="Артикул")
    stock_quantity = models.PositiveIntegerField(default=0, verbose_name="Количество на складе")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00, verbose_name="Рейтинг")
    reviews_count = models.PositiveIntegerField(default=0, verbose_name="Количество отзывов")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'products_simple_product'
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        ordering = ['-created_at']

class ProductCharacteristic(models.Model):
    """Модель характеристики товара"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='characteristics', verbose_name="Товар")
    name = models.CharField(max_length=100, verbose_name="Название характеристики")
    value = models.CharField(max_length=255, verbose_name="Значение")
    unit = models.CharField(max_length=20, blank=True, verbose_name="Единица измерения")
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок")
    
    def __str__(self):
        return f"{self.product.name} - {self.name}: {self.value}"
    
    class Meta:
        db_table = 'products_simple_productcharacteristic'
        verbose_name = "Характеристика товара"
        verbose_name_plural = "Характеристики товаров"
        ordering = ['order', 'name']

# Реальные данные товаров
REAL_PRODUCTS_DATA = [
    {
        "name": "iPhone 15 Pro Max 256GB Natural Titanium",
        "description": "Новейший смартфон Apple с титановым корпусом, чипом A17 Pro и камерой 48 МП. Поддержка 5G, Face ID, беспроводная зарядка. Дисплей Super Retina XDR 6.7 дюйма с технологией ProMotion.",
        "price": Decimal("99990.00"),
        "category": "Смартфоны",
        "characteristics": [
            {"name": "Диагональ экрана", "value": "6.7", "unit": "дюйма"},
            {"name": "Разрешение экрана", "value": "2796x1290", "unit": "пикселей"},
            {"name": "Процессор", "value": "Apple A17 Pro"},
            {"name": "Объем памяти", "value": "256", "unit": "ГБ"},
            {"name": "Оперативная память", "value": "8", "unit": "ГБ"},
            {"name": "Основная камера", "value": "48", "unit": "МП"},
            {"name": "Фронтальная камера", "value": "12", "unit": "МП"},
            {"name": "Аккумулятор", "value": "4422", "unit": "мАч"},
            {"name": "Операционная система", "value": "iOS 17"},
            {"name": "Материал корпуса", "value": "Титан"},
            {"name": "Цвет", "value": "Натуральный титан"},
            {"name": "Водозащита", "value": "IP68"},
            {"name": "Беспроводная зарядка", "value": "Да"},
            {"name": "5G", "value": "Да"},
            {"name": "Face ID", "value": "Да"}
        ]
    },
    {
        "name": "Samsung Galaxy S24 Ultra 512GB Titanium Black",
        "description": "Флагманский смартфон Samsung с S Pen, камерой 200 МП и экраном Dynamic AMOLED 2X. Искусственный интеллект Galaxy AI. Процессор Snapdragon 8 Gen 3 для Galaxy.",
        "price": Decimal("119990.00"),
        "category": "Смартфоны",
        "characteristics": [
            {"name": "Диагональ экрана", "value": "6.8", "unit": "дюйма"},
            {"name": "Разрешение экрана", "value": "3120x1440", "unit": "пикселей"},
            {"name": "Процессор", "value": "Snapdragon 8 Gen 3"},
            {"name": "Объем памяти", "value": "512", "unit": "ГБ"},
            {"name": "Оперативная память", "value": "12", "unit": "ГБ"},
            {"name": "Основная камера", "value": "200", "unit": "МП"},
            {"name": "Фронтальная камера", "value": "12", "unit": "МП"},
            {"name": "Аккумулятор", "value": "5000", "unit": "мАч"},
            {"name": "Операционная система", "value": "Android 14"},
            {"name": "Материал корпуса", "value": "Титан"},
            {"name": "Цвет", "value": "Титан черный"},
            {"name": "S Pen", "value": "Да"},
            {"name": "Водозащита", "value": "IP68"},
            {"name": "Беспроводная зарядка", "value": "Да"},
            {"name": "5G", "value": "Да"}
        ]
    },
    {
        "name": "MacBook Pro 16 M3 Max 1TB Space Gray",
        "description": "Профессиональный ноутбук Apple с чипом M3 Max, дисплеем Liquid Retina XDR и до 22 часов работы от батареи. Идеален для профессиональной работы с видео, графикой и разработки.",
        "price": Decimal("299990.00"),
        "category": "Ноутбуки",
        "characteristics": [
            {"name": "Диагональ экрана", "value": "16.2", "unit": "дюйма"},
            {"name": "Разрешение экрана", "value": "3456x2234", "unit": "пикселей"},
            {"name": "Процессор", "value": "Apple M3 Max"},
            {"name": "Объем памяти", "value": "1", "unit": "ТБ SSD"},
            {"name": "Оперативная память", "value": "32", "unit": "ГБ"},
            {"name": "Графический процессор", "value": "40-ядерный GPU"},
            {"name": "Время работы от батареи", "value": "22", "unit": "часов"},
            {"name": "Операционная система", "value": "macOS Sonoma"},
            {"name": "Материал корпуса", "value": "Алюминий"},
            {"name": "Цвет", "value": "Серый космос"},
            {"name": "Вес", "value": "2.16", "unit": "кг"},
            {"name": "Порты", "value": "3x Thunderbolt 4, HDMI, SDXC"},
            {"name": "Wi-Fi", "value": "Wi-Fi 6E"},
            {"name": "Bluetooth", "value": "5.3"}
        ]
    }
]

# Шаблоны для генерации дополнительных товаров
PRODUCT_TEMPLATES = {
    "Смартфоны": [
        {"name": "OnePlus 12", "base_price": 59990, "brand": "OnePlus"},
        {"name": "Google Pixel 8", "base_price": 79990, "brand": "Google"},
        {"name": "Huawei P60 Pro", "base_price": 89990, "brand": "Huawei"},
        {"name": "Nothing Phone 2", "base_price": 39990, "brand": "Nothing"},
        {"name": "Realme GT 5", "base_price": 34990, "brand": "Realme"},
        {"name": "Vivo X100 Pro", "base_price": 69990, "brand": "Vivo"},
        {"name": "Oppo Find X6", "base_price": 79990, "brand": "Oppo"},
    ],
    "Ноутбуки": [
        {"name": "Dell XPS 15", "base_price": 199990, "brand": "Dell"},
        {"name": "HP Spectre x360", "base_price": 179990, "brand": "HP"},
        {"name": "Lenovo ThinkPad X1", "base_price": 249990, "brand": "Lenovo"},
        {"name": "MSI Creator 15", "base_price": 159990, "brand": "MSI"},
        {"name": "Acer Swift 5", "base_price": 99990, "brand": "Acer"},
        {"name": "Razer Blade 15", "base_price": 199990, "brand": "Razer"},
        {"name": "Gigabyte Aero 16", "base_price": 189990, "brand": "Gigabyte"},
    ],
    "Телевизоры": [
        {"name": "LG OLED C3", "base_price": 149990, "brand": "LG"},
        {"name": "Samsung QLED Q80C", "base_price": 129990, "brand": "Samsung"},
        {"name": "TCL QLED 55C735", "base_price": 79990, "brand": "TCL"},
        {"name": "Hisense U8K", "base_price": 89990, "brand": "Hisense"},
        {"name": "Xiaomi TV A2", "base_price": 59990, "brand": "Xiaomi"},
        {"name": "Philips OLED 806", "base_price": 139990, "brand": "Philips"},
        {"name": "Panasonic LZ2000", "base_price": 179990, "brand": "Panasonic"},
    ],
    "Планшеты": [
        {"name": "Samsung Galaxy Tab S9", "base_price": 69990, "brand": "Samsung"},
        {"name": "Huawei MatePad Pro", "base_price": 59990, "brand": "Huawei"},
        {"name": "Lenovo Tab P11 Pro", "base_price": 49990, "brand": "Lenovo"},
        {"name": "Xiaomi Pad 6", "base_price": 39990, "brand": "Xiaomi"},
        {"name": "Honor Pad 9", "base_price": 29990, "brand": "Honor"},
        {"name": "Realme Pad 2", "base_price": 34990, "brand": "Realme"},
        {"name": "Oppo Pad Air", "base_price": 24990, "brand": "Oppo"},
    ]
}

def create_tables():
    """Создает таблицы в базе данных"""
    logger.info("Создание таблиц в базе данных...")
    
    with connection.cursor() as cursor:
        # Создаем таблицу пользователей
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products_simple_user (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                password VARCHAR(128) NOT NULL,
                last_login DATETIME,
                is_superuser BOOLEAN NOT NULL,
                username VARCHAR(150) NOT NULL UNIQUE,
                first_name VARCHAR(150) NOT NULL,
                last_name VARCHAR(150) NOT NULL,
                email VARCHAR(254) NOT NULL,
                is_staff BOOLEAN NOT NULL,
                is_active BOOLEAN NOT NULL,
                date_joined DATETIME NOT NULL,
                role VARCHAR(20) NOT NULL DEFAULT 'user'
            )
        """)
        
        # Создаем таблицу категорий
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products_simple_category (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) NOT NULL,
                description TEXT NOT NULL,
                slug VARCHAR(100) NOT NULL UNIQUE,
                parent_id INTEGER REFERENCES products_simple_category(id),
                is_active BOOLEAN NOT NULL DEFAULT 1,
                sort_order INTEGER NOT NULL DEFAULT 0,
                created_at DATETIME NOT NULL,
                updated_at DATETIME NOT NULL
            )
        """)
        
        # Создаем таблицу продавцов
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products_simple_seller (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL UNIQUE REFERENCES products_simple_user(id),
                company_name VARCHAR(255) NOT NULL,
                description TEXT NOT NULL,
                commission_rate DECIMAL(5,2) NOT NULL DEFAULT 5.00,
                is_verified BOOLEAN NOT NULL DEFAULT 0,
                rating DECIMAL(3,2) NOT NULL DEFAULT 0.00,
                created_at DATETIME NOT NULL,
                updated_at DATETIME NOT NULL
            )
        """)
        
        # Создаем таблицу товаров
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products_simple_product (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(255) NOT NULL,
                description TEXT NOT NULL,
                price DECIMAL(10,2) NOT NULL,
                discount_price DECIMAL(10,2),
                category_id INTEGER REFERENCES products_simple_category(id),
                seller_id INTEGER REFERENCES products_simple_seller(id),
                sku VARCHAR(100) UNIQUE,
                stock_quantity INTEGER NOT NULL DEFAULT 0,
                is_active BOOLEAN NOT NULL DEFAULT 1,
                rating DECIMAL(3,2) NOT NULL DEFAULT 0.00,
                reviews_count INTEGER NOT NULL DEFAULT 0,
                created_at DATETIME NOT NULL,
                updated_at DATETIME NOT NULL
            )
        """)
        
        # Создаем таблицу характеристик
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products_simple_productcharacteristic (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL REFERENCES products_simple_product(id),
                name VARCHAR(100) NOT NULL,
                value VARCHAR(255) NOT NULL,
                unit VARCHAR(20) NOT NULL DEFAULT '',
                order_field INTEGER NOT NULL DEFAULT 0
            )
        """)
    
    logger.info("Таблицы созданы успешно")

def create_categories():
    """Создает 3-уровневую иерархию категорий"""
    logger.info("Создание иерархии категорий...")
    
    categories_data = {
        "Электроника": {
            "subcategories": {
                "Смартфоны": {},
                "Ноутбуки": {},
                "Телевизоры": {},
                "Планшеты": {},
                "Наушники": {},
                "Часы": {}
            }
        },
        "Одежда и обувь": {
            "subcategories": {
                "Мужская одежда": {},
                "Женская одежда": {},
                "Детская одежда": {},
                "Обувь": {},
                "Аксессуары": {}
            }
        },
        "Дом и сад": {
            "subcategories": {
                "Мебель": {},
                "Декор": {},
                "Кухня": {},
                "Спальня": {},
                "Ванная": {}
            }
        },
        "Спорт и отдых": {
            "subcategories": {
                "Фитнес": {},
                "Игры": {},
                "Туризм": {},
                "Водные виды спорта": {},
                "Зимние виды спорта": {}
            }
        },
        "Красота и здоровье": {
            "subcategories": {
                "Косметика": {},
                "Парфюмерия": {},
                "Уход за кожей": {},
                "Витамины": {},
                "Здоровье": {}
            }
        }
    }
    
    created_categories = {}
    
    with connection.cursor() as cursor:
        for root_name, root_data in categories_data.items():
            # Создаем корневую категорию
            cursor.execute("""
                INSERT OR IGNORE INTO products_simple_category 
                (name, description, slug, parent_id, is_active, sort_order, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
            """, (root_name, f"Товары категории {root_name}", 
                  root_name.lower().replace(" ", "-").replace("и", "i"), None, True, 0))
            
            # Получаем ID корневой категории
            cursor.execute("SELECT id FROM products_simple_category WHERE name = ?", (root_name,))
            root_id = cursor.fetchone()[0]
            created_categories[root_name] = root_id
            
            # Создаем подкатегории 2-го уровня
            for sub_name in root_data['subcategories']:
                cursor.execute("""
                    INSERT OR IGNORE INTO products_simple_category 
                    (name, description, slug, parent_id, is_active, sort_order, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
                """, (sub_name, f"Товары подкатегории {sub_name}", 
                      sub_name.lower().replace(" ", "-").replace("и", "i"), root_id, True, 0))
                
                # Получаем ID подкатегории
                cursor.execute("SELECT id FROM products_simple_category WHERE name = ? AND parent_id = ?", (sub_name, root_id))
                sub_id = cursor.fetchone()[0]
                created_categories[sub_name] = sub_id
    
    logger.info(f"Создано {len(created_categories)} категорий")
    return created_categories

def create_seller():
    """Создает продавца"""
    logger.info("Создание продавца...")
    
    with connection.cursor() as cursor:
        # Создаем пользователя
        cursor.execute("""
            INSERT OR IGNORE INTO products_simple_user 
            (username, email, password, is_superuser, is_staff, is_active, date_joined, role)
            VALUES (?, ?, ?, ?, ?, ?, datetime('now'), ?)
        """, ('marketplace_seller', 'seller@marketplace.ru', 'pbkdf2_sha256$test', False, False, True, 'seller'))
        
        # Получаем ID пользователя
        cursor.execute("SELECT id FROM products_simple_user WHERE username = ?", ('marketplace_seller',))
        user_id = cursor.fetchone()[0]
        
        # Создаем продавца
        cursor.execute("""
            INSERT OR IGNORE INTO products_simple_seller 
            (user_id, company_name, description, commission_rate, is_verified, rating, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
        """, (user_id, 'Marketplace Store', 'Официальный продавец маркетплейса', 5.0, True, 5.0))
        
        # Получаем ID продавца
        cursor.execute("SELECT id FROM products_simple_seller WHERE user_id = ?", (user_id,))
        seller_id = cursor.fetchone()[0]
    
    logger.info("Продавец создан")
    return seller_id

def create_products(categories, seller_id, target_count=500):
    """Создает товары"""
    logger.info(f"Создание {target_count} товаров...")
    
    created = 0
    
    # Создаем реальные товары
    for product_data in REAL_PRODUCTS_DATA:
        try:
            category_id = categories[product_data["category"]]
            
            with connection.cursor() as cursor:
                # Создаем товар
                cursor.execute("""
                    INSERT INTO products_simple_product 
                    (name, description, price, category_id, seller_id, sku, stock_quantity, is_active, rating, reviews_count, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
                """, (
                    product_data["name"],
                    product_data["description"],
                    float(product_data["price"]),
                    category_id,
                    seller_id,
                    f"PRD-{random.randint(100000, 999999)}",
                    random.randint(10, 100),
                    True,
                    round(random.uniform(4.0, 5.0), 2),
                    random.randint(10, 500)
                ))
                
                product_id = cursor.lastrowid
                
                # Добавляем характеристики
                for char_data in product_data["characteristics"]:
                    cursor.execute("""
                        INSERT INTO products_simple_productcharacteristic 
                        (product_id, name, value, unit, order_field)
                        VALUES (?, ?, ?, ?, ?)
                    """, (product_id, char_data["name"], char_data["value"], char_data.get("unit", ""), 0))
                
                created += 1
                logger.info(f"Создан товар: {product_data['name']} (цена: {product_data['price']}₽)")
                
        except Exception as e:
            logger.error(f"Ошибка при создании товара {product_data['name']}: {e}")
    
    # Создаем дополнительные товары
    for category_name, category_id in categories.items():
        if created >= target_count:
            break
            
        if category_name not in PRODUCT_TEMPLATES:
            continue
            
        template_list = PRODUCT_TEMPLATES[category_name]
        
        for i in range(min(target_count - created, len(template_list) * 20)):
            template = template_list[i % len(template_list)]
            
            try:
                # Генерируем вариации названия
                variations = ["", " Plus", " Pro", " Max", " Ultra", " SE", " Lite", " 256GB", " 512GB", " 1TB"]
                variation = random.choice(variations)
                name = template["name"] + variation
                
                # Генерируем цену с вариацией
                price_variation = random.uniform(0.7, 1.3)
                price = int(template["base_price"] * price_variation)
                
                with connection.cursor() as cursor:
                    # Создаем товар
                    cursor.execute("""
                        INSERT INTO products_simple_product 
                        (name, description, price, category_id, seller_id, sku, stock_quantity, is_active, rating, reviews_count, created_at, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
                    """, (
                        name,
                        f"Высококачественный {category_name.lower()} {template['brand']} с отличными характеристиками и современным дизайном. Идеально подходит для повседневного использования.",
                        price,
                        category_id,
                        seller_id,
                        f"PRD-{random.randint(100000, 999999)}",
                        random.randint(5, 100),
                        True,
                        round(random.uniform(3.5, 5.0), 2),
                        random.randint(5, 300)
                    ))
                    
                    product_id = cursor.lastrowid
                    
                    # Добавляем базовые характеристики
                    base_characteristics = [
                        {"name": "Бренд", "value": template["brand"]},
                        {"name": "Модель", "value": name},
                        {"name": "Цвет", "value": random.choice(["Черный", "Белый", "Серый", "Синий", "Красный", "Золотой", "Серебряный"])},
                        {"name": "Гарантия", "value": "12 месяцев"},
                        {"name": "Страна производства", "value": random.choice(["Китай", "Южная Корея", "США", "Япония", "Германия"])},
                        {"name": "Вес", "value": f"{random.randint(100, 2000)}", "unit": "г"},
                        {"name": "Размеры", "value": f"{random.randint(50, 300)}x{random.randint(50, 300)}x{random.randint(5, 50)}", "unit": "мм"},
                    ]
                    
                    # Добавляем специфичные характеристики для категории
                    if category_name == "Смартфоны":
                        base_characteristics.extend([
                            {"name": "Диагональ экрана", "value": f"{random.uniform(5.0, 7.0):.1f}", "unit": "дюйма"},
                            {"name": "Разрешение экрана", "value": random.choice(["1080x2400", "1440x3200", "1179x2556"])},
                            {"name": "Процессор", "value": random.choice(["Snapdragon 8 Gen 3", "Apple A17 Pro", "MediaTek Dimensity 9000"])},
                            {"name": "Объем памяти", "value": random.choice(["128", "256", "512", "1"]), "unit": "ГБ"},
                            {"name": "Оперативная память", "value": random.choice(["8", "12", "16"]), "unit": "ГБ"},
                        ])
                    elif category_name == "Ноутбуки":
                        base_characteristics.extend([
                            {"name": "Диагональ экрана", "value": random.choice(["13.3", "14", "15.6", "16", "17.3"]), "unit": "дюйма"},
                            {"name": "Разрешение экрана", "value": random.choice(["1920x1080", "2560x1440", "2880x1800", "3456x2234"])},
                            {"name": "Процессор", "value": random.choice(["Intel Core i7", "Intel Core i9", "AMD Ryzen 7", "Apple M3"])},
                            {"name": "Видеокарта", "value": random.choice(["NVIDIA RTX 4060", "NVIDIA RTX 4070", "AMD Radeon RX 7600", "Intel Iris Xe"])},
                            {"name": "Объем памяти", "value": random.choice(["512", "1", "2"]), "unit": "ТБ SSD"},
                        ])
                    elif category_name == "Телевизоры":
                        base_characteristics.extend([
                            {"name": "Диагональ экрана", "value": random.choice(["43", "55", "65", "75", "85"]), "unit": "дюймов"},
                            {"name": "Разрешение экрана", "value": random.choice(["4K UHD", "8K UHD", "Full HD"])},
                            {"name": "Технология экрана", "value": random.choice(["OLED", "QLED", "LED", "Mini LED"])},
                            {"name": "HDR", "value": random.choice(["HDR10", "Dolby Vision", "HDR10+", "HLG"])},
                            {"name": "Частота обновления", "value": random.choice(["60", "120", "240"]), "unit": "Гц"},
                        ])
                    elif category_name == "Планшеты":
                        base_characteristics.extend([
                            {"name": "Диагональ экрана", "value": random.choice(["10.1", "10.9", "11", "12.9"]), "unit": "дюйма"},
                            {"name": "Разрешение экрана", "value": random.choice(["1920x1200", "2560x1600", "2732x2048"])},
                            {"name": "Процессор", "value": random.choice(["Apple M2", "Snapdragon 8 Gen 2", "MediaTek Dimensity 9000"])},
                            {"name": "Объем памяти", "value": random.choice(["64", "128", "256", "512"]), "unit": "ГБ"},
                            {"name": "Операционная система", "value": random.choice(["iPadOS", "Android", "Windows"])},
                        ])
                    
                    for char_data in base_characteristics:
                        cursor.execute("""
                            INSERT INTO products_simple_productcharacteristic 
                            (product_id, name, value, unit, order_field)
                            VALUES (?, ?, ?, ?, ?)
                        """, (product_id, char_data["name"], char_data["value"], char_data.get("unit", ""), 0))
                    
                    created += 1
                    
                    if created % 50 == 0:
                        logger.info(f"Создано {created} товаров...")
                
            except Exception as e:
                logger.error(f"Ошибка при создании дополнительного товара: {e}")
    
    return created

def check_results():
    """Проверяет результаты"""
    logger.info("Проверка результатов...")
    
    with connection.cursor() as cursor:
        # Подсчитываем товары
        cursor.execute("SELECT COUNT(*) FROM products_simple_product")
        total_products = cursor.fetchone()[0]
        
        # Подсчитываем категории
        cursor.execute("SELECT COUNT(*) FROM products_simple_category")
        total_categories = cursor.fetchone()[0]
        
        # Подсчитываем характеристики
        cursor.execute("SELECT COUNT(*) FROM products_simple_productcharacteristic")
        total_characteristics = cursor.fetchone()[0]
        
        # Подсчитываем продавцов
        cursor.execute("SELECT COUNT(*) FROM products_simple_seller")
        total_sellers = cursor.fetchone()[0]
        
        logger.info(f"\n=== ИТОГОВАЯ СТАТИСТИКА ===")
        logger.info(f"Товаров: {total_products}")
        logger.info(f"Категорий: {total_categories}")
        logger.info(f"Характеристик: {total_characteristics}")
        logger.info(f"Продавцов: {total_sellers}")
        
        if total_products >= 500:
            logger.info("✅ Цель достигнута: создано 500+ товаров")
        else:
            logger.warning(f"⚠️ Создано только {total_products} товаров из 500")
        
        return total_products, total_categories, total_characteristics

def main():
    logger.info("🎯 НАЧАЛО СОЗДАНИЯ 500 ТОВАРОВ")
    logger.info("=" * 60)
    
    try:
        # Создаем таблицы
        create_tables()
        
        # Создаем категории
        categories = create_categories()
        
        # Создаем продавца
        seller_id = create_seller()
        
        # Создаем товары
        created_products = create_products(categories, seller_id, 500)
        
        # Проверяем результаты
        total_products, total_categories, total_characteristics = check_results()
        
        logger.info("🎉 СОЗДАНИЕ ТОВАРОВ ЗАВЕРШЕНО!")
        logger.info("=" * 60)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ КРИТИЧЕСКАЯ ОШИБКА: {e}")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n✅ Все задачи выполнены успешно!")
        print("📊 Проверьте базу данных db_simple.sqlite3")
    else:
        print("\n❌ Процесс завершился с ошибками")
        print("📋 Проверьте логи для деталей")
    
    sys.exit(0 if success else 1)
