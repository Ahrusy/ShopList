from django.core.management.base import BaseCommand
from django.db import transaction
from decimal import Decimal
import random
from products.models import (
    Category, Shop, Tag, Product, ProductImage, ProductCharacteristic,
    Seller, User
)


class Command(BaseCommand):
    help = 'Загружает реальные товары с русскими названиями, описаниями и характеристиками'

    def add_arguments(self, parser):
        parser.add_argument(
            '--products',
            type=int,
            default=50,
            help='Количество товаров для загрузки'
        )

    def handle(self, *args, **options):
        self.stdout.write('Начинаем загрузку реальных русских товаров...')
        
        # Создаем базовые данные если их нет
        self.ensure_basic_data()
        
        # Загружаем реальные русские товары
        self.load_russian_products(options['products'])

        self.stdout.write(
            self.style.SUCCESS('Реальные русские товары успешно загружены!')
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
        if Seller.objects.count() < 5:
            self.create_sellers()

    def create_categories(self):
        """Создает категории товаров на русском языке"""
        categories_data = [
            {
                'name': 'Смартфоны и гаджеты',
                'description': 'Смартфоны, планшеты, умные часы и другие гаджеты',
                'slug': 'smartphones-gadgets'
            },
            {
                'name': 'Компьютеры и ноутбуки',
                'description': 'Ноутбуки, компьютеры, мониторы и компьютерные комплектующие',
                'slug': 'computers-laptops'
            },
            {
                'name': 'Бытовая техника',
                'description': 'Холодильники, стиральные машины, микроволновки и другая техника для дома',
                'slug': 'home-appliances'
            },
            {
                'name': 'Одежда и обувь',
                'description': 'Модная одежда и обувь для всей семьи',
                'slug': 'clothing-shoes'
            },
            {
                'name': 'Красота и здоровье',
                'description': 'Косметика, парфюмерия и товары для здоровья',
                'slug': 'beauty-health'
            },
            {
                'name': 'Спорт и отдых',
                'description': 'Спортивные товары, туристическое снаряжение',
                'slug': 'sports-outdoor'
            },
            {
                'name': 'Детские товары',
                'description': 'Игрушки, одежда и товары для детей',
                'slug': 'kids-products'
            },
            {
                'name': 'Дом и сад',
                'description': 'Мебель, декор, товары для сада и дачи',
                'slug': 'home-garden'
            }
        ]
        
        for i, data in enumerate(categories_data):
            category, created = Category.objects.get_or_create(
                name=data['name'],
                defaults={
                    'description': data['description'],
                    'slug': data['slug'],
                    'is_active': True,
                    'sort_order': i
                }
            )
            if created:
                self.stdout.write(f'Создана категория: {category.name}')

    def create_tags(self):
        """Создает теги товаров на русском языке"""
        tags_data = [
            'Новинка',
            'Хит продаж',
            'Распродажа',
            'Премиум',
            'Экологично',
            'Ограниченный тираж',
            'Быстрая доставка',
            'Гарантия качества',
        ]
        
        for name in tags_data:
            tag, created = Tag.objects.get_or_create(name=name)
            if created:
                self.stdout.write(f'Создан тег: {tag.name}')

    def create_shops(self):
        """Создает магазины на русском языке"""
        shops_data = [
            {
                'name': 'Электроника Маркет',
                'address': 'ул. Тверская, 15, Москва',
                'city': 'Москва',
                'coords': (55.7558, 37.6173)
            },
            {
                'name': 'Техно Дом',
                'address': 'пр. Невский, 30, Санкт-Петербург',
                'city': 'Санкт-Петербург',
                'coords': (59.9311, 30.3609)
            },
            {
                'name': 'Гипермаркет Электроники',
                'address': 'ул. Кирова, 50, Екатеринбург',
                'city': 'Екатеринбург',
                'coords': (56.8431, 60.6454)
            },
            {
                'name': 'Мир Техники',
                'address': 'ул. Ленина, 25, Новосибирск',
                'city': 'Новосибирск',
                'coords': (55.0084, 82.9357)
            },
            {
                'name': 'Техно Сити',
                'address': 'ул. Советская, 10, Казань',
                'city': 'Казань',
                'coords': (55.8304, 49.0661)
            }
        ]
        
        for data in shops_data:
            shop, created = Shop.objects.get_or_create(
                name=data['name'],
                defaults={
                    'address': data['address'],
                    'city': data['city'],
                    'latitude': data['coords'][0],
                    'longitude': data['coords'][1],
                    'phone': f"+7{random.randint(9000000000, 9999999999)}",
                    'email': f"info@{data['name'].lower().replace(' ', '')}.ru",
                    'is_active': True
                }
            )
            if created:
                self.stdout.write(f'Создан магазин: {shop.name}')

    def create_sellers(self):
        """Создает продавцов на русском языке"""
        company_names = [
            'ООО "ТехноМаркет"',
            'ИП Сидоров А.В.',
            'ООО "ЭлектроДом"',
            'ИП Петрова М.С.',
            'ООО "ГаджетСити"',
            'ИП Иванов И.И.',
            'ООО "СмартТех"',
            'ИП Козлова Е.А.',
        ]
        
        for i, company_name in enumerate(company_names):
            # Проверяем, существует ли уже такой продавец
            if Seller.objects.filter(company_name=company_name).exists():
                continue
                
            # Создаем пользователя-продавца
            user = User.objects.create_user(
                username=f'seller_{i+100}',  # Используем другие номера, чтобы не конфликтовать
                email=f'seller{i+100}@example.com',
                password='password123',
                role='seller',
                first_name=f'Продавец {i+1}',
                last_name='Тестовый'
            )
            
            # Создаем профиль продавца
            seller = Seller.objects.create(
                user=user,
                company_name=company_name,
                description=f'Официальный дилер. Компания {company_name} работает на рынке с 2010 года.',
                commission_rate=Decimal(random.uniform(3.0, 15.0)),
                is_verified=random.choice([True, False])
            )
            
            self.stdout.write(f'Создан продавец: {seller.company_name}')

    def load_russian_products(self, count):
        """Загружает реальные русские товары"""
        categories = list(Category.objects.all())
        sellers = list(Seller.objects.all())
        tags = list(Tag.objects.all())
        shops = list(Shop.objects.all())
        
        # Реальные русские товары с характеристиками
        russian_products = [
            {
                'name': 'Смартфон Apple iPhone 15 Pro',
                'description': 'Новейший флагманский смартфон Apple с титановым корпусом и чипом A17 Pro. Оснащен системой камер Pro с 48 МП, экраном Super Retina XDR 6.1" и функцией Dynamic Island.',
                'category_name': 'Смартфоны и гаджеты',
                'price': 99990,
                'discount_price': 89990,
                'characteristics': [
                    ('Цвет', 'Титан'),
                    ('Объем памяти', '128 ГБ'),
                    ('Диагональ экрана', '6.1 дюйм'),
                    ('Процессор', 'Apple A17 Pro'),
                    ('Основная камера', '48 МП'),
                    ('Фронтальная камера', '12 МП'),
                    ('Емкость аккумулятора', '3274 мА·ч'),
                    ('Вес', '187 г'),
                    ('Гарантия', '12 месяцев'),
                    ('Производитель', 'Apple'),
                    ('Страна производства', 'Китай'),
                ]
            },
            {
                'name': 'Ноутбук Apple MacBook Air 15',
                'description': 'Тонкий и легкий ноутбук с процессором Apple M2 и экраном Liquid Retina 15.3". Идеален для работы, учебы и творчества. Время автономной работы до 18 часов.',
                'category_name': 'Компьютеры и ноутбуки',
                'price': 129990,
                'discount_price': 119990,
                'characteristics': [
                    ('Цвет', 'Серый космос'),
                    ('Диагональ экрана', '15.3 дюйма'),
                    ('Процессор', 'Apple M2'),
                    ('Оперативная память', '8 ГБ'),
                    ('SSD накопитель', '256 ГБ'),
                    ('Видеокарта', 'Встроенная'),
                    ('Вес', '1.51 кг'),
                    ('Время автономной работы', 'до 18 часов'),
                    ('Гарантия', '12 месяцев'),
                    ('Производитель', 'Apple'),
                    ('Страна производства', 'Китай'),
                ]
            },
            {
                'name': 'Стиральная машина LG F2J5HS4W',
                'description': 'Стиральная машина с прямым приводом Inverter Direct Drive. Технология 6_motion DD обеспечивает бережную стирку. Функция TurboWash ускоряет стирку на 30 минут.',
                'category_name': 'Бытовая техника',
                'price': 45990,
                'discount_price': 39990,
                'characteristics': [
                    ('Тип загрузки', 'Фронтальная'),
                    ('Максимальная загрузка', '8 кг'),
                    ('Отжим', '1400 об/мин'),
                    ('Класс энергопотребления', 'А+++'),
                    ('Класс стирки', 'А'),
                    ('Класс отжима', 'В'),
                    ('Прямой привод', 'Да'),
                    ('Управление', 'Электронное'),
                    ('Дисплей', 'Да'),
                    ('Габариты (Ш×Г×В)', '60×60×85 см'),
                    ('Вес', '72 кг'),
                    ('Гарантия', '24 месяца'),
                    ('Производитель', 'LG'),
                    ('Страна производства', 'Южная Корея'),
                ]
            },
            {
                'name': 'Пылесос Dyson V15 Detect',
                'description': 'Беспроводной пылесос с лазерной технологией обнаружения пыли. Мощный цифровой двигатель V15 обеспечивает высокую эффективность уборки. Интеллектуальная система подсчета пыли.',
                'category_name': 'Бытовая техника',
                'price': 54990,
                'discount_price': 49990,
                'characteristics': [
                    ('Тип', 'Беспроводной'),
                    ('Тип уборки', 'Сухая'),
                    ('Мощность', '240 Вт'),
                    ('Время работы', 'до 60 мин'),
                    ('Время зарядки', '4.5 часа'),
                    ('Емкость контейнера', '0.76 л'),
                    ('Вес', '3.1 кг'),
                    ('Комплектация', 'Пылесос, насадки, зарядное устройство'),
                    ('Гарантия', '24 месяца'),
                    ('Производитель', 'Dyson'),
                    ('Страна производства', 'Малайзия'),
                ]
            },
            {
                'name': 'Кроссовки Nike Air Max 270',
                'description': 'Спортивные кроссовки Nike с воздушной подушкой Air Max. Верх из прочной ткани и синтетического материала. Амортизирующая подошва обеспечивает комфорт при ходьбе.',
                'category_name': 'Одежда и обувь',
                'price': 12990,
                'discount_price': 10990,
                'characteristics': [
                    ('Цвет', 'Черный/Белый'),
                    ('Размер', '42'),
                    ('Пол', 'Унисекс'),
                    ('Материал верха', 'Текстиль/Синтетика'),
                    ('Материал подкладки', 'Текстиль'),
                    ('Материал подошвы', 'Резина'),
                    ('Тип подошвы', 'Платформа'),
                    ('Страна производства', 'Вьетнам'),
                    ('Гарантия', '30 дней'),
                    ('Производитель', 'Nike'),
                ]
            },
            {
                'name': 'Парфюмерия Chanel Coco Mademoiselle',
                'description': 'Женская парфюмерия в виде туалетной воды. Цветочные и восточные ноты. Верхние ноты: апельсин, бергамот. Средние ноты: роза, жасмин. Базовые ноты: пачули, ваниль.',
                'category_name': 'Красота и здоровье',
                'price': 15990,
                'discount_price': 13990,
                'characteristics': [
                    ('Объем', '50 мл'),
                    ('Тип', 'Туалетная вода'),
                    ('Пол', 'Женский'),
                    ('Группа аромата', 'Цветочные, Восточные'),
                    ('Верхние ноты', 'Апельсин, бергамот'),
                    ('Средние ноты', 'Роза, жасмин'),
                    ('Базовые ноты', 'Пачули, ваниль'),
                    ('Страна производства', 'Франция'),
                    ('Гарантия', 'Оригинал'),
                    ('Производитель', 'Chanel'),
                ]
            },
            {
                'name': 'Велосипед Stels Navigator 710',
                'description': 'Горный велосипед для начинающих и опытных велосипедистов. Алюминиевая рама, 21 скорость, дисковые тормоза. Подходит для поездок по городу и легких трасс.',
                'category_name': 'Спорт и отдых',
                'price': 18990,
                'discount_price': 16990,
                'characteristics': [
                    ('Тип', 'Горный'),
                    ('Возраст', 'Взрослый'),
                    ('Размер рамы', '17 дюймов'),
                    ('Материал рамы', 'Алюминий'),
                    ('Количество скоростей', '21'),
                    ('Тип тормозов', 'Дисковые механические'),
                    ('Диаметр колес', '26 дюймов'),
                    ('Вес', '14.5 кг'),
                    ('Гарантия', '12 месяцев'),
                    ('Производитель', 'Stels'),
                    ('Страна производства', 'Китай'),
                ]
            },
            {
                'name': 'Конструктор LEGO Creator Expert 10295',
                'description': 'Пожарная станция - набор конструктора LEGO Creator Expert. Содержит 2442 детали для сборки пожарной станции с гаражом, башней, жилыми помещениями и т.д.',
                'category_name': 'Детские товары',
                'price': 19990,
                'discount_price': 17990,
                'characteristics': [
                    ('Количество деталей', '2442'),
                    ('Возраст', '18+'),
                    ('Тип', 'Конструктор'),
                    ('Тема', 'Creator Expert'),
                    ('Персонажи', 'Пожарные'),
                    ('Материал', 'Пластик'),
                    ('Размер упаковки', '54×38×12 см'),
                    ('Вес', '1.5 кг'),
                    ('Гарантия', 'Оригинал'),
                    ('Производитель', 'LEGO'),
                    ('Страна производства', 'Дания'),
                ]
            },
            {
                'name': 'Диван-кровать Matrix Орфей 2',
                'description': 'Угловой диван-кровать с механизмом трансформации "аккордеон". Каркас из березовой фанеры и металла. Наполнение сиденья: пенополиуретан высокой плотности.',
                'category_name': 'Дом и сад',
                'price': 45990,
                'discount_price': 39990,
                'characteristics': [
                    ('Тип', 'Угловой'),
                    ('Механизм трансформации', 'Аккордеон'),
                    ('Размеры (Ш×Г×В)', '214×86×83 см'),
                    ('Размеры спального места', '142×196 см'),
                    ('Материал обивки', 'Жаккард'),
                    ('Цвет обивки', 'Серый'),
                    ('Наполнение сиденья', 'Пенополиуретан'),
                    ('Каркас', 'Березовая фанера, металл'),
                    ('Вес', '56 кг'),
                    ('Гарантия', '18 месяцев'),
                    ('Производитель', 'Matrix'),
                    ('Страна производства', 'Россия'),
                ]
            },
            {
                'name': 'Газонокосилка Hyundai MowMaster 42S',
                'description': 'Бензиновая газонокосилка с двигателем Hyundai. Подходит для участков до 1200 м². Регулировка высоты кошения в 7 положениях. Система защиты от перегрузок.',
                'category_name': 'Дом и сад',
                'price': 22990,
                'discount_price': 19990,
                'characteristics': [
                    ('Тип', 'Бензиновая'),
                    ('Мощность двигателя', '4.0 л.с.'),
                    ('Объем двигателя', '140 см³'),
                    ('Ширина кошения', '42 см'),
                    ('Высота кошения', '25-75 мм'),
                    ('Количество положений высоты', '7'),
                    ('Объем травосборника', '55 л'),
                    ('Вес', '17.5 кг'),
                    ('Гарантия', '36 месяцев'),
                    ('Производитель', 'Hyundai'),
                    ('Страна производства', 'Китай'),
                ]
            },
        ]
        
        for i in range(min(count, len(russian_products) * 3)):  # Повторяем товары несколько раз
            product_data = russian_products[i % len(russian_products)]
            
            # Находим категорию по имени
            try:
                category = Category.objects.filter(name=product_data['category_name']).first()
                if category is None:
                    category = random.choice(categories)
            except Category.DoesNotExist:
                category = random.choice(categories)
            
            seller = random.choice(sellers)
            
            self.stdout.write(f'Создаем товар {i+1}: {product_data["name"]}')
            
            # Создаем товар
            product = Product(
                name=product_data['name'],
                description=product_data['description'],
                price=Decimal(product_data['price']),
                discount_price=Decimal(product_data['discount_price']) if product_data['discount_price'] else None,
                category=category,
                seller=seller,
                stock_quantity=random.randint(5, 100),
                is_active=True,
                rating=Decimal(random.uniform(3.5, 5.0)).quantize(Decimal('0.01')),
                reviews_count=random.randint(0, 50)
            )
            
            try:
                product.save()
                self.stdout.write(f'  Товар сохранен: {product.name}')
            except Exception as e:
                self.stdout.write(f'  Ошибка сохранения товара: {e}')
                continue
            
            # Добавляем магазины
            product.shops.set(random.sample(shops, random.randint(1, 3)))
            
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
            
            # Создаем заглушку изображения
            self.create_placeholder_image(product)
            
            self.stdout.write(f'Создан товар: {product.name}')

    def create_placeholder_image(self, product):
        """Создает заглушку изображения"""
        try:
            from PIL import Image, ImageDraw, ImageFont
            import io
            
            # Создаем простое изображение-заглушку
            img = Image.new('RGB', (400, 300), color='lightgray')
            
            # Добавляем текст
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
            product_image = ProductImage(
                product=product,
                alt_text=f"Изображение {product.name}",
                order=0
            )
            
            filename = f"product_{product.id}_russian.jpg"
            product_image.image.save(filename, img_io, save=True)
            
            self.stdout.write(f'  Создана заглушка: {filename}')
            
        except Exception as e:
            self.stdout.write(f'  Ошибка создания заглушки: {e}')