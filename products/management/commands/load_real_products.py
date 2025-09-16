from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from decimal import Decimal
import random
import requests
from PIL import Image
import io
import os
from django.conf import settings
from products.models import (
    Category, Shop, Tag, Product, ProductImage, ProductCharacteristic,
    Seller, Order, OrderItem, Review, Cart, CartItem, Commission
)

User = get_user_model()


class Command(BaseCommand):
    help = 'Загружает реальные товары с изображениями из Unsplash'

    def add_arguments(self, parser):
        parser.add_argument(
            '--products',
            type=int,
            default=50,
            help='Количество товаров для загрузки'
        )
        parser.add_argument(
            '--categories',
            type=int,
            default=5,
            help='Количество категорий'
        )

    def handle(self, *args, **options):
        self.stdout.write('Начинаем загрузку реальных товаров...')
        
        # Проверяем наличие API ключа Unsplash
        if not settings.UNSPLASH_ACCESS_KEY:
            self.stdout.write(
                self.style.WARNING('UNSPLASH_ACCESS_KEY не установлен. Используем заглушки.')
            )
            self.load_with_placeholders(options)
            return
        
        # Создаем базовые данные если их нет
        self.ensure_basic_data()
        
        # Загружаем реальные товары
        self.load_real_products(options['products'])

        self.stdout.write(
            self.style.SUCCESS('Реальные товары успешно загружены!')
        )

    def ensure_basic_data(self):
        """Создает базовые данные если их нет"""
        # Создаем категории
        if not Category.objects.exists():
            self.create_categories()
        
        # Создаем теги
        if not Tag.objects.exists():
            self.create_tags()
        
        # Создаем магазины
        if not Shop.objects.exists():
            self.create_shops()
        
        # Создаем продавцов
        self.create_sellers()

    def create_categories(self):
        """Создает категории товаров"""
        categories_data = [
            'Электроника',
            'Одежда и обувь',
            'Дом и сад',
            'Спорт и отдых',
            'Красота и здоровье',
        ]
        
        for i, name in enumerate(categories_data):
            category, created = Category.objects.get_or_create(
                name=name,
                defaults={'slug': f"category-{i+1}"}
            )
            if created:
                self.stdout.write(f'Создана категория: {category.name}')

    def create_tags(self):
        """Создает теги товаров"""
        tags_data = [
            'Новинка',
            'Хит продаж',
            'Скидка',
            'Премиум',
            'Экологичный',
        ]
        
        for name in tags_data:
            tag, created = Tag.objects.get_or_create(name=name)
            if created:
                self.stdout.write(f'Создан тег: {tag.name}')

    def create_shops(self):
        """Создает магазины"""
        shops_data = [
            {
                'name': 'ТехноМир',
                'address': 'ул. Ленина, 10',
                'city': 'Москва',
                'coords': (55.7558, 37.6173)
            },
            {
                'name': 'Модный дом',
                'address': 'пр. Невский, 25',
                'city': 'Санкт-Петербург',
                'coords': (59.9311, 30.3609)
            },
        ]
        
        for data in shops_data:
            shop, created = Shop.objects.get_or_create(
                name=data['name'],
                defaults={
                    'address': data['address'],
                    'city': data['city'],
                    'latitude': data['coords'][0],
                    'longitude': data['coords'][1]
                }
            )
            if created:
                self.stdout.write(f'Создан магазин: {shop.name}')

    def create_sellers(self):
        """Создает продавцов"""
        company_names = [
            'ООО "ТехноПро"', 'ИП Иванов', 'ООО "МодаСтиль"', 'ИП Петров',
            'ООО "СпортГир"', 'ИП Сидоров', 'ООО "ДомТовар"', 'ИП Козлов',
        ]
        
        for i, company_name in enumerate(company_names):
            # Создаем пользователя-продавца
            user = User.objects.create_user(
                username=f'seller_{i+1}',
                email=f'seller{i+1}@example.com',
                password='password123',
                role='seller',
                first_name=f'Продавец{i+1}',
                last_name='Тестовый'
            )
            
            # Создаем профиль продавца
            seller = Seller.objects.create(
                user=user,
                company_name=company_name,
                description=f'Описание компании продавца {i+1}',
                commission_rate=Decimal(random.uniform(3.0, 15.0)),
                is_verified=random.choice([True, False])
            )
            
            self.stdout.write(f'Создан продавец: {seller.company_name}')

    def load_real_products(self, count):
        """Загружает реальные товары с Unsplash"""
        categories = list(Category.objects.all())
        sellers = list(Seller.objects.all())
        tags = list(Tag.objects.all())
        shops = list(Shop.objects.all())
        
        # Реальные товары с поисковыми запросами для Unsplash
        real_products = [
            {
                'name': {'ru': 'iPhone 15 Pro', 'en': 'iPhone 15 Pro', 'ar': 'آيفون 15 برو'},
                'description': {'ru': 'Новейший смартфон Apple с титановым корпусом', 'en': 'Latest Apple smartphone with titanium body', 'ar': 'أحدث هاتف ذكي من Apple بهيكل من التيتانيوم'},
                'category_keywords': 'electronics smartphone',
                'price_range': (80000, 120000),
                'characteristics': [
                    ('Цвет', 'Титан'),
                    ('Память', '256 ГБ'),
                    ('Экран', '6.1" Super Retina XDR'),
                    ('Процессор', 'A17 Pro'),
                    ('Камера', '48 МП'),
                ]
            },
            {
                'name': {'ru': 'MacBook Air M3', 'en': 'MacBook Air M3', 'ar': 'ماك بوك إير M3'},
                'description': {'ru': 'Ультратонкий ноутбук с чипом M3', 'en': 'Ultra-thin laptop with M3 chip', 'ar': 'كمبيوتر محمول فائق النحافة بمعالج M3'},
                'category_keywords': 'electronics laptop computer',
                'price_range': (100000, 150000),
                'characteristics': [
                    ('Цвет', 'Серебристый'),
                    ('Память', '8 ГБ'),
                    ('Диск', '256 ГБ SSD'),
                    ('Экран', '13.6" Liquid Retina'),
                    ('Процессор', 'Apple M3'),
                ]
            },
            {
                'name': {'ru': 'Nike Air Max 270', 'en': 'Nike Air Max 270', 'ar': 'نايك إير ماكس 270'},
                'description': {'ru': 'Спортивные кроссовки с технологией Air Max', 'en': 'Sports sneakers with Air Max technology', 'ar': 'أحذية رياضية بتقنية إير ماكس'},
                'category_keywords': 'shoes sneakers sport',
                'price_range': (8000, 15000),
                'characteristics': [
                    ('Цвет', 'Черный/Белый'),
                    ('Размер', '42'),
                    ('Материал', 'Ткань/Кожа'),
                    ('Подошва', 'Резина'),
                    ('Бренд', 'Nike'),
                ]
            },
            {
                'name': {'ru': 'Samsung Galaxy S24', 'en': 'Samsung Galaxy S24', 'ar': 'سامسونج جالاكسي S24'},
                'description': {'ru': 'Флагманский смартфон Samsung с ИИ', 'en': 'Samsung flagship smartphone with AI', 'ar': 'هاتف سامسونج الرئيسي بالذكاء الاصطناعي'},
                'category_keywords': 'electronics smartphone samsung',
                'price_range': (70000, 100000),
                'characteristics': [
                    ('Цвет', 'Черный'),
                    ('Память', '128 ГБ'),
                    ('Экран', '6.2" Dynamic AMOLED'),
                    ('Процессор', 'Snapdragon 8 Gen 3'),
                    ('Камера', '50 МП'),
                ]
            },
            {
                'name': {'ru': 'Adidas Ultraboost 22', 'en': 'Adidas Ultraboost 22', 'ar': 'أديداس ألترابوست 22'},
                'description': {'ru': 'Беговые кроссовки с технологией Boost', 'en': 'Running sneakers with Boost technology', 'ar': 'أحذية جري بتقنية بوست'},
                'category_keywords': 'shoes running sport adidas',
                'price_range': (12000, 20000),
                'characteristics': [
                    ('Цвет', 'Белый/Черный'),
                    ('Размер', '43'),
                    ('Материал', 'Primeknit'),
                    ('Подошва', 'Boost'),
                    ('Бренд', 'Adidas'),
                ]
            },
            {
                'name': {'ru': 'Sony WH-1000XM5', 'en': 'Sony WH-1000XM5', 'ar': 'سوني WH-1000XM5'},
                'description': {'ru': 'Беспроводные наушники с шумоподавлением', 'en': 'Wireless headphones with noise cancellation', 'ar': 'سماعات لاسلكية بإلغاء الضوضاء'},
                'category_keywords': 'electronics headphones audio',
                'price_range': (25000, 35000),
                'characteristics': [
                    ('Цвет', 'Черный'),
                    ('Тип', 'Накладные'),
                    ('Подключение', 'Bluetooth 5.2'),
                    ('Батарея', '30 часов'),
                    ('Бренд', 'Sony'),
                ]
            },
            {
                'name': {'ru': 'Dyson V15 Detect', 'en': 'Dyson V15 Detect', 'ar': 'دايسون V15 ديتكت'},
                'description': {'ru': 'Беспроводной пылесос с лазерной технологией', 'en': 'Cordless vacuum with laser technology', 'ar': 'مكنسة كهربائية لاسلكية بتقنية الليزر'},
                'category_keywords': 'home vacuum cleaner',
                'price_range': (45000, 60000),
                'characteristics': [
                    ('Цвет', 'Желтый'),
                    ('Тип', 'Беспроводной'),
                    ('Батарея', '60 минут'),
                    ('Мощность', '230 AW'),
                    ('Бренд', 'Dyson'),
                ]
            },
            {
                'name': {'ru': 'Apple Watch Series 9', 'en': 'Apple Watch Series 9', 'ar': 'ساعة أبل سيريس 9'},
                'description': {'ru': 'Умные часы с функциями здоровья', 'en': 'Smartwatch with health features', 'ar': 'ساعة ذكية بميزات صحية'},
                'category_keywords': 'electronics smartwatch apple',
                'price_range': (30000, 45000),
                'characteristics': [
                    ('Цвет', 'Розовое золото'),
                    ('Размер', '45мм'),
                    ('Экран', 'Always-On Retina'),
                    ('Батарея', '18 часов'),
                    ('Бренд', 'Apple'),
                ]
            },
            {
                'name': {'ru': 'Levi\'s 501 Original', 'en': 'Levi\'s 501 Original', 'ar': 'ليفايز 501 أوريجينال'},
                'description': {'ru': 'Классические джинсы прямого кроя', 'en': 'Classic straight-fit jeans', 'ar': 'جينز كلاسيكي بقصة مستقيمة'},
                'category_keywords': 'clothing jeans denim',
                'price_range': (5000, 8000),
                'characteristics': [
                    ('Цвет', 'Синий'),
                    ('Размер', '32/32'),
                    ('Материал', '100% Хлопок'),
                    ('Крой', 'Прямой'),
                    ('Бренд', 'Levi\'s'),
                ]
            },
            {
                'name': {'ru': 'Canon EOS R6 Mark II', 'en': 'Canon EOS R6 Mark II', 'ar': 'كانون EOS R6 مارك 2'},
                'description': {'ru': 'Зеркальная камера для профессионалов', 'en': 'Professional mirrorless camera', 'ar': 'كاميرا احترافية بدون مرآة'},
                'category_keywords': 'electronics camera photography',
                'price_range': (200000, 250000),
                'characteristics': [
                    ('Цвет', 'Черный'),
                    ('Матрица', '24.2 МП'),
                    ('Стабилизация', '5-осевая'),
                    ('Видео', '4K 60p'),
                    ('Бренд', 'Canon'),
                ]
            },
        ]
        
        for i in range(min(count, len(real_products))):
            product_data = real_products[i % len(real_products)]
            
            # Выбираем случайные данные
            category = random.choice(categories)
            seller = random.choice(sellers)
            
            self.stdout.write(f'Создаем товар {i+1}: {product_data["name"]["ru"]}')
            
            # Создаем товар
            product = Product()
            product.name = product_data['name']['ru']  # Используем русское название
            product.description = product_data['description']['ru']  # Используем русское описание
            
            # Устанавливаем цену
            price_min, price_max = product_data['price_range']
            product.price = Decimal(random.uniform(price_min, price_max))
            if random.choice([True, False]):
                product.discount_price = product.price * Decimal(random.uniform(0.8, 0.95))
            
            product.category = category
            product.seller = seller
            product.stock_quantity = random.randint(5, 100)
            product.is_active = True
            
            try:
                product.save()
                self.stdout.write(f'  Товар сохранен: {product.name}')
            except Exception as e:
                self.stdout.write(f'  Ошибка сохранения товара: {e}')
                continue
            
            # Магазины не связаны с товарами в текущей модели
            
            # Добавляем теги
            product.tags.set(random.sample(tags, random.randint(1, 3)))
            
            # Создаем характеристики
            for j, (name, value) in enumerate(product_data['characteristics']):
                ProductCharacteristic.objects.create(
                    product=product,
                    name=name,
                    value=value,
                    order=j
                )
            
            # Создаем заглушки изображений
            self.create_placeholder_image(product)
            
            self.stdout.write(f'Создан товар: {product.name}')

    def load_product_images(self, product, keywords):
        """Загружает изображения товара с Unsplash"""
        try:
            # Получаем изображения с Unsplash
            headers = {
                'Authorization': f'Client-ID {settings.UNSPLASH_ACCESS_KEY}'
            }
            
            # Ищем изображения по ключевым словам
            search_url = 'https://api.unsplash.com/search/photos'
            params = {
                'query': keywords,
                'per_page': 3,
                'orientation': 'landscape'
            }
            
            response = requests.get(search_url, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                photos = data.get('results', [])
                
                for i, photo in enumerate(photos[:3]):  # Максимум 3 изображения
                    try:
                        # Скачиваем изображение
                        image_url = photo['urls']['regular']
                        img_response = requests.get(image_url)
                        
                        if img_response.status_code == 200:
                            # Создаем объект изображения
                            image = Image.open(io.BytesIO(img_response.content))
                            
                            # Изменяем размер если нужно
                            if image.width > 800:
                                image.thumbnail((800, 600), Image.Resampling.LANCZOS)
                            
                            # Сохраняем изображение
                            img_io = io.BytesIO()
                            image.save(img_io, format='JPEG', quality=85)
                            img_io.seek(0)
                            
                            # Создаем ProductImage
                            product_image = ProductImage.objects.create(
                                product=product,
                                alt_text=f"Изображение {product.name} {i+1}",
                                order=i
                            )
                            
                            # Сохраняем файл
                            filename = f"product_{product.id}_image_{i+1}.jpg"
                            product_image.image.save(filename, img_io, save=True)
                            
                            self.stdout.write(f'  Загружено изображение: {filename}')
                            
                    except Exception as e:
                        self.stdout.write(f'  Ошибка загрузки изображения {i+1}: {e}')
                        continue
                        
            else:
                self.stdout.write(f'  Ошибка API Unsplash: {response.status_code}')
                # Создаем заглушку
                self.create_placeholder_image(product)
                
        except Exception as e:
            self.stdout.write(f'  Ошибка загрузки изображений: {e}')
            # Создаем заглушку
            self.create_placeholder_image(product)

    def create_placeholder_image(self, product):
        """Создает заглушку изображения"""
        try:
            # Создаем простое изображение-заглушку
            img = Image.new('RGB', (400, 300), color='lightgray')
            
            # Добавляем текст
            from PIL import ImageDraw, ImageFont
            draw = ImageDraw.Draw(img)
            
            # Пытаемся использовать системный шрифт
            try:
                font = ImageFont.truetype("arial.ttf", 20)
            except:
                font = ImageFont.load_default()
            
            text = f"Изображение\n{product.name}"
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            x = (400 - text_width) // 2
            y = (300 - text_height) // 2
            
            draw.text((x, y), text, fill='black', font=font)
            
            # Сохраняем изображение
            img_io = io.BytesIO()
            img.save(img_io, format='JPEG')
            img_io.seek(0)
            
            # Создаем ProductImage
            product_image = ProductImage.objects.create(
                product=product,
                alt_text=f"Заглушка {product.name}",
                order=0
            )
            
            filename = f"product_{product.id}_placeholder.jpg"
            product_image.image.save(filename, img_io, save=True)
            
            self.stdout.write(f'  Создана заглушка: {filename}')
            
        except Exception as e:
            self.stdout.write(f'  Ошибка создания заглушки: {e}')

    def load_with_placeholders(self, options):
        """Загружает товары с заглушками если нет API ключа"""
        self.stdout.write('Загружаем товары с заглушками...')
        
        with transaction.atomic():
            self.ensure_basic_data()
            self.load_real_products(options['products'])
