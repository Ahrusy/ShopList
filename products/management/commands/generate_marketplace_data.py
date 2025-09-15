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
from products.models import (
    Category, Shop, Tag, Product, ProductImage, ProductCharacteristic,
    Seller, Order, OrderItem, Review, Cart, CartItem, Commission
)

User = get_user_model()


class Command(BaseCommand):
    help = 'Генерирует тестовые данные для маркетплейса'

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

    def handle(self, *args, **options):
        self.stdout.write('Начинаем генерацию тестовых данных...')
        
        with transaction.atomic():
            # Создаем категории
            self.create_categories(options['categories'])
            
            # Создаем теги
            self.create_tags()
            
            # Создаем магазины
            self.create_shops()
            
            # Создаем продавцов
            self.create_sellers(options['sellers'])
            
            # Создаем товары
            self.create_products(options['products'])
            
            # Создаем отзывы
            self.create_reviews(options['reviews'])
            
            # Создаем заказы
            self.create_orders(options['orders'])
            
            # Создаем корзины для пользователей
            self.create_carts()

        self.stdout.write(
            self.style.SUCCESS('Тестовые данные успешно созданы!')
        )

    def create_categories(self, count):
        """Создает категории товаров"""
        categories_data = [
            {'ru': 'Электроника', 'en': 'Electronics', 'ar': 'إلكترونيات'},
            {'ru': 'Одежда и обувь', 'en': 'Clothing & Shoes', 'ar': 'الملابس والأحذية'},
            {'ru': 'Дом и сад', 'en': 'Home & Garden', 'ar': 'المنزل والحديقة'},
            {'ru': 'Спорт и отдых', 'en': 'Sports & Recreation', 'ar': 'الرياضة والترفيه'},
            {'ru': 'Красота и здоровье', 'en': 'Beauty & Health', 'ar': 'الجمال والصحة'},
            {'ru': 'Книги и медиа', 'en': 'Books & Media', 'ar': 'الكتب والوسائط'},
            {'ru': 'Автомобили', 'en': 'Automotive', 'ar': 'السيارات'},
            {'ru': 'Детские товары', 'en': 'Kids & Baby', 'ar': 'أطفال ورضع'},
            {'ru': 'Продукты питания', 'en': 'Food & Grocery', 'ar': 'الطعام والبقالة'},
            {'ru': 'Промышленность', 'en': 'Industrial', 'ar': 'الصناعة'},
        ]
        
        for i, data in enumerate(categories_data[:count]):
            category = Category()
            for lang_code, name in data.items():
                category.set_current_language(lang_code)
                category.name = name
                category.slug = f"category-{i+1}-{lang_code}"
            category.save()
            self.stdout.write(f'Создана категория: {category.name}')

    def create_tags(self):
        """Создает теги товаров"""
        tags_data = [
            {'ru': 'Новинка', 'en': 'New', 'ar': 'جديد'},
            {'ru': 'Хит продаж', 'en': 'Best Seller', 'ar': 'الأكثر مبيعاً'},
            {'ru': 'Скидка', 'en': 'Sale', 'ar': 'خصم'},
            {'ru': 'Премиум', 'en': 'Premium', 'ar': 'متميز'},
            {'ru': 'Экологичный', 'en': 'Eco-friendly', 'ar': 'صديق للبيئة'},
            {'ru': 'Ограниченная серия', 'en': 'Limited Edition', 'ar': 'إصدار محدود'},
            {'ru': 'Быстрая доставка', 'en': 'Fast Delivery', 'ar': 'توصيل سريع'},
            {'ru': 'Гарантия качества', 'en': 'Quality Guarantee', 'ar': 'ضمان الجودة'},
        ]
        
        for data in tags_data:
            tag = Tag()
            for lang_code, name in data.items():
                tag.set_current_language(lang_code)
                tag.name = name
            tag.save()
            self.stdout.write(f'Создан тег: {tag.name}')

    def create_shops(self):
        """Создает магазины"""
        shops_data = [
            {
                'ru': {'name': 'ТехноМир', 'address': 'ул. Ленина, 10', 'city': 'Москва'},
                'en': {'name': 'TechnoWorld', 'address': 'Lenin St, 10', 'city': 'Moscow'},
                'ar': {'name': 'عالم التكنولوجيا', 'address': 'شارع لينين، 10', 'city': 'موسكو'},
                'coords': (55.7558, 37.6173)
            },
            {
                'ru': {'name': 'Модный дом', 'address': 'пр. Невский, 25', 'city': 'Санкт-Петербург'},
                'en': {'name': 'Fashion House', 'address': 'Nevsky Ave, 25', 'city': 'St. Petersburg'},
                'ar': {'name': 'دار الأزياء', 'address': 'شارع نيفسكي، 25', 'city': 'سانت بطرسبرغ'},
                'coords': (59.9311, 30.3609)
            },
            {
                'ru': {'name': 'СпортМакс', 'address': 'ул. Красная, 5', 'city': 'Казань'},
                'en': {'name': 'SportMax', 'address': 'Krasnaya St, 5', 'city': 'Kazan'},
                'ar': {'name': 'سبورت ماكس', 'address': 'شارع كراسنايا، 5', 'city': 'قازان'},
                'coords': (55.8304, 49.0661)
            },
            {
                'ru': {'name': 'Дом и сад', 'address': 'ул. Мира, 15', 'city': 'Екатеринбург'},
                'en': {'name': 'Home & Garden', 'address': 'Mira St, 15', 'city': 'Yekaterinburg'},
                'ar': {'name': 'المنزل والحديقة', 'address': 'شارع ميرا، 15', 'city': 'يكاترينبورغ'},
                'coords': (56.8431, 60.6454)
            },
            {
                'ru': {'name': 'Красота+', 'address': 'ул. Пушкина, 8', 'city': 'Новосибирск'},
                'en': {'name': 'Beauty+', 'address': 'Pushkin St, 8', 'city': 'Novosibirsk'},
                'ar': {'name': 'الجمال+', 'address': 'شارع بوشكين، 8', 'city': 'نوفوسيبيرسك'},
                'coords': (55.0084, 82.9357)
            }
        ]
        
        for data in shops_data:
            shop = Shop()
            for lang_code, shop_data in data.items():
                if lang_code != 'coords':
                    shop.set_current_language(lang_code)
                    shop.name = shop_data['name']
                    shop.address = shop_data['address']
                    shop.city = shop_data['city']
            shop.latitude = data['coords'][0]
            shop.longitude = data['coords'][1]
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

    def create_products(self, count):
        """Создает товары"""
        categories = list(Category.objects.all())
        sellers = list(Seller.objects.all())
        tags = list(Tag.objects.all())
        shops = list(Shop.objects.all())
        
        product_names = [
            {'ru': 'Смартфон', 'en': 'Smartphone', 'ar': 'هاتف ذكي'},
            {'ru': 'Ноутбук', 'en': 'Laptop', 'ar': 'كمبيوتر محمول'},
            {'ru': 'Планшет', 'en': 'Tablet', 'ar': 'جهاز لوحي'},
            {'ru': 'Наушники', 'en': 'Headphones', 'ar': 'سماعات'},
            {'ru': 'Футболка', 'en': 'T-shirt', 'ar': 'قميص'},
            {'ru': 'Джинсы', 'en': 'Jeans', 'ar': 'جينز'},
            {'ru': 'Кроссовки', 'en': 'Sneakers', 'ar': 'أحذية رياضية'},
            {'ru': 'Куртка', 'en': 'Jacket', 'ar': 'سترة'},
            {'ru': 'Стул', 'en': 'Chair', 'ar': 'كرسي'},
            {'ru': 'Стол', 'en': 'Table', 'ar': 'طاولة'},
            {'ru': 'Лампа', 'en': 'Lamp', 'ar': 'مصباح'},
            {'ru': 'Книга', 'en': 'Book', 'ar': 'كتاب'},
            {'ru': 'Игрушка', 'en': 'Toy', 'ar': 'لعبة'},
            {'ru': 'Велосипед', 'en': 'Bicycle', 'ar': 'دراجة'},
            {'ru': 'Мяч', 'en': 'Ball', 'ar': 'كرة'},
        ]
        
        for i in range(count):
            # Выбираем случайные данные
            category = random.choice(categories)
            seller = random.choice(sellers)
            product_name = random.choice(product_names)
            
            # Создаем товар
            product = Product()
            for lang_code, name in product_name.items():
                product.set_current_language(lang_code)
                product.name = f"{name} {i+1}"
                product.description = f"Описание товара {name} {i+1}"
            
            product.price = Decimal(random.uniform(100, 50000))
            if random.choice([True, False]):
                product.discount_price = product.price * Decimal(random.uniform(0.7, 0.9))
            
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
            characteristics = [
                ('Цвет', random.choice(['Черный', 'Белый', 'Красный', 'Синий', 'Зеленый'])),
                ('Материал', random.choice(['Пластик', 'Металл', 'Дерево', 'Ткань', 'Кожа'])),
                ('Размер', random.choice(['S', 'M', 'L', 'XL', 'XXL'])),
                ('Вес', f"{random.uniform(0.1, 10.0):.1f} кг"),
                ('Страна производства', random.choice(['Россия', 'Китай', 'Германия', 'Япония', 'США'])),
            ]
            
            for j, (name, value) in enumerate(characteristics[:random.randint(2, 5)]):
                ProductCharacteristic.objects.create(
                    product=product,
                    name=name,
                    value=value,
                    order=j
                )
            
            # Создаем изображения (заглушки)
            for j in range(random.randint(1, 3)):
                ProductImage.objects.create(
                    product=product,
                    alt_text=f"Изображение {product.name} {j+1}",
                    order=j
                )
            
            self.stdout.write(f'Создан товар: {product.name}')

    def create_reviews(self, count):
        """Создает отзывы"""
        products = list(Product.objects.all())
        users = list(User.objects.filter(role='user'))
        
        # Создаем пользователей-покупателей если их нет
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
        
        for i in range(count):
            product = random.choice(products)
            user = random.choice(users)
            
            # Проверяем, что пользователь еще не оставлял отзыв на этот товар
            if Review.objects.filter(product=product, user=user).exists():
                continue
            
            review = Review.objects.create(
                user=user,
                product=product,
                rating=random.randint(1, 5),
                title=f"Отзыв о товаре {product.name}",
                text=f"Очень хороший товар! Рекомендую к покупке. Качество на высоте.",
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
