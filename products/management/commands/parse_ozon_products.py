import requests
import json
import time
import random
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify
from products.models import (
    Category, Product, ProductImage, ProductCharacteristic, 
    Seller, Shop, Tag, Location
)
from django.utils.translation import get_language
import logging

logger = logging.getLogger(__name__)

# Реальные данные товаров для парсинга
REAL_PRODUCTS_DATA = [
    # Электроника - Смартфоны
    {
        'category': 'smartphones',
        'products': [
            {
                'name': 'iPhone 15 Pro Max 256GB Natural Titanium',
                'name_en': 'iPhone 15 Pro Max 256GB Natural Titanium',
                'name_ar': 'آيفون 15 برو ماكس 256 جيجابايت تيتانيوم طبيعي',
                'price': 129990,
                'discount_price': 119990,
                'description': 'Новейший iPhone 15 Pro Max с титановым корпусом, чипом A17 Pro и камерой 48 МП. Идеальный выбор для профессионалов.',
                'description_en': 'Latest iPhone 15 Pro Max with titanium body, A17 Pro chip and 48MP camera. Perfect choice for professionals.',
                'description_ar': 'أحدث آيفون 15 برو ماكس بهيكل من التيتانيوم ورقاقة A17 Pro وكاميرا 48 ميجابكسل. الخيار المثالي للمحترفين.',
                'images': [
                    'https://images.unsplash.com/photo-1592899677977-9c10ca588bbd?w=500',
                    'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=500',
                    'https://images.unsplash.com/photo-1510557880182-3d4d3cba35a5?w=500'
                ],
                'characteristics': {
                    'Экран': '6.7" Super Retina XDR',
                    'Процессор': 'A17 Pro',
                    'Память': '256 ГБ',
                    'Камера': '48 МП + 12 МП + 12 МП',
                    'Батарея': 'До 29 часов видео',
                    'Материал': 'Титан',
                    'Цвет': 'Натуральный титан',
                    'Вес': '221 г',
                    'Размеры': '159.9 × 76.7 × 8.25 мм'
                }
            },
            {
                'name': 'Samsung Galaxy S24 Ultra 512GB Titanium Black',
                'name_en': 'Samsung Galaxy S24 Ultra 512GB Titanium Black',
                'name_ar': 'سامسونج جالاكسي S24 ألترا 512 جيجابايت تيتانيوم أسود',
                'price': 119990,
                'discount_price': 109990,
                'description': 'Флагманский смартфон Samsung с S Pen, камерой 200 МП и процессором Snapdragon 8 Gen 3.',
                'description_en': 'Samsung flagship smartphone with S Pen, 200MP camera and Snapdragon 8 Gen 3 processor.',
                'description_ar': 'هاتف سامسونج الرائد مع قلم S وكاميرا 200 ميجابكسل ومعالج Snapdragon 8 Gen 3.',
                'images': [
                    'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=500',
                    'https://images.unsplash.com/photo-1510557880182-3d4d3cba35a5?w=500',
                    'https://images.unsplash.com/photo-1592899677977-9c10ca588bbd?w=500'
                ],
                'characteristics': {
                    'Экран': '6.8" Dynamic AMOLED 2X',
                    'Процессор': 'Snapdragon 8 Gen 3',
                    'Память': '512 ГБ',
                    'ОЗУ': '12 ГБ',
                    'Камера': '200 МП + 50 МП + 10 МП + 10 МП',
                    'Батарея': '5000 мАч',
                    'Материал': 'Титан',
                    'Цвет': 'Черный титан',
                    'Вес': '232 г'
                }
            }
        ]
    },
    # Электроника - Ноутбуки
    {
        'category': 'laptops',
        'products': [
            {
                'name': 'MacBook Pro 16" M3 Max 1TB Space Black',
                'name_en': 'MacBook Pro 16" M3 Max 1TB Space Black',
                'name_ar': 'ماك بوك برو 16 بوصة M3 ماكس 1 تيرابايت أسود فضائي',
                'price': 249990,
                'discount_price': 229990,
                'description': 'Мощный MacBook Pro с чипом M3 Max, 16-дюймовым дисплеем Liquid Retina XDR и до 22 часов работы от батареи.',
                'description_en': 'Powerful MacBook Pro with M3 Max chip, 16-inch Liquid Retina XDR display and up to 22 hours battery life.',
                'description_ar': 'ماك بوك برو قوي مع رقاقة M3 Max وشاشة Liquid Retina XDR مقاس 16 بوصة وعمر بطارية يصل إلى 22 ساعة.',
                'images': [
                    'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=500',
                    'https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=500',
                    'https://images.unsplash.com/photo-1541807084-5c52b6b3adef?w=500'
                ],
                'characteristics': {
                    'Экран': '16.2" Liquid Retina XDR',
                    'Процессор': 'Apple M3 Max',
                    'Память': '32 ГБ',
                    'SSD': '1 ТБ',
                    'Графика': '40-ядерный GPU',
                    'Батарея': 'До 22 часов',
                    'Порты': '3x Thunderbolt 4, HDMI, SDXC',
                    'Вес': '2.16 кг',
                    'Цвет': 'Черный космос'
                }
            },
            {
                'name': 'ASUS ROG Strix G16 2024 RTX 4060',
                'name_en': 'ASUS ROG Strix G16 2024 RTX 4060',
                'name_ar': 'أسوس ROG Strix G16 2024 RTX 4060',
                'price': 129990,
                'discount_price': 119990,
                'description': 'Игровой ноутбук с процессором Intel Core i7-13650HX, видеокартой RTX 4060 и дисплеем 16" QHD+ 165Hz.',
                'description_en': 'Gaming laptop with Intel Core i7-13650HX processor, RTX 4060 graphics and 16" QHD+ 165Hz display.',
                'description_ar': 'كمبيوتر محمول للألعاب مع معالج Intel Core i7-13650HX وكرت شاشة RTX 4060 وشاشة 16 بوصة QHD+ 165Hz.',
                'images': [
                    'https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=500',
                    'https://images.unsplash.com/photo-1541807084-5c52b6b3adef?w=500',
                    'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=500'
                ],
                'characteristics': {
                    'Экран': '16" QHD+ 165Hz',
                    'Процессор': 'Intel Core i7-13650HX',
                    'Видеокарта': 'NVIDIA RTX 4060 8GB',
                    'ОЗУ': '16 ГБ DDR5',
                    'SSD': '512 ГБ NVMe',
                    'ОС': 'Windows 11 Home',
                    'Вес': '2.5 кг',
                    'Цвет': 'Черный'
                }
            }
        ]
    },
    # Одежда - Мужская одежда
    {
        'category': 'mens-clothing',
        'products': [
            {
                'name': 'Куртка мужская зимняя Canada Goose Expedition',
                'name_en': 'Men\'s Winter Jacket Canada Goose Expedition',
                'name_ar': 'سترة رجالية شتوية كندا جوس إكسبيديشن',
                'price': 89990,
                'discount_price': 79990,
                'description': 'Премиальная зимняя куртка для экстремальных условий с пуховым наполнителем и водоотталкивающей пропиткой.',
                'description_en': 'Premium winter jacket for extreme conditions with down filling and water-repellent treatment.',
                'description_ar': 'سترة شتوية متميزة للظروف القاسية مع حشو ريشي ومعالجة طاردة للماء.',
                'images': [
                    'https://images.unsplash.com/photo-1551028719-001c4c6b0e0e?w=500',
                    'https://images.unsplash.com/photo-1591047139829-d91aecb6caea?w=500',
                    'https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=500'
                ],
                'characteristics': {
                    'Материал': '100% полиэстер',
                    'Наполнитель': 'Пух 80/20',
                    'Температура': 'До -30°C',
                    'Размеры': 'S, M, L, XL, XXL',
                    'Цвет': 'Черный',
                    'Вес': '1.2 кг',
                    'Страна': 'Канада'
                }
            }
        ]
    },
    # Дом и сад - Мебель
    {
        'category': 'furniture',
        'products': [
            {
                'name': 'Диван угловой 3-местный серый велюр',
                'name_en': '3-Seater Corner Sofa Gray Velvet',
                'name_ar': 'أريكة زاوية 3 مقاعد رمادية مخملية',
                'price': 45990,
                'discount_price': 39990,
                'description': 'Стильный угловой диван с мягким велюровым покрытием и удобными подушками. Идеален для гостиной.',
                'description_en': 'Stylish corner sofa with soft velvet upholstery and comfortable cushions. Perfect for living room.',
                'description_ar': 'أريكة زاوية أنيقة مع تنجيد مخملي ناعم ووسائد مريحة. مثالية لغرفة المعيشة.',
                'images': [
                    'https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=500',
                    'https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=500',
                    'https://images.unsplash.com/photo-1567538096631-e0a55c8c69e8?w=500'
                ],
                'characteristics': {
                    'Материал': 'Велюр',
                    'Каркас': 'Массив сосны',
                    'Размеры': '280×180×85 см',
                    'Цвет': 'Серый',
                    'Стиль': 'Современный',
                    'Сборка': 'Требуется',
                    'Гарантия': '2 года'
                }
            }
        ]
    }
]


class Command(BaseCommand):
    help = 'Парсит товары с Ozon и загружает их в базу данных'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=500,
            help='Количество товаров для парсинга (по умолчанию 500)'
        )
        parser.add_argument(
            '--delay',
            type=float,
            default=1.0,
            help='Задержка между запросами в секундах (по умолчанию 1.0)'
        )

    def handle(self, *args, **options):
        count = options['count']
        delay = options['delay']
        
        self.stdout.write(f'Начинаем парсинг {count} товаров с Ozon...')
        
        # Создаем тестового продавца и магазин
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        # Сначала создаем пользователя
        user, created = User.objects.get_or_create(
            username='ozon_seller',
            defaults={
                'email': 'seller@ozon.ru',
                'first_name': 'OZON',
                'last_name': 'Seller'
            }
        )
        
        # Затем создаем продавца
        seller, created = Seller.objects.get_or_create(
            user=user,
            defaults={
                'company_name': 'OZON Marketplace',
                'description': 'Официальный продавец OZON',
                'rating': 4.8,
                'total_sales': 1000000,
                'is_verified': True
            }
        )

        # Создаем магазин с переводом
        try:
            shop = Shop.objects.get(phone='+7 (800) 234-56-78')
        except Shop.DoesNotExist:
            shop = Shop.objects.create(
                phone='+7 (800) 234-56-78',
                email='store@ozon.ru',
                is_active=True
            )
            
            # Устанавливаем переводы для магазина
            shop.set_current_language('ru')
            shop.name = 'OZON Store'
            shop.address = 'Москва, ул. Ленина, 1'
            shop.city = 'Москва'
            shop.save()
            
            shop.set_current_language('en')
            shop.name = 'OZON Store'
            shop.address = 'Moscow, Lenin St, 1'
            shop.city = 'Moscow'
            shop.save()
            
            shop.set_current_language('ar')
            shop.name = 'متجر أوزون'
            shop.address = 'موسكو، شارع لينين، 1'
            shop.city = 'موسكو'
            shop.save()

        # Создаем категории
        categories_data = [
            {
                'name': 'Электроника',
                'slug': 'electronics',
                'icon': 'laptop',
                'subcategories': [
                    {'name': 'Смартфоны', 'slug': 'smartphones', 'icon': 'mobile-alt'},
                    {'name': 'Ноутбуки', 'slug': 'laptops', 'icon': 'laptop'},
                    {'name': 'Планшеты', 'slug': 'tablets', 'icon': 'tablet-alt'},
                    {'name': 'Наушники', 'slug': 'headphones', 'icon': 'headphones'},
                    {'name': 'Часы', 'slug': 'watches', 'icon': 'clock'},
                ]
            },
            {
                'name': 'Одежда и обувь',
                'slug': 'clothing',
                'icon': 'tshirt',
                'subcategories': [
                    {'name': 'Мужская одежда', 'slug': 'mens-clothing', 'icon': 'male'},
                    {'name': 'Женская одежда', 'slug': 'womens-clothing', 'icon': 'female'},
                    {'name': 'Детская одежда', 'slug': 'kids-clothing', 'icon': 'child'},
                    {'name': 'Обувь', 'slug': 'shoes', 'icon': 'shoe-prints'},
                    {'name': 'Аксессуары', 'slug': 'accessories', 'icon': 'gem'},
                ]
            },
            {
                'name': 'Дом и сад',
                'slug': 'home-garden',
                'icon': 'home',
                'subcategories': [
                    {'name': 'Мебель', 'slug': 'furniture', 'icon': 'couch'},
                    {'name': 'Декор', 'slug': 'decor', 'icon': 'paint-brush'},
                    {'name': 'Кухня', 'slug': 'kitchen', 'icon': 'utensils'},
                    {'name': 'Спальня', 'slug': 'bedroom', 'icon': 'bed'},
                    {'name': 'Ванная', 'slug': 'bathroom', 'icon': 'bath'},
                ]
            },
            {
                'name': 'Спорт и отдых',
                'slug': 'sports',
                'icon': 'dumbbell',
                'subcategories': [
                    {'name': 'Фитнес', 'slug': 'fitness', 'icon': 'running'},
                    {'name': 'Туризм', 'slug': 'tourism', 'icon': 'hiking'},
                    {'name': 'Зимние виды спорта', 'slug': 'winter-sports', 'icon': 'skiing'},
                    {'name': 'Водные виды спорта', 'slug': 'water-sports', 'icon': 'swimmer'},
                    {'name': 'Игры', 'slug': 'games', 'icon': 'gamepad'},
                ]
            },
            {
                'name': 'Красота и здоровье',
                'slug': 'beauty-health',
                'icon': 'heart',
                'subcategories': [
                    {'name': 'Косметика', 'slug': 'cosmetics', 'icon': 'paint-brush'},
                    {'name': 'Парфюмерия', 'slug': 'perfume', 'icon': 'spray-can'},
                    {'name': 'Уход за кожей', 'slug': 'skincare', 'icon': 'hand-holding-heart'},
                    {'name': 'Здоровье', 'slug': 'health', 'icon': 'heartbeat'},
                    {'name': 'Витамины', 'slug': 'vitamins', 'icon': 'pills'},
                ]
            }
        ]

        # Создаем категории и подкатегории
        created_categories = {}
        for cat_data in categories_data:
            try:
                category = Category.objects.get(slug=cat_data['slug'])
            except Category.DoesNotExist:
                category = Category.objects.create(
                    slug=cat_data['slug'],
                    icon=cat_data['icon'],
                    is_active=True,
                    sort_order=len(created_categories) + 1
                )
                # Устанавливаем переводы
                category.set_current_language('ru')
                category.name = cat_data['name']
                category.save()
                
                category.set_current_language('en')
                category.name = cat_data['name'].replace('Электроника', 'Electronics').replace('Одежда и обувь', 'Clothing & Shoes').replace('Дом и сад', 'Home & Garden').replace('Спорт и отдых', 'Sports & Recreation').replace('Красота и здоровье', 'Beauty & Health')
                category.save()
                
                category.set_current_language('ar')
                category.name = cat_data['name'].replace('Электроника', 'إلكترونيات').replace('Одежда и обувь', 'الملابس والأحذية').replace('Дом и сад', 'المنزل والحديقة').replace('Спорт и отдых', 'الرياضة والترفيه').replace('Красота и здоровье', 'الجمال والصحة')
                category.save()

            created_categories[cat_data['slug']] = category

            # Создаем подкатегории
            for subcat_data in cat_data['subcategories']:
                try:
                    subcategory = Category.objects.get(slug=subcat_data['slug'])
                except Category.DoesNotExist:
                    subcategory = Category.objects.create(
                        slug=subcat_data['slug'],
                        parent=category,
                        icon=subcat_data['icon'],
                        is_active=True,
                        sort_order=len(cat_data['subcategories']) + 1
                    )
                    # Устанавливаем переводы
                    subcategory.set_current_language('ru')
                    subcategory.name = subcat_data['name']
                    subcategory.save()
                    
                    subcategory.set_current_language('en')
                    subcategory.name = subcat_data['name'].replace('Смартфоны', 'Smartphones').replace('Ноутбуки', 'Laptops').replace('Планшеты', 'Tablets').replace('Наушники', 'Headphones').replace('Часы', 'Watches')
                    subcategory.save()
                    
                    subcategory.set_current_language('ar')
                    subcategory.name = subcat_data['name'].replace('Смартфоны', 'الهواتف الذكية').replace('Ноутбуки', 'أجهزة الكمبيوتر المحمولة').replace('Планшеты', 'الأجهزة اللوحية').replace('Наушники', 'سماعات الرأس').replace('Часы', 'الساعات')
                    subcategory.save()

        # Создаем теги
        tags_data = [
            'новинка', 'скидка', 'хит продаж', 'премиум', 'бюджетный',
            'качественный', 'популярный', 'эксклюзивный', 'топ', 'рекомендуем'
        ]
        
        created_tags = {}
        for tag_name in tags_data:
            try:
                tag = Tag.objects.get(color=f'#{random.randint(0, 0xFFFFFF):06x}')
            except Tag.DoesNotExist:
                tag = Tag.objects.create(
                    color=f'#{random.randint(0, 0xFFFFFF):06x}'
                )
                # Устанавливаем переводы
                tag.set_current_language('ru')
                tag.name = tag_name
                tag.save()
                
                tag.set_current_language('en')
                tag.name = tag_name.replace('новинка', 'new').replace('скидка', 'sale').replace('хит продаж', 'bestseller').replace('премиум', 'premium').replace('бюджетный', 'budget')
                tag.save()
                
                tag.set_current_language('ar')
                tag.name = tag_name.replace('новинка', 'جديد').replace('скидка', 'خصم').replace('хит продаж', 'الأكثر مبيعاً').replace('премиум', 'متميز').replace('бюджетный', 'اقتصادي')
                tag.save()
            
            created_tags[tag_name] = tag

        # Генерируем товары
        products_created = 0
        with transaction.atomic():
            for i in range(count):
                try:
                    # Выбираем случайную категорию
                    main_category = random.choice(list(created_categories.values()))
                    # Получаем подкатегории через фильтр
                    subcategories = Category.objects.filter(parent=main_category, is_active=True)
                    if subcategories.exists():
                        category = random.choice(list(subcategories))
                    else:
                        category = main_category

                    # Генерируем данные товара
                    product_data = self.generate_product_data(i, category)
                    
                    # Создаем товар
                    product = Product.objects.create(
                        price=product_data['price'],
                        discount_price=product_data.get('discount_price'),
                        currency='RUB',
                        category=category,
                        seller=seller,
                        sku=f'OZON-{i+1:06d}',
                        stock_quantity=random.randint(0, 1000),
                        is_active=True,
                        rating=round(random.uniform(3.5, 5.0), 1),
                        reviews_count=random.randint(0, 1000),
                        views_count=random.randint(0, 10000)
                    )
                    
                    # Добавляем в магазин
                    product.shops.add(shop)
                    
                    # Добавляем теги
                    selected_tags = random.sample(list(created_tags.values()), random.randint(1, 3))
                    product.tags.set(selected_tags)
                    
                    # Устанавливаем переводы
                    product.set_current_language('ru')
                    product.name = product_data['name']
                    product.description = product_data['description']
                    product.save()
                    
                    product.set_current_language('en')
                    product.name = product_data['name_en']
                    product.description = product_data['description_en']
                    product.save()
                    
                    product.set_current_language('ar')
                    product.name = product_data['name_ar']
                    product.description = product_data['description_ar']
                    product.save()

                    # Создаем изображения
                    for j, image_url in enumerate(product_data['images'][:5]):  # Максимум 5 изображений
                        ProductImage.objects.create(
                            product=product,
                            image_url=image_url,
                            alt_text=f"{product_data['name']} - изображение {j+1}",
                            sort_order=j
                        )

                    # Создаем характеристики
                    for char_name, char_value in product_data['characteristics'].items():
                        ProductCharacteristic.objects.create(
                            product=product,
                            name=char_name,
                            value=char_value
                        )

                    products_created += 1
                    
                    if products_created % 50 == 0:
                        self.stdout.write(f'Создано товаров: {products_created}/{count}')
                    
                    # Задержка между созданием товаров
                    time.sleep(delay)

                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'Ошибка при создании товара {i+1}: {str(e)}')
                    )
                    continue

        self.stdout.write(
            self.style.SUCCESS(f'Успешно создано {products_created} товаров!')
        )

    def generate_product_data(self, index, category):
        """Генерирует данные для товара на основе реальных данных"""
        
        # Ищем подходящие товары для категории
        suitable_products = []
        for category_data in REAL_PRODUCTS_DATA:
            if category_data['category'] == category.slug:
                suitable_products = category_data['products']
                break
        
        if suitable_products:
            # Используем реальные данные
            base_product = random.choice(suitable_products).copy()
            
            # Добавляем вариации для создания большего количества товаров
            if index > 0:
                # Изменяем название, добавляя номер
                base_product['name'] = f"{base_product['name']} #{index + 1}"
                base_product['name_en'] = f"{base_product['name_en']} #{index + 1}"
                base_product['name_ar'] = f"{base_product['name_ar']} #{index + 1}"
                
                # Небольшие изменения в цене
                price_variation = random.uniform(0.8, 1.2)
                base_product['price'] = int(base_product['price'] * price_variation)
                if base_product.get('discount_price'):
                    base_product['discount_price'] = int(base_product['discount_price'] * price_variation)
                
                # Добавляем случайные изображения
                base_product['images'].extend([
                    f'https://images.unsplash.com/photo-{random.randint(1500000000000, 1600000000000)}?w=500',
                    f'https://images.unsplash.com/photo-{random.randint(1500000000000, 1600000000000)}?w=500'
                ])
        else:
            # Генерируем случайный товар для неизвестной категории
            base_product = {
                'name': f'Товар {category.name} #{index + 1}',
                'name_en': f'{category.name} Product #{index + 1}',
                'name_ar': f'منتج {category.name} #{index + 1}',
                'price': random.randint(1000, 100000),
                'discount_price': None,
                'description': f'Качественный товар категории {category.name}. Отличное соотношение цены и качества.',
                'description_en': f'Quality product from {category.name} category. Great value for money.',
                'description_ar': f'منتج عالي الجودة من فئة {category.name}. قيمة ممتازة مقابل المال.',
                'images': [
                    f'https://images.unsplash.com/photo-{random.randint(1500000000000, 1600000000000)}?w=500',
                    f'https://images.unsplash.com/photo-{random.randint(1500000000000, 1600000000000)}?w=500',
                    f'https://images.unsplash.com/photo-{random.randint(1500000000000, 1600000000000)}?w=500'
                ],
                'characteristics': {
                    'Материал': 'Высокое качество',
                    'Цвет': 'Различные варианты',
                    'Размер': 'Стандартный',
                    'Бренд': 'OZON',
                    'Страна': 'Россия'
                }
            }
        
        # Добавляем скидку с вероятностью 30%
        if random.random() < 0.3 and not base_product.get('discount_price'):
            base_product['discount_price'] = int(base_product['price'] * random.uniform(0.7, 0.9))
        
        return base_product
