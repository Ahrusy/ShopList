from django.core.management.base import BaseCommand
from products.models import Category, Product, Shop, Tag


class Command(BaseCommand):
    help = 'Update translations with proper Russian names'

    def handle(self, *args, **options):
        self.stdout.write('Updating Russian translations...')
        
        # Словарь для перевода категорий
        category_translations = {
            'electronics': 'Электроника',
            'clothing': 'Одежда',
            'home-garden': 'Дом и сад',
            'beauty': 'Красота и здоровье',
            'sports': 'Спорт и отдых',
            'auto': 'Автотовары',
            'books': 'Книги',
            'food': 'Продукты питания',
            'pets': 'Товары для животных',
            'bytovaya-tehnika': 'Бытовая техника',
            
            # Электроника подкатегории
            'iphone': 'iPhone',
            'samsung': 'Samsung',
            'xiaomi': 'Xiaomi',
            'huawei': 'Huawei',
            'playstation': 'PlayStation',
            'xbox': 'Xbox',
            'nintendo': 'Nintendo',
            
            # Одежда подкатегории
            'odezhda': 'Одежда',
            'muzhskaya-odezhda': 'Мужская одежда',
            'zhenskaya-odezhda': 'Женская одежда',
            'detskaya-odezhda': 'Детская одежда',
            'obuv': 'Обувь',
            'aksessuary': 'Аксессуары',
            
            # Спорт подкатегории
            'sport-i-otdyh': 'Спорт и отдых',
            'fitnes': 'Фитнес',
            'turizm': 'Туризм',
            'rybalka': 'Рыбалка',
            'velosipedy': 'Велосипеды',
            'zimnie-vidy-sporta': 'Зимние виды спорта',
            
            # Красота подкатегории
            'krasota-i-zdorove': 'Красота и здоровье',
            'kosmetika': 'Косметика',
            'parfyumeriya': 'Парфюмерия',
            'uhod-za-kozhej': 'Уход за кожей',
            'uhod-za-volosami': 'Уход за волосами',
            'medicinskiye-tovary': 'Медицинские товары',
        }
        
        # Обновляем переводы категорий
        categories = Category.objects.all()
        for category in categories:
            # Получаем русское название из словаря или создаем на основе slug
            russian_name = self.get_russian_category_name(category.slug, category_translations)
            
            # Обновляем или создаем перевод
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
        
        # Обновляем названия товаров
        products = Product.objects.all()
        for product in products:
            # Создаем более осмысленное название товара
            russian_name = self.generate_product_name(product)
            
            translation, created = product.translations.get_or_create(
                language_code='ru',
                defaults={
                    'name': russian_name,
                    'description': f'Описание товара {russian_name}'
                }
            )
            
            if not created:
                translation.name = russian_name
                translation.description = f'Описание товара {russian_name}'
                translation.save()
            
            if product.id <= 10:  # Показываем только первые 10 для краткости
                self.stdout.write(f'Updated product {product.id}: {russian_name}')
        
        # Обновляем магазины
        shops = Shop.objects.all()
        shop_names = ['Электронный мир', 'Модный стиль', 'Дом и уют', 'Спорт центр', 'Красота плюс']
        for i, shop in enumerate(shops):
            russian_name = shop_names[i] if i < len(shop_names) else f'Магазин {shop.id}'
            
            translation, created = shop.translations.get_or_create(
                language_code='ru',
                defaults={
                    'name': russian_name,
                    'address': f'ул. Примерная, д. {shop.id}',
                    'city': 'Москва'
                }
            )
            
            if not created:
                translation.name = russian_name
                translation.address = f'ул. Примерная, д. {shop.id}'
                translation.city = 'Москва'
                translation.save()
            
            self.stdout.write(f'Updated shop {shop.id}: {russian_name}')
        
        # Обновляем теги
        tags = Tag.objects.all()
        tag_names = ['Новинка', 'Скидка', 'Хит продаж', 'Рекомендуем', 'Эксклюзив', 
                    'Премиум', 'Бестселлер', 'Акция', 'Топ выбор', 'Популярное',
                    'Качество', 'Надежность', 'Стиль', 'Комфорт', 'Инновации',
                    'Экологично', 'Доступно', 'Практично', 'Модно', 'Удобно', 'Выгодно', 'Тренд']
        
        for i, tag in enumerate(tags):
            russian_name = tag_names[i] if i < len(tag_names) else f'Тег {tag.id}'
            
            translation, created = tag.translations.get_or_create(
                language_code='ru',
                defaults={'name': russian_name}
            )
            
            if not created:
                translation.name = russian_name
                translation.save()
            
            self.stdout.write(f'Updated tag {tag.id}: {russian_name}')
        
        self.stdout.write(self.style.SUCCESS('Successfully updated Russian translations'))

    def get_russian_category_name(self, slug, translations_dict):
        """Получает русское название категории"""
        # Сначала проверяем точное совпадение
        if slug in translations_dict:
            return translations_dict[slug]
        
        # Ищем частичные совпадения
        for key, value in translations_dict.items():
            if key in slug:
                return value
        
        # Если не найдено, создаем на основе slug
        return self.slug_to_russian(slug)
    
    def slug_to_russian(self, slug):
        """Преобразует slug в русское название"""
        # Убираем category- префиксы и хеши
        clean_slug = slug.replace('category-', '').split('-category-')[0]
        
        # Словарь для базовых переводов
        basic_translations = {
            'electronics': 'Электроника',
            'clothing': 'Одежда', 
            'odezhda': 'Одежда',
            'beauty': 'Красота',
            'sports': 'Спорт',
            'sport': 'Спорт',
            'auto': 'Авто',
            'books': 'Книги',
            'food': 'Еда',
            'pets': 'Животные',
            'home': 'Дом',
            'garden': 'Сад',
            'bytovaya': 'Бытовая',
            'tehnika': 'техника',
            'krasota': 'Красота',
            'zdorove': 'здоровье',
            'otdyh': 'отдых'
        }
        
        # Пытаемся найти перевод
        for eng, rus in basic_translations.items():
            if eng in clean_slug:
                return rus
        
        # Если ничего не найдено, делаем красивое название из slug
        words = clean_slug.replace('-', ' ').split()
        return ' '.join(word.capitalize() for word in words if not word.isdigit() and len(word) > 2)
    
    def generate_product_name(self, product):
        """Генерирует осмысленное название товара"""
        category_name = ''
        try:
            if product.category:
                category_name = product.category.safe_translation_getter('name', product.category.slug)
        except:
            category_name = 'Товар'
        
        # Список типов товаров для разных категорий
        product_types = {
            'электроника': ['Смартфон', 'Планшет', 'Ноутбук', 'Наушники', 'Колонка', 'Телевизор', 'Камера'],
            'одежда': ['Футболка', 'Джинсы', 'Куртка', 'Платье', 'Рубашка', 'Свитер', 'Брюки'],
            'красота': ['Крем', 'Шампунь', 'Помада', 'Тушь', 'Духи', 'Лосьон', 'Маска'],
            'спорт': ['Кроссовки', 'Мяч', 'Гантели', 'Коврик', 'Велосипед', 'Ракетка', 'Форма'],
            'дом': ['Подушка', 'Одеяло', 'Ваза', 'Светильник', 'Картина', 'Зеркало', 'Часы'],
            'книги': ['Роман', 'Учебник', 'Справочник', 'Энциклопедия', 'Детектив', 'Фантастика'],
            'авто': ['Шины', 'Масло', 'Фильтр', 'Аккумулятор', 'Свечи', 'Коврики'],
            'животные': ['Корм', 'Игрушка', 'Поводок', 'Миска', 'Домик', 'Лежанка']
        }
        
        # Определяем тип товара на основе категории
        product_type = 'Товар'
        category_lower = category_name.lower()
        
        for cat_key, types in product_types.items():
            if cat_key in category_lower:
                import random
                product_type = random.choice(types)
                break
        
        # Добавляем бренд или модель
        brands = ['Premium', 'Classic', 'Modern', 'Deluxe', 'Standard', 'Pro', 'Elite', 'Basic']
        import random
        brand = random.choice(brands)
        
        return f'{product_type} {brand} #{product.id}'