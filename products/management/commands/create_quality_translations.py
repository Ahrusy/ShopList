from django.core.management.base import BaseCommand
from products.models import Category, Product, Shop, Tag
import random


class Command(BaseCommand):
    help = 'Create quality Russian translations for main categories and products'

    def handle(self, *args, **options):
        self.stdout.write('Creating quality Russian translations...')
        
        # Создаем качественные переводы для основных категорий
        self.create_main_category_translations()
        
        # Создаем переводы для товаров
        self.create_product_translations()
        
        self.stdout.write(self.style.SUCCESS('Successfully created quality translations'))

    def create_main_category_translations(self):
        """Создает переводы для основных категорий"""
        
        # Основные категории с их подкатегориями
        main_categories = {
            'electronics': {
                'name': 'Электроника',
                'description': 'Современная электроника и гаджеты',
                'subcategories': {
                    'smartphones': 'Смартфоны',
                    'laptops': 'Ноутбуки',
                    'tablets': 'Планшеты',
                    'headphones': 'Наушники',
                    'cameras': 'Фотокамеры',
                    'gaming': 'Игровые консоли',
                    'accessories': 'Аксессуары'
                }
            },
            'clothing': {
                'name': 'Одежда и обувь',
                'description': 'Модная одежда для всей семьи',
                'subcategories': {
                    'mens': 'Мужская одежда',
                    'womens': 'Женская одежда',
                    'kids': 'Детская одежда',
                    'shoes': 'Обувь',
                    'accessories': 'Аксессуары',
                    'bags': 'Сумки и рюкзаки'
                }
            },
            'beauty': {
                'name': 'Красота и здоровье',
                'description': 'Косметика, парфюмерия и товары для здоровья',
                'subcategories': {
                    'skincare': 'Уход за кожей',
                    'makeup': 'Декоративная косметика',
                    'perfume': 'Парфюмерия',
                    'haircare': 'Уход за волосами',
                    'health': 'Здоровье'
                }
            },
            'sports': {
                'name': 'Спорт и отдых',
                'description': 'Спортивные товары и товары для активного отдыха',
                'subcategories': {
                    'fitness': 'Фитнес',
                    'outdoor': 'Активный отдых',
                    'team-sports': 'Командные виды спорта',
                    'water-sports': 'Водные виды спорта',
                    'winter-sports': 'Зимние виды спорта'
                }
            },
            'home': {
                'name': 'Дом и сад',
                'description': 'Товары для дома, сада и дачи',
                'subcategories': {
                    'furniture': 'Мебель',
                    'decor': 'Декор',
                    'kitchen': 'Кухонные принадлежности',
                    'garden': 'Сад и огород',
                    'tools': 'Инструменты'
                }
            },
            'auto': {
                'name': 'Автотовары',
                'description': 'Автомобильные товары и аксессуары',
                'subcategories': {
                    'parts': 'Запчасти',
                    'accessories': 'Аксессуары',
                    'oils': 'Масла и жидкости',
                    'tires': 'Шины и диски',
                    'electronics': 'Автоэлектроника'
                }
            }
        }
        
        # Обновляем переводы категорий
        categories = Category.objects.all()
        
        for category in categories:
            russian_name = self.get_category_translation(category.slug, main_categories)
            
            try:
                translation, created = category.translations.get_or_create(
                    language_code='ru',
                    defaults={
                        'name': russian_name,
                        'description': f'Категория {russian_name}'
                    }
                )
                
                if not created:
                    translation.name = russian_name
                    translation.description = f'Категория {russian_name}'
                    translation.save()
                
                self.stdout.write(f'Updated category: {category.slug} -> {russian_name}')
                
            except Exception as e:
                self.stdout.write(f'Error updating category {category.slug}: {str(e)}')

    def get_category_translation(self, slug, main_categories):
        """Получает русский перевод для категории"""
        
        # Проверяем основные категории
        for key, data in main_categories.items():
            if key in slug.lower():
                return data['name']
        
        # Специальные переводы
        special_translations = {
            'iphone': 'iPhone',
            'samsung': 'Samsung',
            'xiaomi': 'Xiaomi',
            'huawei': 'Huawei',
            'playstation': 'PlayStation',
            'xbox': 'Xbox',
            'nintendo': 'Nintendo',
            'books': 'Книги',
            'food': 'Продукты питания',
            'pets': 'Товары для животных',
            'bytovaya-tehnika': 'Бытовая техника',
            'krasota-i-zdorove': 'Красота и здоровье',
            'odezhda': 'Одежда',
            'sport-i-otdyh': 'Спорт и отдых'
        }
        
        for key, translation in special_translations.items():
            if key in slug:
                return translation
        
        # Если не найдено, создаем на основе slug
        return self.slug_to_russian_name(slug)

    def slug_to_russian_name(self, slug):
        """Преобразует slug в русское название"""
        # Убираем технические части
        clean_slug = slug.replace('category-', '').split('-category-')[0]
        
        # Базовые переводы
        word_translations = {
            'electronics': 'Электроника',
            'clothing': 'Одежда',
            'beauty': 'Красота',
            'sports': 'Спорт',
            'home': 'Дом',
            'garden': 'Сад',
            'auto': 'Авто',
            'books': 'Книги',
            'food': 'Еда',
            'pets': 'Животные',
            'kids': 'Детские товары',
            'mens': 'Мужское',
            'womens': 'Женское',
            'accessories': 'Аксессуары'
        }
        
        # Пытаемся найти перевод
        for eng, rus in word_translations.items():
            if eng in clean_slug:
                return rus
        
        # Если ничего не найдено, делаем красивое название
        words = clean_slug.replace('-', ' ').split()
        filtered_words = [word.capitalize() for word in words if len(word) > 2 and not word.isdigit()]
        
        if filtered_words:
            return ' '.join(filtered_words)
        else:
            return 'Категория товаров'

    def create_product_translations(self):
        """Создает переводы для товаров"""
        
        product_names = {
            'electronics': [
                'Смартфон Apple iPhone 15 Pro', 'Samsung Galaxy S24 Ultra', 'Xiaomi Redmi Note 13',
                'Ноутбук MacBook Air M2', 'Asus ROG Gaming Laptop', 'Lenovo ThinkPad X1',
                'Наушники AirPods Pro', 'Sony WH-1000XM5', 'JBL Tune 760NC',
                'Планшет iPad Air', 'Samsung Galaxy Tab S9', 'Huawei MatePad Pro'
            ],
            'clothing': [
                'Футболка хлопковая мужская', 'Джинсы классические женские', 'Куртка зимняя детская',
                'Платье летнее', 'Рубашка деловая', 'Свитер вязаный', 'Брюки спортивные',
                'Кроссовки Nike Air Max', 'Ботинки кожаные', 'Сапоги зимние'
            ],
            'beauty': [
                'Крем для лица увлажняющий', 'Шампунь для всех типов волос', 'Помада матовая',
                'Тушь для ресниц', 'Духи женские 50мл', 'Лосьон для тела', 'Маска для лица',
                'Сыворотка антивозрастная', 'Бальзам для губ', 'Скраб для тела'
            ],
            'sports': [
                'Гантели разборные 20кг', 'Коврик для йоги', 'Мяч футбольный', 'Ракетка теннисная',
                'Велосипед горный', 'Лыжи беговые', 'Форма спортивная', 'Кроссовки для бега',
                'Рюкзак туристический', 'Палатка 2-местная'
            ],
            'home': [
                'Подушка ортопедическая', 'Одеяло пуховое', 'Ваза декоративная', 'Светильник настольный',
                'Картина на холсте', 'Зеркало настенное', 'Часы настенные', 'Шторы блэкаут',
                'Ковер персидский', 'Растение комнатное'
            ],
            'auto': [
                'Шины летние R16', 'Масло моторное 5W-30', 'Фильтр воздушный', 'Аккумулятор 60Ah',
                'Свечи зажигания', 'Коврики автомобильные', 'Видеорегистратор', 'Антифриз',
                'Тормозные колодки', 'Амортизаторы'
            ]
        }
        
        products = Product.objects.all()[:100]  # Обновляем первые 100 товаров
        
        for i, product in enumerate(products):
            # Определяем категорию товара
            category_type = 'electronics'  # по умолчанию
            
            if product.category:
                category_slug = product.category.slug.lower()
                if 'clothing' in category_slug or 'odezhda' in category_slug:
                    category_type = 'clothing'
                elif 'beauty' in category_slug or 'krasota' in category_slug:
                    category_type = 'beauty'
                elif 'sport' in category_slug:
                    category_type = 'sports'
                elif 'home' in category_slug or 'garden' in category_slug:
                    category_type = 'home'
                elif 'auto' in category_slug:
                    category_type = 'auto'
            
            # Выбираем случайное название из соответствующей категории
            available_names = product_names.get(category_type, product_names['electronics'])
            product_name = random.choice(available_names)
            
            try:
                translation, created = product.translations.get_or_create(
                    language_code='ru',
                    defaults={
                        'name': product_name,
                        'description': f'Качественный товар {product_name.lower()}'
                    }
                )
                
                if not created:
                    translation.name = product_name
                    translation.description = f'Качественный товар {product_name.lower()}'
                    translation.save()
                
                if i < 10:  # Показываем только первые 10
                    self.stdout.write(f'Updated product {product.id}: {product_name}')
                    
            except Exception as e:
                self.stdout.write(f'Error updating product {product.id}: {str(e)}')