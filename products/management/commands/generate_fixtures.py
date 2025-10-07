"""
Команда для генерации тестовых данных
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from products.models import Category, Shop, Tag, Product, ProductImage, Seller
from faker import Faker
import random
import requests
from io import BytesIO
from django.core.files import File
from django.conf import settings

User = get_user_model()
fake = Faker('ru_RU')


class Command(BaseCommand):
    help = 'Генерирует тестовые данные для ShopList'

    def add_arguments(self, parser):
        parser.add_argument('--categories', type=int, default=5, help='Количество категорий')
        parser.add_argument('--shops', type=int, default=10, help='Количество магазинов')
        parser.add_argument('--tags', type=int, default=15, help='Количество тегов')
        parser.add_argument('--products', type=int, default=50, help='Количество товаров')
        parser.add_argument('--users', type=int, default=20, help='Количество пользователей')

    def handle(self, *args, **options):
        self.stdout.write('Начинаем генерацию тестовых данных...')
        
        # Создаем пользователей
        self.create_users(options['users'])
        
        # Создаем категории
        categories = self.create_categories(options['categories'])
        
        # Создаем магазины
        shops = self.create_shops(options['shops'])
        
        # Создаем теги
        tags = self.create_tags(options['tags'])
        
        # Создаем продавцов
        sellers = self.create_sellers()
        
        # Создаем товары
        self.create_products(options['products'], categories, shops, tags, sellers)
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Успешно создано:\n'
                f'- Пользователей: {options["users"]}\n'
                f'- Категорий: {options["categories"]}\n'
                f'- Магазинов: {options["shops"]}\n'
                f'- Тегов: {options["tags"]}\n'
                f'- Товаров: {options["products"]}'
            )
        )

    def create_users(self, count):
        """Создает тестовых пользователей"""
        self.stdout.write('Создаем пользователей...')
        
        # Создаем админа если его нет
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@shoplist.com',
                password='admin123',
                role='admin'
            )
            self.stdout.write('Создан администратор: admin/admin123')
        
        for i in range(count):
            username = fake.user_name() + str(i)
            email = fake.email()
            
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password='password123',
                    first_name=fake.first_name(),
                    last_name=fake.last_name(),
                    role=random.choice(['user', 'manager', 'seller'])
                )

    def create_categories(self, count):
        """Создает категории товаров"""
        self.stdout.write('Создаем категории...')
        
        category_names = [
            'Электроника', 'Одежда', 'Дом и сад', 'Спорт и отдых', 'Красота и здоровье',
            'Автотовары', 'Детские товары', 'Книги', 'Продукты питания', 'Мебель'
        ]
        
        categories = []
        for i in range(min(count, len(category_names))):
            name = category_names[i]
            slug = name.lower().replace(' ', '-').replace('ё', 'е')
            
            category, created = Category.objects.get_or_create(
                slug=slug,
                defaults={
                    'name': name,
                    'description': fake.text(max_nb_chars=200),
                    'is_active': True,
                    'sort_order': i
                }
            )
            categories.append(category)
            
        return categories

    def create_shops(self, count):
        """Создает магазины"""
        self.stdout.write('Создаем магазины...')
        
        cities = ['Москва', 'Санкт-Петербург', 'Новосибирск', 'Екатеринбург', 'Казань']
        shops = []
        
        for i in range(count):
            city = random.choice(cities)
            name = f"{fake.company()} ({city})"
            
            shop, created = Shop.objects.get_or_create(
                name=name,
                defaults={
                    'address': fake.address(),
                    'city': city,
                    'phone': fake.phone_number(),
                    'email': fake.email(),
                    'latitude': fake.latitude(),
                    'longitude': fake.longitude(),
                    'is_active': True
                }
            )
            shops.append(shop)
            
        return shops

    def create_tags(self, count):
        """Создает теги"""
        self.stdout.write('Создаем теги...')
        
        tag_names = [
            'Новинка', 'Хит продаж', 'Скидка', 'Премиум', 'Эко', 'Быстрая доставка',
            'Гарантия', 'Популярное', 'Рекомендуем', 'Лимитированная серия',
            'Бестселлер', 'Акция', 'Выгодно', 'Качество', 'Надежность'
        ]
        
        colors = ['#ff6b35', '#005bff', '#28a745', '#ffc107', '#dc3545', '#6f42c1']
        tags = []
        
        for i in range(min(count, len(tag_names))):
            name = tag_names[i]
            
            tag, created = Tag.objects.get_or_create(
                name=name,
                defaults={
                    'color': random.choice(colors)
                }
            )
            tags.append(tag)
            
        return tags

    def create_sellers(self):
        """Создает продавцов"""
        self.stdout.write('Создаем продавцов...')
        
        seller_users = User.objects.filter(role='seller')
        sellers = []
        
        for user in seller_users:
            seller, created = Seller.objects.get_or_create(
                user=user,
                defaults={
                    'company_name': fake.company(),
                    'description': fake.text(max_nb_chars=300),
                    'commission_rate': random.uniform(3.0, 10.0),
                    'is_verified': random.choice([True, False]),
                    'rating': random.uniform(3.5, 5.0)
                }
            )
            sellers.append(seller)
            
        return sellers

    def create_products(self, count, categories, shops, tags, sellers):
        """Создает товары"""
        self.stdout.write('Создаем товары...')
        
        product_names = [
            'Смартфон', 'Ноутбук', 'Наушники', 'Планшет', 'Умные часы',
            'Футболка', 'Джинсы', 'Кроссовки', 'Куртка', 'Рюкзак',
            'Кофеварка', 'Пылесос', 'Микроволновка', 'Утюг', 'Фен',
            'Книга', 'Игрушка', 'Мяч', 'Велосипед', 'Палатка'
        ]
        
        for i in range(count):
            base_name = random.choice(product_names)
            brand = fake.company()
            name = f"{brand} {base_name} {fake.word().title()}"
            
            price = random.uniform(500, 50000)
            discount_price = None
            if random.choice([True, False]):
                discount_price = price * random.uniform(0.7, 0.95)
            
            product = Product.objects.create(
                name=name,
                description=fake.text(max_nb_chars=500),
                price=price,
                discount_price=discount_price,
                category=random.choice(categories),
                seller=random.choice(sellers) if sellers else None,
                sku=f"PRD-{fake.random_number(digits=8)}",
                brand=brand,
                stock_quantity=random.randint(0, 100),
                is_active=True,
                rating=random.uniform(3.0, 5.0),
                reviews_count=random.randint(0, 500),
                views_count=random.randint(0, 1000)
            )
            
            # Добавляем магазины
            product.shops.set(random.sample(shops, random.randint(1, min(3, len(shops)))))
            
            # Добавляем теги
            product.tags.set(random.sample(tags, random.randint(0, min(3, len(tags)))))
            
            # Создаем изображения (заглушки)
            for j in range(random.randint(1, 3)):
                ProductImage.objects.create(
                    product=product,
                    alt_text=f"{product.name} - изображение {j+1}",
                    is_primary=(j == 0),
                    order=j
                )

    def download_image(self, url):
        """Скачивает изображение по URL"""
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                return BytesIO(response.content)
        except:
            pass
        return None