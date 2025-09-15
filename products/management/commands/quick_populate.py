from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from products.models import Category, Shop, Seller, Product, ProductCharacteristic, Review, Tag
from decimal import Decimal
import random
from faker import Faker

fake = Faker('ru_RU')
User = get_user_model()


class Command(BaseCommand):
    help = 'Быстрое заполнение базы данных'

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=1000, help='Количество товаров')

    def handle(self, *args, **options):
        count = options['count']
        
        self.stdout.write('Начинаем быстрое заполнение...')
        
        # Создаем категории
        self.create_categories()
        
        # Создаем продавцов
        self.create_sellers()
        
        # Создаем товары
        self.create_products(count)
        
        self.stdout.write(self.style.SUCCESS(f'Создано {count} товаров!'))

    def create_categories(self):
        categories_data = [
            'Электроника', 'Одежда', 'Дом и сад', 'Спорт', 'Красота',
            'Автотовары', 'Детские товары', 'Книги', 'Продукты', 'Зоотовары'
        ]
        
        for name in categories_data:
            Category.objects.get_or_create(
                name=name,
                defaults={'slug': name.lower().replace(' ', '-')}
            )

    def create_sellers(self):
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
            
            Seller.objects.get_or_create(
                user=user,
                defaults={
                    'company_name': fake.company(),
                    'description': fake.text(max_nb_chars=100),
                    'is_verified': True,
                    'rating': round(random.uniform(4.0, 5.0), 1),
                }
            )

    def create_products(self, count):
        categories = list(Category.objects.all())
        sellers = list(Seller.objects.all())
        
        if not categories or not sellers:
            self.stdout.write('Нет категорий или продавцов!')
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
                name = f"{random.choice(product_names)} {fake.word().title()}"
                category = random.choice(categories)
                seller = random.choice(sellers)
                
                base_price = Decimal(str(round(random.uniform(100, 50000), 2)))
                has_discount = random.choice([True, False, False])
                
                if has_discount:
                    discount_percent = random.randint(5, 50)
                    discount_price = base_price * (1 - discount_percent / 100)
                    discount_price = Decimal(str(round(discount_price, 2)))
                else:
                    discount_price = None
                
                product = Product.objects.create(
                    name=name,
                    description=fake.text(max_nb_chars=300),
                    price=base_price,
                    discount_price=discount_price,
                    category=category,
                    seller=seller,
                    stock_quantity=random.randint(0, 1000),
                    sku=f"SKU-{random.randint(100000, 999999)}",
                    is_active=True,
                    rating=round(random.uniform(3.0, 5.0), 1),
                    reviews_count=random.randint(0, 100),
                    views_count=random.randint(0, 10000)
                )
                
                # Добавляем характеристики
                characteristics = [
                    {'name': 'Бренд', 'value': fake.company()},
                    {'name': 'Цвет', 'value': random.choice(['Черный', 'Белый', 'Красный', 'Синий', 'Зеленый'])},
                    {'name': 'Материал', 'value': random.choice(['Пластик', 'Металл', 'Ткань', 'Кожа', 'Дерево'])},
                ]
                
                for char_data in characteristics:
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
