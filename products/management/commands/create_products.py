from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from decimal import Decimal
import random
from products.models import (
    Category, Tag, Product, ProductCharacteristic, Seller
)

User = get_user_model()


class Command(BaseCommand):
    help = 'Создает 100 товаров с ценами и характеристиками'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=100,
            help='Количество товаров для создания'
        )

    def handle(self, *args, **options):
        self.stdout.write('Начинаем создание товаров...')
        
        # Создаем базовые данные если их нет
        self.ensure_basic_data()
        
        # Создаем товары
        self.create_products(options['count'])

        self.stdout.write(
            self.style.SUCCESS(f'Успешно создано {options["count"]} товаров!')
        )

    def ensure_basic_data(self):
        """Создает базовые данные если их нет"""
        # Создаем категории
        if not Category.objects.exists():
            self.create_categories()
        
        # Создаем теги
        if not Tag.objects.exists():
            self.create_tags()
        
        # Создаем продавцов
        if not Seller.objects.exists():
            self.create_sellers()

    def create_categories(self):
        """Создает категории товаров"""
        categories_data = [
            'Электроника',
            'Одежда и обувь',
            'Дом и сад',
            'Спорт и отдых',
            'Красота и здоровье',
            'Книги и медиа',
            'Автомобили',
            'Детские товары',
            'Продукты питания',
            'Промышленность',
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
            'Ограниченная серия',
            'Быстрая доставка',
            'Гарантия качества',
        ]
        
        for name in tags_data:
            tag, created = Tag.objects.get_or_create(name=name)
            if created:
                self.stdout.write(f'Создан тег: {tag.name}')

    def create_sellers(self):
        """Создает продавцов"""
        company_names = [
            'ООО "ТехноПро"', 'ИП Иванов', 'ООО "МодаСтиль"', 'ИП Петров',
            'ООО "СпортГир"', 'ИП Сидоров', 'ООО "ДомТовар"', 'ИП Козлов',
            'ООО "Красота+"', 'ИП Морозов', 'ООО "КнигиМир"', 'ИП Волков',
            'ООО "АвтоМир"', 'ИП Соколов', 'ООО "Детки"', 'ИП Лебедев',
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

    def create_products(self, count):
        """Создает товары"""
        categories = list(Category.objects.all())
        sellers = list(Seller.objects.all())
        tags = list(Tag.objects.all())
        
        # Создаем словарь категорий для быстрого поиска
        category_dict = {cat.name: cat for cat in categories}
        
        # Реальные товары с ценами и характеристиками, привязанные к категориям
        real_products = [
            {
                'name': 'iPhone 15 Pro',
                'description': 'Новейший смартфон Apple с титановым корпусом и чипом A17 Pro',
                'category': 'Электроника',
                'price_range': (80000, 120000),
                'characteristics': [
                    ('Цвет', 'Титан'),
                    ('Память', '256 ГБ'),
                    ('Экран', '6.1" Super Retina XDR'),
                    ('Процессор', 'A17 Pro'),
                    ('Камера', '48 МП'),
                    ('Батарея', 'До 23 часов видео'),
                    ('Водонепроницаемость', 'IP68'),
                ]
            },
            {
                'name': 'MacBook Air M3',
                'description': 'Ультратонкий ноутбук с чипом M3 и дисплеем Liquid Retina',
                'category': 'Электроника',
                'price_range': (100000, 150000),
                'characteristics': [
                    ('Цвет', 'Серебристый'),
                    ('Память', '8 ГБ'),
                    ('Диск', '256 ГБ SSD'),
                    ('Экран', '13.6" Liquid Retina'),
                    ('Процессор', 'Apple M3'),
                    ('Вес', '1.24 кг'),
                    ('Батарея', 'До 18 часов'),
                ]
            },
            {
                'name': 'Nike Air Max 270',
                'description': 'Спортивные кроссовки с технологией Air Max для максимального комфорта',
                'category': 'Спорт и отдых',
                'price_range': (8000, 15000),
                'characteristics': [
                    ('Цвет', 'Черный/Белый'),
                    ('Размер', '42'),
                    ('Материал', 'Ткань/Кожа'),
                    ('Подошва', 'Резина'),
                    ('Бренд', 'Nike'),
                    ('Пол', 'Унисекс'),
                    ('Сезон', 'Всесезонные'),
                ]
            },
            {
                'name': 'Samsung Galaxy S24',
                'description': 'Флагманский смартфон Samsung с ИИ и камерой 200 МП',
                'category': 'Электроника',
                'price_range': (70000, 100000),
                'characteristics': [
                    ('Цвет', 'Черный'),
                    ('Память', '128 ГБ'),
                    ('Экран', '6.2" Dynamic AMOLED'),
                    ('Процессор', 'Snapdragon 8 Gen 3'),
                    ('Камера', '50 МП'),
                    ('Батарея', '4000 мАч'),
                    ('5G', 'Поддержка'),
                ]
            },
            {
                'name': 'Adidas Ultraboost 22',
                'description': 'Беговые кроссовки с технологией Boost для профессиональных спортсменов',
                'category': 'Спорт и отдых',
                'price_range': (12000, 20000),
                'characteristics': [
                    ('Цвет', 'Белый/Черный'),
                    ('Размер', '43'),
                    ('Материал', 'Primeknit'),
                    ('Подошва', 'Boost'),
                    ('Бренд', 'Adidas'),
                    ('Тип', 'Беговые'),
                    ('Амортизация', 'Максимальная'),
                ]
            },
            {
                'name': 'Sony WH-1000XM5',
                'description': 'Беспроводные наушники с шумоподавлением и 30-часовой батареей',
                'category': 'Электроника',
                'price_range': (25000, 35000),
                'characteristics': [
                    ('Цвет', 'Черный'),
                    ('Тип', 'Накладные'),
                    ('Подключение', 'Bluetooth 5.2'),
                    ('Батарея', '30 часов'),
                    ('Бренд', 'Sony'),
                    ('Шумоподавление', 'Активное'),
                    ('Вес', '250 г'),
                ]
            },
            {
                'name': 'Dyson V15 Detect',
                'description': 'Беспроводной пылесос с лазерной технологией обнаружения пыли',
                'category': 'Дом и сад',
                'price_range': (45000, 60000),
                'characteristics': [
                    ('Цвет', 'Желтый'),
                    ('Тип', 'Беспроводной'),
                    ('Батарея', '60 минут'),
                    ('Мощность', '230 AW'),
                    ('Бренд', 'Dyson'),
                    ('Фильтрация', 'HEPA'),
                    ('Вес', '3.2 кг'),
                ]
            },
            {
                'name': 'Apple Watch Series 9',
                'description': 'Умные часы с функциями здоровья и Always-On дисплеем',
                'category': 'Электроника',
                'price_range': (30000, 45000),
                'characteristics': [
                    ('Цвет', 'Розовое золото'),
                    ('Размер', '45мм'),
                    ('Экран', 'Always-On Retina'),
                    ('Батарея', '18 часов'),
                    ('Бренд', 'Apple'),
                    ('Водонепроницаемость', 'WR50'),
                    ('Сенсоры', 'Сердце, кровь, ЭКГ'),
                ]
            },
            {
                'name': 'Levi\'s 501 Original',
                'description': 'Классические джинсы прямого кроя из 100% хлопка',
                'category': 'Одежда и обувь',
                'price_range': (5000, 8000),
                'characteristics': [
                    ('Цвет', 'Синий'),
                    ('Размер', '32/32'),
                    ('Материал', '100% Хлопок'),
                    ('Крой', 'Прямой'),
                    ('Бренд', 'Levi\'s'),
                    ('Стирка', 'Можно стирать'),
                    ('Страна', 'США'),
                ]
            },
            {
                'name': 'Canon EOS R6 Mark II',
                'description': 'Зеркальная камера для профессионалов с 24.2 МП матрицей',
                'category': 'Электроника',
                'price_range': (200000, 250000),
                'characteristics': [
                    ('Цвет', 'Черный'),
                    ('Матрица', '24.2 МП'),
                    ('Стабилизация', '5-осевая'),
                    ('Видео', '4K 60p'),
                    ('Бренд', 'Canon'),
                    ('Тип', 'Беззеркальная'),
                    ('Батарея', '580 снимков'),
                ]
            },
            # Добавляем больше товаров для разных категорий
            {
                'name': 'Крем для лица Nivea',
                'description': 'Увлажняющий крем для лица с гиалуроновой кислотой',
                'category': 'Красота и здоровье',
                'price_range': (500, 1500),
                'characteristics': [
                    ('Объем', '50 мл'),
                    ('Тип кожи', 'Все типы'),
                    ('SPF', '15'),
                    ('Бренд', 'Nivea'),
                    ('Страна', 'Германия'),
                    ('Возраст', '25+'),
                ]
            },
            {
                'name': 'Книга "1984" Джордж Оруэлл',
                'description': 'Классический роман-антиутопия в твердом переплете',
                'category': 'Книги и медиа',
                'price_range': (300, 800),
                'characteristics': [
                    ('Автор', 'Джордж Оруэлл'),
                    ('Переплет', 'Твердый'),
                    ('Страниц', '328'),
                    ('Язык', 'Русский'),
                    ('Издательство', 'АСТ'),
                    ('Год', '2023'),
                ]
            },
            {
                'name': 'Детская коляска Chicco',
                'description': 'Универсальная коляска 3 в 1 для новорожденных',
                'category': 'Детские товары',
                'price_range': (15000, 25000),
                'characteristics': [
                    ('Возраст', '0-3 года'),
                    ('Вес', '12 кг'),
                    ('Складывание', 'Книжка'),
                    ('Колеса', '4'),
                    ('Бренд', 'Chicco'),
                    ('Цвет', 'Серый'),
                ]
            },
            {
                'name': 'Автомобильные шины Michelin',
                'description': 'Летние шины 205/55 R16 для легковых автомобилей',
                'category': 'Автомобили',
                'price_range': (8000, 12000),
                'characteristics': [
                    ('Размер', '205/55 R16'),
                    ('Сезон', 'Летние'),
                    ('Бренд', 'Michelin'),
                    ('Индекс скорости', 'H'),
                    ('Индекс нагрузки', '91'),
                    ('Протектор', 'Асимметричный'),
                ]
            },
            {
                'name': 'Хлеб "Бородинский"',
                'description': 'Ржаной хлеб с кориандром по традиционному рецепту',
                'category': 'Продукты питания',
                'price_range': (50, 150),
                'characteristics': [
                    ('Вес', '400 г'),
                    ('Состав', 'Ржаная мука, вода, соль'),
                    ('Срок годности', '5 дней'),
                    ('Производитель', 'Хлебозавод №1'),
                    ('Упаковка', 'Бумажная'),
                ]
            },
            {
                'name': 'Сварочный аппарат Fubag',
                'description': 'Инверторный сварочный аппарат для MMA сварки',
                'category': 'Промышленность',
                'price_range': (15000, 25000),
                'characteristics': [
                    ('Мощность', '200А'),
                    ('Напряжение', '220В'),
                    ('Тип', 'MMA'),
                    ('Бренд', 'Fubag'),
                    ('Вес', '4.5 кг'),
                    ('Гарантия', '2 года'),
                ]
            },
        ]
        
        for i in range(count):
            product_data = real_products[i % len(real_products)]
            
            # Получаем правильную категорию
            category = category_dict.get(product_data['category'])
            if not category:
                category = random.choice(categories)  # Fallback если категория не найдена
            
            seller = random.choice(sellers)
            
            # Создаем товар
            product = Product()
            product.name = f"{product_data['name']} #{i+1}"
            product.description = product_data['description']
            
            # Устанавливаем цену
            price_min, price_max = product_data['price_range']
            product.price = Decimal(random.uniform(price_min, price_max))
            if random.choice([True, False]):
                product.discount_price = product.price * Decimal(random.uniform(0.8, 0.95))
            
            product.category = category
            product.seller = seller
            product.stock_quantity = random.randint(5, 100)
            product.is_active = True
            product.rating = Decimal(random.uniform(3.5, 5.0))
            product.reviews_count = random.randint(0, 50)
            product.views_count = random.randint(0, 200)
            
            product.save()
            
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
            
            if (i + 1) % 10 == 0:
                self.stdout.write(f'Создано товаров: {i + 1}')

        self.stdout.write(f'Всего создано товаров: {count}')
