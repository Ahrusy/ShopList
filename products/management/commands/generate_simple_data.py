from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from products.models import Category, Shop, Tag, Seller, Product, ProductImage, ProductCharacteristic, Review, Order, OrderItem
from decimal import Decimal
import random
from faker import Faker

fake = Faker('ru_RU')
User = get_user_model()


class Command(BaseCommand):
    help = 'Генерирует простые тестовые данные для маркетплейса'

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=50, help='Количество товаров для создания')

    def handle(self, *args, **options):
        count = options['count']
        
        with transaction.atomic():
            self.stdout.write('Начинаем генерацию тестовых данных...')
            
            # Создаем категории
            self.create_categories()
            
            # Создаем магазины
            self.create_shops()
            
            # Создаем теги
            self.create_tags()
            
            # Создаем продавцов
            self.create_sellers()
            
            # Создаем товары
            self.create_products(count)
            
            # Создаем отзывы
            self.create_reviews()
            
            self.stdout.write(self.style.SUCCESS('Генерация данных завершена!'))

    def create_categories(self):
        """Создание категорий"""
        categories_data = [
            {'name': 'Электроника', 'slug': 'electronics', 'icon': 'laptop'},
            {'name': 'Одежда', 'slug': 'clothing', 'icon': 'tshirt'},
            {'name': 'Дом и сад', 'slug': 'home-garden', 'icon': 'home'},
            {'name': 'Спорт', 'slug': 'sports', 'icon': 'dumbbell'},
            {'name': 'Красота', 'slug': 'beauty', 'icon': 'spa'},
            {'name': 'Книги', 'slug': 'books', 'icon': 'book'},
        ]
        
        for data in categories_data:
            Category.objects.get_or_create(
                slug=data['slug'],
                defaults={
                    'name': data['name'],
                    'icon': data['icon']
                }
            )
        
        self.stdout.write(self.style.SUCCESS(f'Создано {Category.objects.count()} категорий'))

    def create_shops(self):
        """Создание магазинов"""
        for i in range(5):
            Shop.objects.get_or_create(
                name=fake.company(),
                defaults={
                    'address': fake.address(),
                    'city': fake.city(),
                    'phone': fake.phone_number(),
                    'email': fake.email(),
                }
            )
        
        self.stdout.write(self.style.SUCCESS(f'Создано {Shop.objects.count()} магазинов'))

    def create_tags(self):
        """Создание тегов"""
        tags_data = [
            'Популярное', 'Новинка', 'Скидка', 'Хит продаж', 'Рекомендуем',
            'Премиум', 'Эко', 'Органическое', 'Бестселлер', 'Лимитированное'
        ]
        
        for tag_name in tags_data:
            Tag.objects.get_or_create(name=tag_name)
        
        self.stdout.write(self.style.SUCCESS(f'Создано {Tag.objects.count()} тегов'))

    def create_sellers(self):
        """Создание продавцов"""
        for i in range(3):
            user, created = User.objects.get_or_create(
                username=f'seller{i+1}',
                defaults={
                    'email': f'seller{i+1}@example.com',
                    'role': 'seller'
                }
            )
            if created:
                user.set_password('password123')
                user.save()
            
            Seller.objects.get_or_create(
                user=user,
                defaults={
                    'company_name': fake.company(),
                    'description': fake.text(max_nb_chars=200),
                    'commission_rate': Decimal(str(random.uniform(3, 10))),
                    'is_verified': random.choice([True, False])
                }
            )
        
        self.stdout.write(self.style.SUCCESS(f'Создано {Seller.objects.count()} продавцов'))

    def create_products(self, count):
        """Создание товаров"""
        categories = list(Category.objects.all())
        sellers = list(Seller.objects.all())
        tags = list(Tag.objects.all())
        
        for i in range(count):
            category = random.choice(categories)
            seller = random.choice(sellers)
            
            price = Decimal(str(random.uniform(100, 10000)))
            discount_price = price * Decimal(str(random.uniform(0.7, 0.9))) if random.choice([True, False]) else None
            
            product = Product.objects.create(
                name=fake.catch_phrase(),
                description=fake.text(max_nb_chars=500),
                price=price,
                discount_price=discount_price,
                category=category,
                seller=seller,
                stock_quantity=random.randint(0, 100),
                rating=Decimal(str(random.uniform(3, 5))),
                reviews_count=random.randint(0, 50)
            )
            
            # Добавляем теги
            product.tags.set(random.sample(tags, random.randint(1, 3)))
            
            # Создаем характеристики
            characteristics = [
                {'name': 'Бренд', 'value': fake.company()},
                {'name': 'Цвет', 'value': fake.color_name()},
                {'name': 'Материал', 'value': random.choice(['Пластик', 'Металл', 'Дерево', 'Ткань'])},
                {'name': 'Вес', 'value': f"{random.randint(100, 5000)}", 'unit': 'г'},
            ]
            
            for char_data in characteristics:
                ProductCharacteristic.objects.create(
                    product=product,
                    name=char_data['name'],
                    value=char_data['value'],
                    unit=char_data.get('unit', '')
                )
            
            if i % 10 == 0:
                self.stdout.write(f'Создано {i+1} товаров...')
        
        self.stdout.write(self.style.SUCCESS(f'Создано {Product.objects.count()} товаров'))

    def create_reviews(self):
        """Создание отзывов"""
        products = list(Product.objects.all())
        
        # Создаем тестового пользователя для отзывов
        user, created = User.objects.get_or_create(
            username='testuser',
            defaults={'email': 'test@example.com'}
        )
        if created:
            user.set_password('password123')
            user.save()
        
        for product in products[:20]:  # Отзывы только для первых 20 товаров
            for _ in range(random.randint(1, 5)):
                Review.objects.create(
                    user=user,
                    product=product,
                    rating=random.randint(1, 5),
                    title=fake.sentence(nb_words=3),
                    text=fake.text(max_nb_chars=200),
                    is_verified_purchase=random.choice([True, False])
                )
        
        self.stdout.write(self.style.SUCCESS(f'Создано {Review.objects.count()} отзывов'))
