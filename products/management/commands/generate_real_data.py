from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from decimal import Decimal
import random
import requests
from PIL import Image
import io
from products.models import (
    Category, Shop, Tag, Product, ProductImage, ProductCharacteristic,
    Seller, Order, OrderItem, Review, Cart, CartItem, Commission, User
)


class Command(BaseCommand):
    help = 'Генерирует реалистичные тестовые данные с изображениями'

    def add_arguments(self, parser):
        parser.add_argument(
            '--categories',
            type=int,
            default=10,
            help='Количество категорий'
        )
        parser.add_argument(
            '--sellers',
            type=int,
            default=20,
            help='Количество продавцов'
        )
        parser.add_argument(
            '--products',
            type=int,
            default=100,
            help='Количество товаров'
        )
        parser.add_argument(
            '--reviews',
            type=int,
            default=200,
            help='Количество отзывов'
        )
        parser.add_argument(
            '--orders',
            type=int,
            default=50,
            help='Количество заказов'
        )
        parser.add_argument(
            '--with-images',
            action='store_true',
            help='Загружать реальные изображения через Unsplash API'
        )

    def handle(self, *args, **options):
        self.stdout.write('Начинаем генерацию реалистичных тестовых данных...')
        
        with transaction.atomic():
            # Очищаем существующие данные
            self.clear_data()
            
            # Создаем базовые данные
            self.create_categories(options['categories'])
            self.create_tags()
            self.create_shops()
            self.create_sellers(options['sellers'])
            self.create_products(options['products'], options['with_images'])
            self.create_reviews(options['reviews'])
            self.create_orders(options['orders'])
            self.create_carts()

        self.stdout.write(
            self.style.SUCCESS('Реалистичные тестовые данные успешно созданы!')
        )

    def clear_data(self):
        """Очищает существующие данные"""
        self.stdout.write('Очищаем существующие данные...')
        ProductImage.objects.all().delete()
        ProductCharacteristic.objects.all().delete()
        CartItem.objects.all().delete()
        Cart.objects.all().delete()
        OrderItem.objects.all().delete()
        Order.objects.all().delete()
        Review.objects.all().delete()
        Product.objects.all().delete()
        Seller.objects.all().delete()
        Tag.objects.all().delete()
        Shop.objects.all().delete()
        Category.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()

    def create_categories(self, count):
        """Создает категории товаров"""
        categories_data = [
            {
                'ru': {'name': 'Смартфоны и телефоны', 'description': 'Мобильные устройства и аксессуары'},
                'en': {'name': 'Smartphones & Phones', 'description': 'Mobile devices and accessories'},
                'ar': {'name': 'الهواتف الذكية والهواتف', 'description': 'الأجهزة المحمولة والملحقات'},
                'icon': 'mobile-alt',
                'slug': 'smartphones'
            },
            {
                'ru': {'name': 'Ноутбуки и компьютеры', 'description': 'Компьютерная техника и периферия'},
                'en': {'name': 'Laptops & Computers', 'description': 'Computer equipment and peripherals'},
                'ar': {'name': 'أجهزة الكمبيوتر المحمولة وأجهزة الكمبيوتر', 'description': 'معدات الكمبيوتر والملحقات'},
                'icon': 'laptop',
                'slug': 'laptops'
            },
            {
                'ru': {'name': 'Одежда для мужчин', 'description': 'Мужская одежда и аксессуары'},
                'en': {'name': 'Men\'s Clothing', 'description': 'Men\'s clothing and accessories'},
                'ar': {'name': 'ملابس الرجال', 'description': 'ملابس وإكسسوارات الرجال'},
                'icon': 'tshirt',
                'slug': 'mens-clothing'
            },
            {
                'ru': {'name': 'Одежда для женщин', 'description': 'Женская одежда и аксессуары'},
                'en': {'name': 'Women\'s Clothing', 'description': 'Women\'s clothing and accessories'},
                'ar': {'name': 'ملابس النساء', 'description': 'ملابس وإكسسوارات النساء'},
                'icon': 'female',
                'slug': 'womens-clothing'
            },
            {
                'ru': {'name': 'Дом и интерьер', 'description': 'Товары для дома и декора'},
                'en': {'name': 'Home & Interior', 'description': 'Home goods and decor'},
                'ar': {'name': 'المنزل والديكور', 'description': 'سلع المنزل والديكور'},
                'icon': 'home',
                'slug': 'home-interior'
            },
            {
                'ru': {'name': 'Спорт и фитнес', 'description': 'Спортивные товары и оборудование'},
                'en': {'name': 'Sports & Fitness', 'description': 'Sports goods and equipment'},
                'ar': {'name': 'الرياضة واللياقة البدنية', 'description': 'البضائع الرياضية والمعدات'},
                'icon': 'dumbbell',
                'slug': 'sports-fitness'
            },
            {
                'ru': {'name': 'Красота и здоровье', 'description': 'Косметика и товары для здоровья'},
                'en': {'name': 'Beauty & Health', 'description': 'Cosmetics and health products'},
                'ar': {'name': 'الجمال والصحة', 'description': 'مستحضرات التجميل ومنتجات الصحة'},
                'icon': 'spa',
                'slug': 'beauty-health'
            },
            {
                'ru': {'name': 'Книги и медиа', 'description': 'Книги, фильмы, музыка'},
                'en': {'name': 'Books & Media', 'description': 'Books, movies, music'},
                'ar': {'name': 'الكتب والوسائط', 'description': 'الكتب والأفلام والموسيقى'},
                'icon': 'book',
                'slug': 'books-media'
            },
            {
                'ru': {'name': 'Автомобили и мотоциклы', 'description': 'Автомобили, мотоциклы, запчасти'},
                'en': {'name': 'Cars & Motorcycles', 'description': 'Cars, motorcycles, parts'},
                'ar': {'name': 'السيارات والدراجات النارية', 'description': 'السيارات والدراجات النارية وقطع الغيار'},
                'icon': 'car',
                'slug': 'cars-motorcycles'
            },
            {
                'ru': {'name': 'Детские товары', 'description': 'Товары для детей и игрушки'},
                'en': {'name': 'Kids & Baby', 'description': 'Children\'s goods and toys'},
                'ar': {'name': 'سلع الأطفال', 'description': 'سلع الأطفال والألعاب'},
                'icon': 'baby',
                'slug': 'kids-baby'
            }
        ]
        
        for i, data in enumerate(categories_data[:count]):
            category = Category()
            for lang_code, lang_data in data.items():
                if lang_code in ['ru', 'en', 'ar']:
                    category.set_current_language(lang_code)
                    category.name = lang_data['name']
                    category.description = lang_data['description']
            category.slug = data['slug']
            category.icon = data['icon']
            category.is_active = True
            category.sort_order = i
            category.save()
            self.stdout.write(f'Создана категория: {category.name}')

    def create_tags(self):
        """Создает теги товаров"""
        tags_data = [
            {'ru': 'Новинка', 'en': 'New', 'ar': 'جديد', 'color': '#FF6B35'},
            {'ru': 'Хит продаж', 'en': 'Best Seller', 'ar': 'الأكثر مبيعاً', 'color': '#FFD700'},
            {'ru': 'Скидка', 'en': 'Sale', 'ar': 'خصم', 'color': '#FF0000'},
            {'ru': 'Премиум', 'en': 'Premium', 'ar': 'متميز', 'color': '#8B4513'},
            {'ru': 'Экологичный', 'en': 'Eco-friendly', 'ar': 'صديق للبيئة', 'color': '#00FF00'},
            {'ru': 'Ограниченная серия', 'en': 'Limited Edition', 'ar': 'إصدار محدود', 'color': '#800080'},
            {'ru': 'Быстрая доставка', 'en': 'Fast Delivery', 'ar': 'توصيل سريع', 'color': '#00BFFF'},
            {'ru': 'Гарантия качества', 'en': 'Quality Guarantee', 'ar': 'ضمان الجودة', 'color': '#32CD32'},
        ]
        
        for data in tags_data:
            tag = Tag()
            for lang_code, name in data.items():
                if lang_code in ['ru', 'en', 'ar']:
                    tag.set_current_language(lang_code)
                    tag.name = name
            tag.color = data['color']
            tag.save()
            self.stdout.write(f'Создан тег: {tag.name}')

    def create_shops(self):
        """Создает магазины"""
        shops_data = [
            {
                'ru': {'name': 'ТехноМир', 'address': 'ул. Ленина, 10, Москва', 'city': 'Москва'},
                'en': {'name': 'TechnoWorld', 'address': 'Lenin St, 10, Moscow', 'city': 'Moscow'},
                'ar': {'name': 'عالم التكنولوجيا', 'address': 'شارع لينين، 10، موسكو', 'city': 'موسكو'},
                'coords': (55.7558, 37.6173)
            },
            {
                'ru': {'name': 'Модный дом', 'address': 'пр. Невский, 25, Санкт-Петербург', 'city': 'Санкт-Петербург'},
                'en': {'name': 'Fashion House', 'address': 'Nevsky Ave, 25, St. Petersburg', 'city': 'St. Petersburg'},
                'ar': {'name': 'دار الأزياء', 'address': 'شارع نيفسكي، 25، سانت بطرسبرغ', 'city': 'سانت بطرسبرغ'},
                'coords': (59.9311, 30.3609)
            },
            {
                'ru': {'name': 'СпортМакс', 'address': 'ул. Красная, 5, Казань', 'city': 'Казань'},
                'en': {'name': 'SportMax', 'address': 'Krasnaya St, 5, Kazan', 'city': 'Kazan'},
                'ar': {'name': 'سبورت ماكس', 'address': 'شارع كراسنايا، 5، قازان', 'city': 'قازان'},
                'coords': (55.8304, 49.0661)
            },
            {
                'ru': {'name': 'Дом и сад', 'address': 'ул. Мира, 15, Екатеринбург', 'city': 'Екатеринбург'},
                'en': {'name': 'Home & Garden', 'address': 'Mira St, 15, Yekaterinburg', 'city': 'Yekaterinburg'},
                'ar': {'name': 'المنزل والحديقة', 'address': 'شارع ميرا، 15، يكاترينبورغ', 'city': 'يكاترينبورغ'},
                'coords': (56.8431, 60.6454)
            },
            {
                'ru': {'name': 'Красота+', 'address': 'ул. Пушкина, 8, Новосибирск', 'city': 'Новосибирск'},
                'en': {'name': 'Beauty+', 'address': 'Pushkin St, 8, Novosibirsk', 'city': 'Novosibirsk'},
                'ar': {'name': 'الجمال+', 'address': 'شارع بوشكين، 8، نوفوسيبيرسك', 'city': 'نوفوسيبيرسك'},
                'coords': (55.0084, 82.9357)
            }
        ]
        
        for data in shops_data:
            shop = Shop()
            for lang_code, shop_data in data.items():
                if lang_code in ['ru', 'en', 'ar']:
                    shop.set_current_language(lang_code)
                    shop.name = shop_data['name']
                    shop.address = shop_data['address']
                    shop.city = shop_data['city']
            shop.latitude = data['coords'][0]
            shop.longitude = data['coords'][1]
            shop.phone = f"+7{random.randint(9000000000, 9999999999)}"
            shop.email = f"info@{shop.name.lower().replace(' ', '')}.ru"
            shop.is_active = True
            shop.save()
            self.stdout.write(f'Создан магазин: {shop.name}')

    def create_sellers(self, count):
        """Создает продавцов"""
        company_names = [
            'ООО "ТехноПро"', 'ИП Иванов', 'ООО "МодаСтиль"', 'ИП Петров',
            'ООО "СпортГир"', 'ИП Сидоров', 'ООО "ДомТовар"', 'ИП Козлов',
            'ООО "Красота+"', 'ИП Морозов', 'ООО "КнигиМир"', 'ИП Волков',
            'ООО "АвтоМир"', 'ИП Соколов', 'ООО "Детки"', 'ИП Лебедев',
            'ООО "Продукты+"', 'ИП Орлов', 'ООО "ПромТех"', 'ИП Новиков'
        ]
        
        for i in range(count):
            # Создаем пользователя-продавца
            user = User.objects.create_user(
                username=f'seller_{i+1}',
                email=f'seller{i+1}@example.com',
                password='password123',
                role='seller',
                first_name=f'Продавец{i+1}',
                last_name='Тестовый',
                phone_number=f'+7{random.randint(9000000000, 9999999999)}'
            )
            
            # Создаем профиль продавца
            seller = Seller.objects.create(
                user=user,
                company_name=company_names[i % len(company_names)],
                description=f'Описание компании продавца {i+1}',
                commission_rate=Decimal(random.uniform(3.0, 15.0)),
                is_verified=random.choice([True, False])
            )
            
            self.stdout.write(f'Создан продавец: {seller.company_name}')

    def create_products(self, count, with_images=False):
        """Создает товары"""
        categories = list(Category.objects.all())
        sellers = list(Seller.objects.all())
        tags = list(Tag.objects.all())
        shops = list(Shop.objects.all())
        
        product_templates = [
            {
                'ru': {'name': 'Смартфон', 'description': 'Современный смартфон с отличными характеристиками'},
                'en': {'name': 'Smartphone', 'description': 'Modern smartphone with excellent specifications'},
                'ar': {'name': 'هاتف ذكي', 'description': 'هاتف ذكي حديث بمواصفات ممتازة'},
                'price_range': (15000, 80000),
                'keywords': ['smartphone', 'mobile', 'phone']
            },
            {
                'ru': {'name': 'Ноутбук', 'description': 'Производительный ноутбук для работы и учебы'},
                'en': {'name': 'Laptop', 'description': 'Powerful laptop for work and study'},
                'ar': {'name': 'كمبيوتر محمول', 'description': 'كمبيوتر محمول قوي للعمل والدراسة'},
                'price_range': (30000, 150000),
                'keywords': ['laptop', 'computer', 'notebook']
            },
            {
                'ru': {'name': 'Футболка', 'description': 'Удобная футболка из качественного хлопка'},
                'en': {'name': 'T-shirt', 'description': 'Comfortable t-shirt made of quality cotton'},
                'ar': {'name': 'قميص', 'description': 'قميص مريح مصنوع من القطن عالي الجودة'},
                'price_range': (500, 3000),
                'keywords': ['t-shirt', 'clothing', 'cotton']
            },
            {
                'ru': {'name': 'Кроссовки', 'description': 'Спортивные кроссовки для активного образа жизни'},
                'en': {'name': 'Sneakers', 'description': 'Sports sneakers for an active lifestyle'},
                'ar': {'name': 'أحذية رياضية', 'description': 'أحذية رياضية لنمط حياة نشط'},
                'price_range': (2000, 15000),
                'keywords': ['sneakers', 'shoes', 'sports']
            },
            {
                'ru': {'name': 'Стул', 'description': 'Удобный стул для офиса и дома'},
                'en': {'name': 'Chair', 'description': 'Comfortable chair for office and home'},
                'ar': {'name': 'كرسي', 'description': 'كرسي مريح للمكتب والمنزل'},
                'price_range': (3000, 25000),
                'keywords': ['chair', 'furniture', 'office']
            }
        ]
        
        for i in range(count):
            # Выбираем случайные данные
            category = random.choice(categories)
            seller = random.choice(sellers)
            template = random.choice(product_templates)
            
            # Создаем товар
            product = Product()
            for lang_code, lang_data in template.items():
                if lang_code in ['ru', 'en', 'ar']:
                    product.set_current_language(lang_code)
                    product.name = f"{lang_data['name']} {i+1}"
                    product.description = f"{lang_data['description']} {i+1}"
            
            # Устанавливаем цену
            min_price, max_price = template['price_range']
            product.price = Decimal(random.uniform(min_price, max_price))
            
            # Добавляем скидку в 30% случаев
            if random.random() < 0.3:
                product.discount_price = product.price * Decimal(random.uniform(0.7, 0.9))
            
            product.currency = 'RUB'
            product.category = category
            product.seller = seller
            product.stock_quantity = random.randint(0, 100)
            product.is_active = random.choice([True, True, True, False])  # 75% активных
            product.save()
            
            # Добавляем магазины
            product.shops.set(random.sample(shops, random.randint(1, 3)))
            
            # Добавляем теги
            product.tags.set(random.sample(tags, random.randint(1, 3)))
            
            # Создаем характеристики
            self.create_product_characteristics(product)
            
            # Загружаем изображения если нужно
            if with_images and settings.UNSPLASH_ACCESS_KEY:
                self.load_product_images(product, template['keywords'])
            
            self.stdout.write(f'Создан товар: {product.name}')

    def create_product_characteristics(self, product):
        """Создает характеристики для товара"""
        characteristics = [
            ('Цвет', random.choice(['Черный', 'Белый', 'Красный', 'Синий', 'Зеленый', 'Серый'])),
            ('Материал', random.choice(['Пластик', 'Металл', 'Дерево', 'Ткань', 'Кожа', 'Резина'])),
            ('Размер', random.choice(['S', 'M', 'L', 'XL', 'XXL', 'Универсальный'])),
            ('Вес', f"{random.uniform(0.1, 10.0):.1f} кг"),
            ('Страна производства', random.choice(['Россия', 'Китай', 'Германия', 'Япония', 'США', 'Корея'])),
            ('Гарантия', f"{random.randint(6, 36)} месяцев"),
            ('Бренд', random.choice(['Samsung', 'Apple', 'Nike', 'Adidas', 'IKEA', 'Zara'])),
        ]
        
        for j, (name, value) in enumerate(characteristics[:random.randint(3, 6)]):
            ProductCharacteristic.objects.create(
                product=product,
                name=name,
                value=value,
                order=j
            )

    def load_product_images(self, product, keywords):
        """Загружает изображения для товара через Unsplash API"""
        try:
            for i in range(random.randint(1, 3)):  # 1-3 изображения
                keyword = random.choice(keywords)
                
                # Запрашиваем изображение через Unsplash API
                url = f"https://api.unsplash.com/photos/random"
                params = {
                    'query': keyword,
                    'w': 800,
                    'h': 600,
                    'fit': 'crop',
                    'client_id': settings.UNSPLASH_ACCESS_KEY
                }
                
                response = requests.get(url, params=params, timeout=10)
                response.raise_for_status()
                
                data = response.json()
                image_url = data['urls']['regular']
                
                # Загружаем изображение
                img_response = requests.get(image_url, timeout=10)
                img_response.raise_for_status()
                
                # Обрабатываем изображение
                image = Image.open(io.BytesIO(img_response.content))
                
                # Конвертируем в RGB если нужно
                if image.mode in ('RGBA', 'LA', 'P'):
                    image = image.convert('RGB')
                
                # Изменяем размер
                image = image.resize((800, 600), Image.Resampling.LANCZOS)
                
                # Сохраняем в BytesIO
                img_io = io.BytesIO()
                image.save(img_io, format='JPEG', quality=85)
                img_io.seek(0)
                
                # Создаем ProductImage
                from django.core.files.base import ContentFile
                image_file = ContentFile(img_io.getvalue(), name=f"{product.sku}_{i+1}.jpg")
                
                ProductImage.objects.create(
                    product=product,
                    image=image_file,
                    alt_text=f"{product.name} - изображение {i+1}",
                    is_primary=(i == 0),
                    order=i
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f'Не удалось загрузить изображения для {product.name}: {str(e)}')
            )

    def create_reviews(self, count):
        """Создает отзывы"""
        products = list(Product.objects.all())
        
        # Создаем пользователей-покупателей если их нет
        users = list(User.objects.filter(role='user'))
        if not users:
            for i in range(10):
                user = User.objects.create_user(
                    username=f'buyer_{i+1}',
                    email=f'buyer{i+1}@example.com',
                    password='password123',
                    role='user',
                    first_name=f'Покупатель{i+1}',
                    last_name='Тестовый'
                )
                users.append(user)
        
        review_templates = [
            {
                'ru': {
                    'titles': ['Отличный товар!', 'Рекомендую!', 'Качество на высоте', 'Быстрая доставка', 'Соответствует описанию'],
                    'texts': [
                        'Очень доволен покупкой. Качество отличное, доставка быстрая. Рекомендую!',
                        'Товар соответствует описанию. Упаковка аккуратная. Спасибо продавцу!',
                        'Заказывал уже не первый раз. Всегда качественные товары и быстрая доставка.',
                        'Отличное соотношение цена-качество. Буду заказывать еще!',
                        'Товар пришел в срок, упаковка целая. Качество хорошее, рекомендую!'
                    ]
                }
            }
        ]
        
        for i in range(count):
            product = random.choice(products)
            user = random.choice(users)
            
            # Проверяем, что пользователь еще не оставлял отзыв на этот товар
            if Review.objects.filter(product=product, user=user).exists():
                continue
            
            template = random.choice(review_templates)
            title = random.choice(template['ru']['titles'])
            text = random.choice(template['ru']['texts'])
            
            review = Review.objects.create(
                user=user,
                product=product,
                rating=random.randint(1, 5),
                title=title,
                text=text,
                is_verified_purchase=random.choice([True, False]),
                is_moderated=random.choice([True, True, True, False])  # 75% промодерированных
            )
            
            self.stdout.write(f'Создан отзыв: {review.title}')

    def create_orders(self, count):
        """Создает заказы"""
        users = list(User.objects.filter(role='user'))
        products = list(Product.objects.all())
        
        if not users:
            self.stdout.write('Нет пользователей для создания заказов')
            return
        
        for i in range(count):
            user = random.choice(users)
            
            # Создаем заказ
            order = Order.objects.create(
                user=user,
                status=random.choice(['pending', 'confirmed', 'processing', 'shipped', 'delivered']),
                payment_status=random.choice(['pending', 'paid', 'failed']),
                total_amount=Decimal('0.00'),
                shipping_cost=Decimal(random.uniform(0, 500)),
                discount_amount=Decimal(random.uniform(0, 1000)),
                shipping_address=f"Адрес доставки {i+1}, г. Москва, ул. Тестовая, д. {i+1}",
                notes=f"Примечания к заказу {i+1}"
            )
            
            # Создаем позиции заказа
            order_products = random.sample(products, random.randint(1, 5))
            total_amount = Decimal('0.00')
            
            for product in order_products:
                quantity = random.randint(1, 3)
                price = product.final_price
                total_price = price * quantity
                
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    price=price,
                    total_price=total_price
                )
                
                total_amount += total_price
            
            # Обновляем общую сумму заказа
            order.total_amount = total_amount + order.shipping_cost - order.discount_amount
            order.save()
            
            self.stdout.write(f'Создан заказ: {order.order_number}')

    def create_carts(self):
        """Создает корзины для пользователей"""
        users = list(User.objects.filter(role='user'))
        products = list(Product.objects.all())
        
        for user in users:
            cart, created = Cart.objects.get_or_create(user=user)
            
            if created:
                # Добавляем случайные товары в корзину
                cart_products = random.sample(products, random.randint(0, 5))
                
                for product in cart_products:
                    CartItem.objects.create(
                        cart=cart,
                        product=product,
                        quantity=random.randint(1, 3)
                    )
                
                self.stdout.write(f'Создана корзина для пользователя: {user.username}')
