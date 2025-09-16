from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.conf import settings
import requests
import os
from products.models import Product, ProductImage
from PIL import Image
import io


class Command(BaseCommand):
    help = 'Загружает изображения товаров через Unsplash API'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            default=50,
            help='Количество товаров для загрузки изображений'
        )
        parser.add_argument(
            '--width',
            type=int,
            default=800,
            help='Ширина изображения'
        )
        parser.add_argument(
            '--height',
            type=int,
            default=600,
            help='Высота изображения'
        )

    def handle(self, *args, **options):
        if not settings.UNSPLASH_ACCESS_KEY:
            self.stdout.write(
                self.style.ERROR('UNSPLASH_ACCESS_KEY не настроен в settings.py')
            )
            return

        limit = options['limit']
        width = options['width']
        height = options['height']

        # Получаем товары без изображений
        products = Product.objects.filter(images__isnull=True)[:limit]
        
        if not products.exists():
            self.stdout.write(
                self.style.WARNING('Все товары уже имеют изображения')
            )
            return

        self.stdout.write(f'Загружаем изображения для {products.count()} товаров...')

        for product in products:
            try:
                self.load_product_images(product, width, height)
                self.stdout.write(f'✓ Загружены изображения для: {product.name}')
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'✗ Ошибка для {product.name}: {str(e)}')
                )

        self.stdout.write(
            self.style.SUCCESS('Загрузка изображений завершена!')
        )

    def load_product_images(self, product, width, height):
        """Загружает изображения для товара"""
        # Определяем ключевые слова для поиска изображений
        keywords = self.get_search_keywords(product)
        
        for i, keyword in enumerate(keywords[:3]):  # Максимум 3 изображения
            try:
                # Запрашиваем изображение через Unsplash API
                url = f"https://api.unsplash.com/photos/random"
                params = {
                    'query': keyword,
                    'w': width,
                    'h': height,
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
                
                # Изменяем размер если нужно
                if image.size != (width, height):
                    image = image.resize((width, height), Image.Resampling.LANCZOS)
                
                # Сохраняем в BytesIO
                img_io = io.BytesIO()
                image.save(img_io, format='JPEG', quality=85)
                img_io.seek(0)
                
                # Создаем ProductImage
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
                    self.style.WARNING(f'Не удалось загрузить изображение {i+1} для {product.name}: {str(e)}')
                )
                continue

    def get_search_keywords(self, product):
        """Определяет ключевые слова для поиска изображений"""
        keywords = []
        
        # Основное ключевое слово из названия товара
        keywords.append(product.name)
        
        # Ключевые слова из категории
        if product.category:
            keywords.append(product.category.name)
        
        # Ключевые слова из тегов
        for tag in product.tags.all():
            keywords.append(tag.name)
        
        # Дополнительные ключевые слова в зависимости от категории
        if product.category:
            category_keywords = {
                'Электроника': ['electronics', 'technology', 'gadgets'],
                'Одежда и обувь': ['fashion', 'clothing', 'shoes'],
                'Дом и сад': ['home', 'garden', 'furniture'],
                'Спорт и отдых': ['sports', 'fitness', 'outdoor'],
                'Красота и здоровье': ['beauty', 'health', 'cosmetics'],
                'Книги и медиа': ['books', 'media', 'education'],
                'Автомобили': ['cars', 'automotive', 'vehicles'],
                'Детские товары': ['kids', 'children', 'toys'],
                'Продукты питания': ['food', 'grocery', 'cooking'],
                'Промышленность': ['industrial', 'tools', 'equipment'],
            }
            
            for cat_name, cat_keywords in category_keywords.items():
                if cat_name.lower() in product.category.name.lower():
                    keywords.extend(cat_keywords)
                    break
        
        return keywords[:5]  # Максимум 5 ключевых слов
