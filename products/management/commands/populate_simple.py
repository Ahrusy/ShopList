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
    help = 'Заполняет базу данных тестовыми данными (упрощенная версия)'

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=1000, help='Количество товаров для создания')

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
            
            self.stdout.write(self.style.SUCCESS(f'База данных успешно заполнена! Создано {count} товаров.'))

    def create_categories(self):
        """Создание категорий"""
        categories_data = [
            {'name': 'Электроника', 'slug': 'electronics'},
            {'name': 'Одежда', 'slug': 'clothing'},
            {'name': 'Дом и сад', 'slug': 'home-garden'},
            {'name': 'Спорт', 'slug': 'sports'},
            {'name': 'Красота', 'slug': 'beauty'},
            {'name': 'Автотовары', 'slug': 'auto'},
            {'name': 'Детские товары', 'slug': 'kids'},
            {'name': 'Книги', 'slug': 'books'},
            {'name': 'Продукты', 'slug': 'food'},
            {'name': 'Зоотовары', 'slug': 'pets'},
            {'name': 'Строительство', 'slug': 'construction'},
            {'name': 'Хобби', 'slug': 'hobby'},
        ]
        
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                slug=cat_data['slug'],
                defaults={'name': cat_data['name']}
            )
            if created:
                self.stdout.write(f'Создана категория: {category.name}')

    def create_shops(self):
        """Создание магазинов"""
        shops_data = [
            {'name': 'ТехноМир', 'address': 'ул. Ленина, 1', 'city': 'Москва'},
            {'name': 'Модный Дом', 'address': 'пр. Мира, 15', 'city': 'Санкт-Петербург'},
            {'name': 'Дом и Сад', 'address': 'ул. Садовая, 25', 'city': 'Новосибирск'},
            {'name': 'СпортМакс', 'address': 'ул. Спортивная, 10', 'city': 'Екатеринбург'},
            {'name': 'Красота+', 'address': 'ул. Красивая, 5', 'city': 'Казань'},
        ]
        
        for shop_data in shops_data:
            shop, created = Shop.objects.get_or_create(
                name=shop_data['name'],
                defaults={
                    'address': shop_data['address'],
                    'city': shop_data['city']
                }
            )
            if created:
                self.stdout.write(f'Создан магазин: {shop.name}')

    def create_tags(self):
        """Создание тегов"""
        tags_data = [
            'новинка', 'скидка', 'хит', 'премиум', 'эко', 'быстрая доставка',
            'гарантия', 'качество', 'бюджетный', 'стильный', 'удобный', 'надежный'
        ]
        
        for tag_name in tags_data:
            tag, created = Tag.objects.get_or_create(name=tag_name)
            if created:
                self.stdout.write(f'Создан тег: {tag.name}')

    def create_sellers(self):
        """Создание продавцов"""
        shops = Shop.objects.all()
        
        for i in range(5):
            user, created = User.objects.get_or_create(
                username=f'seller{i+1}',
                defaults={
                    'email': f'seller{i+1}@example.com',
                    'first_name': fake.first_name(),
                    'last_name': fake.last_name(),
                }
            )
            if created:
                user.set_password('password123')
                user.save()
            
            seller, created = Seller.objects.get_or_create(
                user=user,
                defaults={
                    'company_name': fake.company(),
                    'description': fake.text(max_nb_chars=200),
                    'is_verified': random.choice([True, False]),
                    'rating': round(random.uniform(3.0, 5.0), 1),
                }
            )
            if created:
                self.stdout.write(f'Создан продавец: {seller.company_name}')

    def create_products(self, count):
        """Создание товаров"""
        categories = list(Category.objects.all())
        sellers = list(Seller.objects.all())
        tags = list(Tag.objects.all())
        
        if not categories or not sellers:
            self.stdout.write(self.style.ERROR('Нет категорий или продавцов для создания товаров'))
            return
        
        product_names = [
            'Смартфон', 'Ноутбук', 'Планшет', 'Наушники', 'Клавиатура', 'Мышь',
            'Футболка', 'Джинсы', 'Куртка', 'Платье', 'Обувь', 'Сумка',
            'Диван', 'Стол', 'Стул', 'Кровать', 'Шкаф', 'Зеркало',
            'Велосипед', 'Гантели', 'Мяч', 'Кроссовки', 'Спортивная форма',
            'Крем', 'Шампунь', 'Помада', 'Тушь', 'Парфюм', 'Мыло',
            'Автомагнитола', 'Коврики', 'Чехлы', 'Аккумулятор', 'Масло',
            'Игрушка', 'Коляска', 'Детская одежда', 'Питание', 'Книга',
            'Роман', 'Учебник', 'Энциклопедия', 'Журнал', 'Комикс',
            'Хлеб', 'Молоко', 'Мясо', 'Овощи', 'Фрукты', 'Сладости',
            'Корм', 'Игрушка для кота', 'Ошейник', 'Поводок', 'Домик',
            'Краска', 'Кисть', 'Дрель', 'Молоток', 'Гвозди', 'Шурупы',
            'Модель', 'Краски', 'Кисти', 'Холст', 'Рамка', 'Клей'
        ]
        
        for i in range(count):
            try:
                # Основные данные товара
                name = f"{random.choice(product_names)} {fake.word().title()}"
                category = random.choice(categories)
                seller = random.choice(sellers)
                
                # Цена и скидка
                base_price = Decimal(str(round(random.uniform(100, 50000), 2)))
                has_discount = random.choice([True, False, False])  # 33% шанс скидки
                
                if has_discount:
                    discount_percent = random.randint(5, 50)
                    discount_price = base_price * (1 - discount_percent / 100)
                    discount_price = Decimal(str(round(discount_price, 2)))
                else:
                    discount_price = None
                
                # Создаем товар
                product = Product.objects.create(
                    name=name,
                    description=fake.text(max_nb_chars=500),
                    price=base_price,
                    discount_price=discount_price,
                    category=category,
                    seller=seller,
                    stock_quantity=random.randint(0, 1000),
                    sku=f"SKU-{random.randint(100000, 999999)}",
                    is_active=random.choice([True, True, True, False]),  # 75% активных
                    rating=round(random.uniform(3.0, 5.0), 1),
                    reviews_count=random.randint(0, 100),
                    views_count=random.randint(0, 10000)
                )
                
                # Добавляем теги
                product_tags = random.sample(tags, random.randint(1, 4))
                product.tags.set(product_tags)
                
                # Создаем характеристики
                characteristics = [
                    {'name': 'Бренд', 'value': fake.company()},
                    {'name': 'Цвет', 'value': random.choice(['Черный', 'Белый', 'Красный', 'Синий', 'Зеленый'])},
                    {'name': 'Материал', 'value': random.choice(['Пластик', 'Металл', 'Ткань', 'Кожа', 'Дерево'])},
                    {'name': 'Размер', 'value': random.choice(['S', 'M', 'L', 'XL', 'XXL'])},
                    {'name': 'Вес', 'value': f"{random.randint(1, 5000)} г"},
                ]
                
                for char_data in characteristics[:random.randint(2, 4)]:
                    ProductCharacteristic.objects.create(
                        product=product,
                        name=char_data['name'],
                        value=char_data['value']
                    )
                
                if i % 100 == 0:
                    self.stdout.write(f'Создано товаров: {i+1}/{count}')
                    
            except Exception as e:
                self.stdout.write(f'Ошибка при создании товара {i+1}: {e}')
                continue

    def create_reviews(self):
        """Создание отзывов"""
        products = Product.objects.all()[:100]  # Только для первых 100 товаров
        users = User.objects.all()
        
        if not users.exists():
            # Создаем тестовых пользователей
            for i in range(10):
                user, created = User.objects.get_or_create(
                    username=f'user{i+1}',
                    defaults={
                        'email': f'user{i+1}@example.com',
                        'first_name': fake.first_name(),
                        'last_name': fake.last_name(),
                    }
                )
                if created:
                    user.set_password('password123')
                    user.save()
        
        users = list(User.objects.all())
        
        for product in products:
            # Создаем 1-5 отзывов для каждого товара
            num_reviews = random.randint(1, 5)
            for _ in range(num_reviews):
                try:
                    Review.objects.create(
                        product=product,
                        user=random.choice(users),
                        rating=random.randint(1, 5),
                        comment=fake.text(max_nb_chars=200)
                    )
                except:
                    continue
