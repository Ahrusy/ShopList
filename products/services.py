"""
Сервисы для работы с товарами и изображениями
"""
import os
import uuid
from io import BytesIO
from PIL import Image, ImageOps
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.conf import settings
from .models import ProductImage


class ImageProcessor:
    """Сервис обработки изображений товаров"""
    
    # Размеры для различных вариантов изображений
    SIZES = {
        'thumbnail': (150, 150),
        'medium': (300, 300),
        'large': (800, 800),
    }
    
    # Качество сжатия для разных размеров
    QUALITY = {
        'thumbnail': 85,
        'medium': 90,
        'large': 95,
    }
    
    # Поддерживаемые форматы
    SUPPORTED_FORMATS = ['JPEG', 'PNG', 'WEBP']
    
    def __init__(self):
        self.max_file_size = getattr(settings, 'MAX_IMAGE_SIZE', 10 * 1024 * 1024)  # 10MB
        self.output_format = getattr(settings, 'IMAGE_OUTPUT_FORMAT', 'JPEG')
    
    def process_product_image(self, image_file, product, alt_text='', is_primary=False):
        """
        Обрабатывает изображение товара и создает все необходимые размеры
        
        Args:
            image_file: Файл изображения
            product: Экземпляр модели Product
            alt_text: Альтернативный текст
            is_primary: Является ли изображение основным
            
        Returns:
            ProductImage: Созданный экземпляр ProductImage
        """
        # Валидация изображения
        self._validate_image(image_file)
        
        # Создаем экземпляр ProductImage
        product_image = ProductImage(
            product=product,
            alt_text=alt_text,
            is_primary=is_primary
        )
        
        # Сохраняем оригинальное изображение
        original_name = self._generate_filename(image_file.name)
        product_image.image.save(original_name, image_file, save=False)
        
        # Открываем изображение для обработки
        image = Image.open(image_file)
        image = self._prepare_image(image)
        
        # Создаем различные размеры
        self._create_thumbnails(product_image, image)
        
        # Сохраняем экземпляр
        product_image.save()
        
        return product_image
    
    def _validate_image(self, image_file):
        """Валидирует загружаемое изображение"""
        # Проверяем размер файла
        if hasattr(image_file, 'size') and image_file.size > self.max_file_size:
            raise ValueError(f"Размер файла превышает максимально допустимый ({self.max_file_size} байт)")
        
        # Проверяем формат
        try:
            image = Image.open(image_file)
            if image.format not in self.SUPPORTED_FORMATS:
                raise ValueError(f"Неподдерживаемый формат изображения: {image.format}")
            
            # Проверяем размеры
            width, height = image.size
            if width < 100 or height < 100:
                raise ValueError("Минимальный размер изображения: 100x100 пикселей")
            
            if width > 5000 or height > 5000:
                raise ValueError("Максимальный размер изображения: 5000x5000 пикселей")
                
        except Exception as e:
            raise ValueError(f"Ошибка при обработке изображения: {str(e)}")
        finally:
            image_file.seek(0)  # Возвращаем указатель в начало файла
    
    def _prepare_image(self, image):
        """Подготавливает изображение для обработки"""
        # Конвертируем в RGB если необходимо
        if image.mode in ('RGBA', 'LA', 'P'):
            # Создаем белый фон для прозрачных изображений
            background = Image.new('RGB', image.size, (255, 255, 255))
            if image.mode == 'P':
                image = image.convert('RGBA')
            background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
            image = background
        elif image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Исправляем ориентацию на основе EXIF данных
        image = ImageOps.exif_transpose(image)
        
        return image
    
    def _create_thumbnails(self, product_image, original_image):
        """Создает миниатюры различных размеров"""
        for size_name, (width, height) in self.SIZES.items():
            # Создаем копию изображения
            img_copy = original_image.copy()
            
            # Изменяем размер с сохранением пропорций
            img_copy.thumbnail((width, height), Image.Resampling.LANCZOS)
            
            # Создаем квадратное изображение с белым фоном для thumbnail
            if size_name == 'thumbnail':
                square_img = Image.new('RGB', (width, height), (255, 255, 255))
                # Центрируем изображение
                x = (width - img_copy.width) // 2
                y = (height - img_copy.height) // 2
                square_img.paste(img_copy, (x, y))
                img_copy = square_img
            
            # Сохраняем в BytesIO
            output = BytesIO()
            img_copy.save(
                output,
                format=self.output_format,
                quality=self.QUALITY[size_name],
                optimize=True
            )
            output.seek(0)
            
            # Генерируем имя файла
            filename = self._generate_filename(
                product_image.image.name,
                suffix=f"_{size_name}"
            )
            
            # Сохраняем в соответствующее поле
            field = getattr(product_image, size_name)
            field.save(
                filename,
                ContentFile(output.getvalue()),
                save=False
            )
    
    def _generate_filename(self, original_name, suffix=''):
        """Генерирует уникальное имя файла"""
        name, ext = os.path.splitext(original_name)
        if not ext:
            ext = '.jpg'
        
        # Генерируем уникальный идентификатор
        unique_id = uuid.uuid4().hex[:8]
        
        return f"{unique_id}{suffix}{ext}"
    
    def optimize_existing_images(self, product_image_id=None):
        """
        Оптимизирует существующие изображения
        
        Args:
            product_image_id: ID конкретного изображения или None для всех
        """
        if product_image_id:
            images = ProductImage.objects.filter(id=product_image_id)
        else:
            images = ProductImage.objects.filter(
                thumbnail__isnull=True
            ).select_related('product')
        
        processed_count = 0
        
        for product_image in images:
            try:
                if product_image.image:
                    # Открываем оригинальное изображение
                    image = Image.open(product_image.image.path)
                    image = self._prepare_image(image)
                    
                    # Создаем миниатюры
                    self._create_thumbnails(product_image, image)
                    
                    # Сохраняем изменения
                    product_image.save()
                    processed_count += 1
                    
            except Exception as e:
                print(f"Ошибка при обработке изображения {product_image.id}: {str(e)}")
                continue
        
        return processed_count
    
    def cleanup_unused_images(self):
        """Удаляет неиспользуемые файлы изображений"""
        # Получаем все пути к файлам из базы данных
        used_files = set()
        
        for product_image in ProductImage.objects.all():
            if product_image.image:
                used_files.add(product_image.image.name)
            if product_image.thumbnail:
                used_files.add(product_image.thumbnail.name)
            if product_image.medium:
                used_files.add(product_image.medium.name)
            if product_image.large:
                used_files.add(product_image.large.name)
        
        # Сканируем директории с изображениями
        media_root = settings.MEDIA_ROOT
        products_dir = os.path.join(media_root, 'products')
        
        if not os.path.exists(products_dir):
            return 0
        
        deleted_count = 0
        
        for root, dirs, files in os.walk(products_dir):
            for file in files:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, media_root)
                
                if relative_path not in used_files:
                    try:
                        os.remove(file_path)
                        deleted_count += 1
                    except OSError:
                        continue
        
        return deleted_count


class ProductImageManager:
    """Менеджер для работы с изображениями товаров"""
    
    def __init__(self):
        self.processor = ImageProcessor()
    
    def add_image_to_product(self, product, image_file, alt_text='', is_primary=False):
        """Добавляет изображение к товару"""
        # Если это первое изображение, делаем его основным
        if not product.images.exists():
            is_primary = True
        
        # Если устанавливаем как основное, убираем флаг с других
        if is_primary:
            product.images.update(is_primary=False)
        
        return self.processor.process_product_image(
            image_file, product, alt_text, is_primary
        )
    
    def set_primary_image(self, product, image_id):
        """Устанавливает основное изображение для товара"""
        # Убираем флаг основного со всех изображений
        product.images.update(is_primary=False)
        
        # Устанавливаем флаг для выбранного изображения
        try:
            image = product.images.get(id=image_id)
            image.is_primary = True
            image.save()
            return image
        except ProductImage.DoesNotExist:
            raise ValueError("Изображение не найдено")
    
    def reorder_images(self, product, image_ids_order):
        """Изменяет порядок изображений товара"""
        for order, image_id in enumerate(image_ids_order):
            try:
                image = product.images.get(id=image_id)
                image.order = order
                image.save(update_fields=['order'])
            except ProductImage.DoesNotExist:
                continue
    
    def get_product_images_data(self, product):
        """Возвращает данные об изображениях товара для API"""
        images_data = []
        
        for image in product.images.all().order_by('order', 'id'):
            images_data.append({
                'id': image.id,
                'urls': image.get_responsive_urls(),
                'alt_text': image.alt_text,
                'is_primary': image.is_primary,
                'order': image.order,
                'width': image.width,
                'height': image.height,
                'file_size': image.file_size,
            })
        
        return images_data


class ProductLoader:
    """Система загрузки товаров с реальными данными"""
    
    # Шаблоны товаров для разных категорий
    PRODUCT_TEMPLATES = {
        'электроника': {
            'смартфоны': [
                {'name': 'iPhone 15 Pro', 'price_range': (80000, 120000), 'brands': ['Apple']},
                {'name': 'Samsung Galaxy S24', 'price_range': (60000, 90000), 'brands': ['Samsung']},
                {'name': 'Xiaomi 14', 'price_range': (40000, 60000), 'brands': ['Xiaomi']},
                {'name': 'Huawei P60', 'price_range': (50000, 70000), 'brands': ['Huawei']},
            ],
            'ноутбуки': [
                {'name': 'MacBook Pro 16"', 'price_range': (200000, 300000), 'brands': ['Apple']},
                {'name': 'Dell XPS 13', 'price_range': (80000, 120000), 'brands': ['Dell']},
                {'name': 'Lenovo ThinkPad', 'price_range': (60000, 100000), 'brands': ['Lenovo']},
                {'name': 'ASUS ZenBook', 'price_range': (50000, 80000), 'brands': ['ASUS']},
            ],
            'телевизоры': [
                {'name': 'Samsung QLED 55"', 'price_range': (80000, 150000), 'brands': ['Samsung']},
                {'name': 'LG OLED 65"', 'price_range': (120000, 200000), 'brands': ['LG']},
                {'name': 'Sony Bravia 50"', 'price_range': (60000, 100000), 'brands': ['Sony']},
            ],
        },
        'одежда': {
            'мужская': [
                {'name': 'Рубашка классическая', 'price_range': (2000, 8000), 'brands': ['Zara', 'H&M', 'Uniqlo']},
                {'name': 'Джинсы прямые', 'price_range': (3000, 12000), 'brands': ['Levi\'s', 'Wrangler', 'Lee']},
                {'name': 'Куртка демисезонная', 'price_range': (5000, 20000), 'brands': ['Nike', 'Adidas', 'Puma']},
                {'name': 'Костюм деловой', 'price_range': (15000, 50000), 'brands': ['Hugo Boss', 'Armani', 'Zegna']},
            ],
            'женская': [
                {'name': 'Платье коктейльное', 'price_range': (3000, 15000), 'brands': ['Zara', 'Mango', 'H&M']},
                {'name': 'Блузка шелковая', 'price_range': (2500, 10000), 'brands': ['Massimo Dutti', 'COS', 'Arket']},
                {'name': 'Юбка миди', 'price_range': (2000, 8000), 'brands': ['Zara', 'Bershka', 'Pull&Bear']},
            ],
        },
        'красота': {
            'уход за лицом': [
                {'name': 'Крем увлажняющий', 'price_range': (500, 5000), 'brands': ['L\'Oreal', 'Nivea', 'Garnier']},
                {'name': 'Сыворотка антивозрастная', 'price_range': (1000, 8000), 'brands': ['Vichy', 'La Roche-Posay', 'Avene']},
                {'name': 'Маска очищающая', 'price_range': (300, 2000), 'brands': ['The Body Shop', 'Lush', 'Origins']},
            ],
            'макияж': [
                {'name': 'Тональный крем', 'price_range': (800, 4000), 'brands': ['Maybelline', 'MAC', 'Dior']},
                {'name': 'Помада матовая', 'price_range': (500, 3000), 'brands': ['NYX', 'Urban Decay', 'Charlotte Tilbury']},
                {'name': 'Тушь для ресниц', 'price_range': (400, 2500), 'brands': ['Maybelline', 'L\'Oreal', 'Lancome']},
            ],
        },
        'дом и сад': {
            'мебель': [
                {'name': 'Диван угловой', 'price_range': (30000, 150000), 'brands': ['IKEA', 'Hoff', 'Много Мебели']},
                {'name': 'Стол обеденный', 'price_range': (10000, 50000), 'brands': ['IKEA', 'Столплит', 'Мебель России']},
                {'name': 'Кресло офисное', 'price_range': (5000, 30000), 'brands': ['Chairman', 'Бюрократ', 'Метта']},
            ],
            'декор': [
                {'name': 'Ваза декоративная', 'price_range': (500, 5000), 'brands': ['Zara Home', 'H&M Home', 'IKEA']},
                {'name': 'Подушка декоративная', 'price_range': (800, 3000), 'brands': ['Zara Home', 'Tkano', 'Arket']},
                {'name': 'Свеча ароматическая', 'price_range': (300, 2000), 'brands': ['Yankee Candle', 'Bath & Body Works', 'Diptyque']},
            ],
        },
        'спорт': {
            'фитнес': [
                {'name': 'Гантели разборные', 'price_range': (2000, 15000), 'brands': ['Torneo', 'DFC', 'Kettler']},
                {'name': 'Коврик для йоги', 'price_range': (500, 3000), 'brands': ['Adidas', 'Nike', 'Reebok']},
                {'name': 'Фитбол', 'price_range': (800, 2500), 'brands': ['Torneo', 'Starfit', 'Indigo']},
            ],
            'одежда': [
                {'name': 'Кроссовки беговые', 'price_range': (5000, 25000), 'brands': ['Nike', 'Adidas', 'New Balance']},
                {'name': 'Футболка спортивная', 'price_range': (1000, 5000), 'brands': ['Nike', 'Adidas', 'Puma']},
                {'name': 'Леггинсы для фитнеса', 'price_range': (1500, 8000), 'brands': ['Nike', 'Adidas', 'Lululemon']},
            ],
        },
        'автотовары': {
            'запчасти': [
                {'name': 'Тормозные колодки', 'price_range': (1500, 8000), 'brands': ['Bosch', 'Brembo', 'ATE']},
                {'name': 'Масло моторное 5W-30', 'price_range': (1000, 5000), 'brands': ['Mobil', 'Shell', 'Castrol']},
                {'name': 'Фильтр воздушный', 'price_range': (500, 2000), 'brands': ['Mann', 'Mahle', 'Bosch']},
            ],
            'аксессуары': [
                {'name': 'Чехлы на сиденья', 'price_range': (2000, 15000), 'brands': ['Autoprofi', 'Seintex', 'Rival']},
                {'name': 'Коврики резиновые', 'price_range': (1000, 5000), 'brands': ['Norplast', 'Rival', 'Seintex']},
                {'name': 'Органайзер в багажник', 'price_range': (800, 3000), 'brands': ['Autoprofi', 'Airline', 'Phantom']},
            ],
        },
    }
    
    # Цвета для товаров
    COLORS = ['Черный', 'Белый', 'Серый', 'Синий', 'Красный', 'Зеленый', 'Желтый', 'Розовый', 'Фиолетовый', 'Коричневый']
    
    # Размеры для одежды
    CLOTHING_SIZES = ['XS', 'S', 'M', 'L', 'XL', 'XXL']
    
    def __init__(self):
        import random
        self.random = random
        self.image_manager = ProductImageManager()
    
    def create_realistic_products(self, category, count=50):
        """
        Создает реалистичные товары для указанной категории
        
        Args:
            category: Экземпляр модели Category
            count: Количество товаров для создания
            
        Returns:
            list: Список созданных товаров
        """
        from .models import Product, Tag
        
        created_products = []
        category_name = category.name.lower()
        
        # Находим подходящий шаблон
        template_data = self._find_template_data(category_name)
        
        if not template_data:
            # Создаем общие товары если шаблон не найден
            template_data = [
                {'name': f'Товар {category.name}', 'price_range': (1000, 10000), 'brands': ['Generic']}
            ]
        
        for i in range(count):
            try:
                product_data = self._generate_product_data(template_data, category, i)
                
                # Создаем товар
                product = Product.objects.create(**product_data)
                
                # Добавляем характеристики
                self._add_product_characteristics(product, category_name)
                
                # Добавляем теги
                self._add_product_tags(product, category_name)
                
                # Создаем изображение-заглушку
                self._create_placeholder_image(product)
                
                created_products.append(product)
                
            except Exception as e:
                print(f"Ошибка при создании товара {i}: {str(e)}")
                continue
        
        return created_products
    
    def _find_template_data(self, category_name):
        """Находит подходящий шаблон данных для категории"""
        for main_category, subcategories in self.PRODUCT_TEMPLATES.items():
            if main_category in category_name:
                # Ищем подходящую подкатегорию
                for subcategory, products in subcategories.items():
                    if subcategory in category_name:
                        return products
                # Если подкатегория не найдена, возвращаем первую доступную
                return list(subcategories.values())[0]
        
        return None
    
    def _generate_product_data(self, template_data, category, index):
        """Генерирует данные для товара на основе шаблона"""
        template = self.random.choice(template_data)
        brand = self.random.choice(template['brands'])
        
        # Генерируем вариации названия
        base_name = template['name']
        variations = [
            f"{brand} {base_name}",
            f"{base_name} {brand}",
            f"{base_name} Premium",
            f"{base_name} Classic",
            f"{base_name} Pro",
        ]
        
        name = self.random.choice(variations)
        
        # Добавляем цвет или размер если подходит
        if any(word in category.name.lower() for word in ['одежда', 'обувь', 'аксессуары']):
            if self.random.choice([True, False]):
                color = self.random.choice(self.COLORS)
                name += f" {color}"
            if self.random.choice([True, False]):
                size = self.random.choice(self.CLOTHING_SIZES)
                name += f" {size}"
        
        # Генерируем цену
        min_price, max_price = template['price_range']
        price = self.random.randint(min_price, max_price)
        
        # Генерируем скидку (30% вероятность)
        discount_price = None
        if self.random.random() < 0.3:
            discount_percent = self.random.randint(10, 50)
            discount_price = price * (100 - discount_percent) / 100
        
        # Генерируем описание
        description = self._generate_description(name, brand, category.name)
        
        return {
            'name': name,
            'description': description,
            'price': price,
            'discount_price': discount_price,
            'category': category,
            'brand': brand,
            'stock_quantity': self.random.randint(0, 100),
            'is_active': True,
            'rating': round(self.random.uniform(3.5, 5.0), 1),
            'reviews_count': self.random.randint(0, 500),
            'views_count': self.random.randint(0, 1000),
        }
    
    def _generate_description(self, name, brand, category_name):
        """Генерирует описание товара"""
        descriptions = [
            f"Высококачественный {name.lower()} от известного бренда {brand}. Отличное соотношение цены и качества.",
            f"Популярный {name.lower()} в категории {category_name}. Рекомендуется покупателями.",
            f"Новинка от {brand} - {name.lower()}. Современный дизайн и надежность.",
            f"Бестселлер в категории {category_name} - {name.lower()}. Проверено временем.",
            f"Премиум качество от {brand}. {name} - выбор профессионалов.",
        ]
        
        base_description = self.random.choice(descriptions)
        
        # Добавляем дополнительные характеристики
        features = [
            "Гарантия производителя",
            "Быстрая доставка",
            "Возможность возврата",
            "Сертифицированное качество",
            "Экологически чистые материалы",
            "Инновационные технологии",
            "Стильный дизайн",
            "Долговечность",
        ]
        
        selected_features = self.random.sample(features, self.random.randint(2, 4))
        features_text = "Особенности: " + ", ".join(selected_features) + "."
        
        return f"{base_description}\n\n{features_text}"
    
    def _add_product_characteristics(self, product, category_name):
        """Добавляет характеристики товару"""
        from .models import ProductCharacteristic
        
        characteristics = []
        
        if 'электроника' in category_name or 'техника' in category_name:
            characteristics = [
                ('Гарантия', f'{self.random.randint(1, 3)} года'),
                ('Страна производства', self.random.choice(['Китай', 'Корея', 'Япония', 'США', 'Германия'])),
                ('Вес', f'{self.random.randint(100, 5000)} г'),
            ]
        elif 'одежда' in category_name:
            characteristics = [
                ('Материал', self.random.choice(['Хлопок', 'Полиэстер', 'Шерсть', 'Лен', 'Вискоза'])),
                ('Сезон', self.random.choice(['Весна-Лето', 'Осень-Зима', 'Всесезонный'])),
                ('Уход', 'Машинная стирка при 30°C'),
            ]
        elif 'красота' in category_name:
            characteristics = [
                ('Объем', f'{self.random.choice([30, 50, 100, 200])} мл'),
                ('Тип кожи', self.random.choice(['Все типы', 'Сухая', 'Жирная', 'Комбинированная', 'Чувствительная'])),
                ('Срок годности', f'{self.random.randint(12, 36)} месяцев'),
            ]
        elif 'дом' in category_name:
            characteristics = [
                ('Материал', self.random.choice(['Дерево', 'Металл', 'Пластик', 'Стекло', 'Керамика'])),
                ('Размеры', f'{self.random.randint(10, 200)}x{self.random.randint(10, 200)}x{self.random.randint(5, 100)} см'),
                ('Вес', f'{self.random.randint(500, 50000)} г'),
            ]
        
        for i, (name, value) in enumerate(characteristics):
            ProductCharacteristic.objects.create(
                product=product,
                name=name,
                value=value,
                order=i
            )
    
    def _add_product_tags(self, product, category_name):
        """Добавляет теги товару"""
        from .models import Tag
        
        # Общие теги
        common_tags = ['Новинка', 'Хит продаж', 'Рекомендуем', 'Скидка', 'Качество']
        
        # Специфичные теги по категориям
        category_tags = {
            'электроника': ['Гаджеты', 'Технологии', 'Инновации'],
            'одежда': ['Мода', 'Стиль', 'Тренд'],
            'красота': ['Уход', 'Красота', 'Здоровье'],
            'дом': ['Интерьер', 'Комфорт', 'Уют'],
            'спорт': ['Спорт', 'Фитнес', 'Здоровье'],
            'авто': ['Автомобили', 'Тюнинг', 'Безопасность'],
        }
        
        # Выбираем подходящие теги
        available_tags = common_tags.copy()
        for key, tags in category_tags.items():
            if key in category_name:
                available_tags.extend(tags)
                break
        
        # Добавляем случайные теги
        selected_tags = self.random.sample(available_tags, self.random.randint(1, 3))
        
        for tag_name in selected_tags:
            tag, created = Tag.objects.get_or_create(
                name=tag_name,
                defaults={'color': self.random.choice(['#007bff', '#28a745', '#dc3545', '#ffc107', '#17a2b8'])}
            )
            product.tags.add(tag)
    
    def _create_placeholder_image(self, product):
        """Создает изображение-заглушку для товара"""
        from PIL import Image, ImageDraw, ImageFont
        from io import BytesIO
        from django.core.files.base import ContentFile
        
        # Создаем изображение 400x400
        img = Image.new('RGB', (400, 400), color='#f8f9fa')
        draw = ImageDraw.Draw(img)
        
        # Рисуем рамку
        draw.rectangle([10, 10, 390, 390], outline='#dee2e6', width=2)
        
        # Добавляем текст
        try:
            # Пытаемся использовать системный шрифт
            font = ImageFont.truetype("arial.ttf", 16)
        except:
            # Если не получается, используем стандартный
            font = ImageFont.load_default()
        
        # Название товара (обрезаем если слишком длинное)
        text = product.name[:30] + "..." if len(product.name) > 30 else product.name
        
        # Вычисляем позицию для центрирования текста
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (400 - text_width) // 2
        y = (400 - text_height) // 2
        
        draw.text((x, y), text, fill='#6c757d', font=font)
        
        # Добавляем цену
        price_text = f"{product.price:,.0f} ₽"
        bbox = draw.textbbox((0, 0), price_text, font=font)
        price_width = bbox[2] - bbox[0]
        
        x = (400 - price_width) // 2
        y = y + text_height + 20
        
        draw.text((x, y), price_text, fill='#28a745', font=font)
        
        # Сохраняем в BytesIO
        output = BytesIO()
        img.save(output, format='JPEG', quality=85)
        output.seek(0)
        
        # Создаем ProductImage
        from .models import ProductImage
        
        filename = f"placeholder_{product.id}.jpg"
        
        product_image = ProductImage(
            product=product,
            alt_text=f"Изображение {product.name}",
            is_primary=True,
            order=0
        )
        
        product_image.image.save(
            filename,
            ContentFile(output.getvalue()),
            save=False
        )
        
        product_image.save()
        
        return product_image
    
    def load_products_for_all_categories(self, products_per_category=20):
        """Загружает товары для всех категорий 3-го уровня"""
        from .models import Category
        
        # Получаем все категории 3-го уровня (самые глубокие)
        leaf_categories = Category.objects.filter(
            category_level=2,
            is_active=True
        ).select_related('parent__parent')
        
        total_created = 0
        
        for category in leaf_categories:
            print(f"Создание товаров для категории: {category.name}")
            
            try:
                created_products = self.create_realistic_products(
                    category, 
                    products_per_category
                )
                total_created += len(created_products)
                
                print(f"  Создано товаров: {len(created_products)}")
                
            except Exception as e:
                print(f"  Ошибка при создании товаров: {str(e)}")
                continue
        
        return total_created