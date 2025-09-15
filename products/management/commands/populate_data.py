from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from products.models import Category, Shop, Seller, Product, ProductImage, ProductCharacteristic, Review, Tag
from decimal import Decimal
import random
from faker import Faker

fake = Faker('ru_RU')
User = get_user_model()


class Command(BaseCommand):
    help = 'Заполняет базу данных тестовыми данными'

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=20, help='Количество товаров для создания')

    def handle(self, *args, **options):
        count = options['count']
        
        with transaction.atomic():
            self.stdout.write('Начинаем заполнение базы данных...')
            
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
            
            self.stdout.write(self.style.SUCCESS('База данных успешно заполнена!'))

    def create_categories(self):
        """Создание категорий"""
        categories_data = [
            {'name': 'Электроника', 'slug': 'electronics', 'icon': 'laptop'},
            {'name': 'Одежда', 'slug': 'clothing', 'icon': 'tshirt'},
            {'name': 'Дом и сад', 'slug': 'home-garden', 'icon': 'home'},
            {'name': 'Спорт', 'slug': 'sports', 'icon': 'dumbbell'},
            {'name': 'Красота', 'slug': 'beauty', 'icon': 'spa'},
            {'name': 'Книги', 'slug': 'books', 'icon': 'book'},
            {'name': 'Автомобили', 'slug': 'automotive', 'icon': 'car'},
            {'name': 'Детские товары', 'slug': 'kids', 'icon': 'baby'},
        ]
        
        for data in categories_data:
            Category.objects.get_or_create(
                slug=data['slug'],
                defaults={
                    'name': data['name'],
                    'icon': data['icon'],
                    'description': f'Категория {data["name"]}'
                }
            )
        
        self.stdout.write(self.style.SUCCESS(f'Создано {Category.objects.count()} категорий'))

    def create_shops(self):
        """Создание магазинов"""
        shops_data = [
            {'name': 'ТехноМир', 'city': 'Москва', 'address': 'ул. Тверская, 1'},
            {'name': 'Модный Дом', 'city': 'Санкт-Петербург', 'address': 'Невский проспект, 50'},
            {'name': 'СпортМакс', 'city': 'Екатеринбург', 'address': 'ул. Ленина, 25'},
            {'name': 'Красота+', 'city': 'Новосибирск', 'address': 'Красный проспект, 100'},
            {'name': 'Книжный Мир', 'city': 'Казань', 'address': 'ул. Баумана, 15'},
        ]
        
        for data in shops_data:
            Shop.objects.get_or_create(
                name=data['name'],
                defaults={
                    'address': data['address'],
                    'city': data['city'],
                    'phone': fake.phone_number(),
                    'email': fake.email(),
                }
            )
        
        self.stdout.write(self.style.SUCCESS(f'Создано {Shop.objects.count()} магазинов'))

    def create_tags(self):
        """Создание тегов"""
        tags_data = [
            'Популярное', 'Новинка', 'Скидка', 'Хит продаж', 'Рекомендуем',
            'Премиум', 'Эко', 'Органическое', 'Бестселлер', 'Лимитированное',
            'Быстрая доставка', 'Гарантия качества', 'Сертифицировано'
        ]
        
        for tag_name in tags_data:
            Tag.objects.get_or_create(name=tag_name)
        
        self.stdout.write(self.style.SUCCESS(f'Создано {Tag.objects.count()} тегов'))

    def create_sellers(self):
        """Создание продавцов"""
        for i in range(5):
            username = f'seller{i+1}'
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': f'seller{i+1}@example.com',
                    'role': 'seller',
                    'first_name': fake.first_name(),
                    'last_name': fake.last_name()
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
        
        # Данные для товаров
        electronics_products = [
            {'name': 'iPhone 15 Pro', 'price': 99999, 'description': 'Новейший смартфон от Apple с чипом A17 Pro'},
            {'name': 'MacBook Air M2', 'price': 129999, 'description': 'Легкий и мощный ноутбук для работы и творчества'},
            {'name': 'AirPods Pro', 'price': 24999, 'description': 'Беспроводные наушники с активным шумоподавлением'},
            {'name': 'iPad Pro', 'price': 89999, 'description': 'Планшет для профессионалов с дисплеем Liquid Retina XDR'},
            {'name': 'Apple Watch Series 9', 'price': 39999, 'description': 'Умные часы с множеством функций для здоровья'},
        ]
        
        clothing_products = [
            {'name': 'Джинсы Levis 501', 'price': 5999, 'description': 'Классические джинсы из денима'},
            {'name': 'Футболка Nike', 'price': 2999, 'description': 'Удобная футболка для спорта и повседневной носки'},
            {'name': 'Куртка The North Face', 'price': 15999, 'description': 'Теплая куртка для активного отдыха'},
            {'name': 'Кроссовки Adidas', 'price': 8999, 'description': 'Спортивные кроссовки для бега и тренировок'},
            {'name': 'Платье Zara', 'price': 4999, 'description': 'Элегантное платье для особых случаев'},
        ]
        
        home_products = [
            {'name': 'Диван IKEA', 'price': 29999, 'description': 'Удобный диван для гостиной'},
            {'name': 'Лампа настольная', 'price': 2999, 'description': 'Современная LED лампа для рабочего стола'},
            {'name': 'Ковер персидский', 'price': 19999, 'description': 'Ручная работа, натуральные материалы'},
            {'name': 'Горшок для цветов', 'price': 999, 'description': 'Керамический горшок для комнатных растений'},
            {'name': 'Шторы блэкаут', 'price': 4999, 'description': 'Затемняющие шторы для спальни'},
        ]
        
        all_products = electronics_products + clothing_products + home_products
        
        for i, product_data in enumerate(all_products[:count]):
            category = random.choice(categories)
            seller = random.choice(sellers)
            
            price = Decimal(str(product_data['price']))
            discount_price = price * Decimal(str(random.uniform(0.7, 0.9))) if random.choice([True, False]) else None
            
            product = Product.objects.create(
                name=product_data['name'],
                description=product_data['description'],
                price=price,
                discount_price=discount_price,
                category=category,
                seller=seller,
                stock_quantity=random.randint(0, 100),
                rating=Decimal(str(random.uniform(3.5, 5.0))),
                reviews_count=random.randint(0, 50)
            )
            
            # Добавляем теги
            product.tags.set(random.sample(tags, random.randint(1, 3)))
            
            # Создаем характеристики
            characteristics = [
                {'name': 'Бренд', 'value': fake.company()},
                {'name': 'Цвет', 'value': fake.color_name()},
                {'name': 'Материал', 'value': random.choice(['Пластик', 'Металл', 'Дерево', 'Ткань', 'Кожа'])},
                {'name': 'Вес', 'value': f"{random.randint(100, 5000)}", 'unit': 'г'},
                {'name': 'Размер', 'value': random.choice(['S', 'M', 'L', 'XL', 'XXL'])},
            ]
            
            for char_data in characteristics:
                ProductCharacteristic.objects.create(
                    product=product,
                    name=char_data['name'],
                    value=char_data['value'],
                    unit=char_data.get('unit', '')
                )
            
            if i % 5 == 0:
                self.stdout.write(f'Создано {i+1} товаров...')
        
        self.stdout.write(self.style.SUCCESS(f'Создано {Product.objects.count()} товаров'))

    def create_reviews(self):
        """Создание отзывов"""
        products = list(Product.objects.all())
        
        # Создаем тестовых пользователей для отзывов
        for i in range(3):
            user, created = User.objects.get_or_create(
                username=f'testuser{i+1}',
                defaults={
                    'email': f'testuser{i+1}@example.com',
                    'first_name': fake.first_name(),
                    'last_name': fake.last_name()
                }
            )
            if created:
                user.set_password('password123')
                user.save()
        
        users = User.objects.filter(username__startswith='testuser')
        
        for product in products[:15]:  # Отзывы только для первых 15 товаров
            for _ in range(random.randint(1, 3)):
                user = random.choice(users)
                Review.objects.create(
                    user=user,
                    product=product,
                    rating=random.randint(1, 5),
                    title=fake.sentence(nb_words=3),
                    text=fake.text(max_nb_chars=200),
                    is_verified_purchase=random.choice([True, False])
                )
        
        self.stdout.write(self.style.SUCCESS(f'Создано {Review.objects.count()} отзывов'))
