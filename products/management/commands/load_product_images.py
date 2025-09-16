from django.core.management.base import BaseCommand
from django.conf import settings
from products.models import Product, ProductImage
import requests
from PIL import Image
import io
import os
import random


class Command(BaseCommand):
    help = 'Загружает изображения для товаров'

    def add_arguments(self, parser):
        parser.add_argument(
            '--products',
            type=int,
            default=50,
            help='Количество товаров для загрузки изображений'
        )

    def handle(self, *args, **options):
        self.stdout.write('Начинаем загрузку изображений...')
        
        products = Product.objects.all()[:options['products']]
        
        for i, product in enumerate(products):
            self.stdout.write(f'Обрабатываем товар {i+1}: {product.name}')
            
            # Создаем изображения для товара
            self.create_product_images(product)
            
            if (i + 1) % 10 == 0:
                self.stdout.write(f'Обработано товаров: {i + 1}')

        self.stdout.write(
            self.style.SUCCESS(f'Изображения загружены для {len(products)} товаров!')
        )

    def create_product_images(self, product):
        """Создает изображения для товара"""
        # Определяем ключевые слова для поиска изображений на основе категории и названия
        keywords = self.get_keywords_for_product(product)
        
        # Создаем 2-3 изображения для каждого товара
        for i in range(random.randint(2, 3)):
            try:
                # Создаем изображение-заглушку с информацией о товаре
                self.create_placeholder_image(product, i, keywords)
            except Exception as e:
                self.stdout.write(f'  Ошибка создания изображения {i+1}: {e}')

    def get_keywords_for_product(self, product):
        """Получает ключевые слова для товара на основе категории и названия"""
        category_keywords = {
            'Электроника': ['electronics', 'technology', 'gadgets'],
            'Одежда и обувь': ['clothing', 'fashion', 'shoes'],
            'Дом и сад': ['home', 'garden', 'household'],
            'Спорт и отдых': ['sports', 'fitness', 'outdoor'],
            'Красота и здоровье': ['beauty', 'cosmetics', 'health'],
            'Книги и медиа': ['books', 'media', 'reading'],
            'Автомобили': ['automotive', 'car', 'vehicle'],
            'Детские товары': ['kids', 'children', 'baby'],
            'Продукты питания': ['food', 'grocery', 'fresh'],
            'Промышленность': ['industrial', 'tools', 'equipment'],
        }
        
        # Получаем ключевые слова для категории
        keywords = category_keywords.get(product.category.name, ['product', 'item'])
        
        # Добавляем ключевые слова из названия товара
        name_words = product.name.lower().split()
        for word in name_words:
            if len(word) > 3:  # Игнорируем короткие слова
                keywords.append(word)
        
        return keywords

    def create_placeholder_image(self, product, image_index, keywords):
        """Создает изображение-заглушку для товара"""
        try:
            # Создаем изображение с градиентом
            width, height = 400, 300
            img = Image.new('RGB', (width, height), color='lightgray')
            
            # Создаем градиент
            from PIL import ImageDraw
            draw = ImageDraw.Draw(img)
            
            # Создаем градиент от светлого к темному
            for y in range(height):
                color_value = int(200 - (y / height) * 100)
                color = (color_value, color_value, color_value)
                draw.line([(0, y), (width, y)], fill=color)
            
            # Добавляем рамку
            draw.rectangle([0, 0, width-1, height-1], outline='black', width=2)
            
            # Добавляем текст с названием товара
            try:
                from PIL import ImageFont
                # Пытаемся использовать системный шрифт
                try:
                    font_large = ImageFont.truetype("arial.ttf", 24)
                    font_small = ImageFont.truetype("arial.ttf", 16)
                except:
                    font_large = ImageFont.load_default()
                    font_small = ImageFont.load_default()
            except:
                font_large = ImageFont.load_default()
                font_small = ImageFont.load_default()
            
            # Название товара
            product_name = product.name[:30] + "..." if len(product.name) > 30 else product.name
            text_bbox = draw.textbbox((0, 0), product_name, font=font_large)
            text_width = text_bbox[2] - text_bbox[0]
            text_x = (width - text_width) // 2
            text_y = height // 2 - 30
            
            draw.text((text_x, text_y), product_name, fill='black', font=font_large)
            
            # Цена товара
            price_text = f"{product.price} руб."
            price_bbox = draw.textbbox((0, 0), price_text, font=font_small)
            price_width = price_bbox[2] - price_bbox[0]
            price_x = (width - price_width) // 2
            price_y = text_y + 40
            
            draw.text((price_x, price_y), price_text, fill='darkgreen', font=font_small)
            
            # Категория
            category_text = product.category.name
            cat_bbox = draw.textbbox((0, 0), category_text, font=font_small)
            cat_width = cat_bbox[2] - cat_bbox[0]
            cat_x = (width - cat_width) // 2
            cat_y = price_y + 25
            
            draw.text((cat_x, cat_y), category_text, fill='blue', font=font_small)
            
            # Добавляем декоративные элементы
            # Рамка вокруг текста
            draw.rectangle([text_x-10, text_y-10, text_x+text_width+10, cat_y+20], 
                          outline='white', width=2)
            
            # Сохраняем изображение
            img_io = io.BytesIO()
            img.save(img_io, format='JPEG', quality=85)
            img_io.seek(0)
            
            # Создаем ProductImage
            product_image = ProductImage.objects.create(
                product=product,
                alt_text=f"Изображение {product.name} {image_index+1}",
                order=image_index,
                is_primary=(image_index == 0)
            )
            
            filename = f"product_{product.id}_image_{image_index+1}.jpg"
            product_image.image.save(filename, img_io, save=True)
            
            self.stdout.write(f'  Создано изображение: {filename}')
            
        except Exception as e:
            self.stdout.write(f'  Ошибка создания изображения: {e}')

