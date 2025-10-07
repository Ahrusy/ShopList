from django.core.management.base import BaseCommand
from products.models import Category, Product


class Command(BaseCommand):
    help = 'Check current Russian translations'

    def handle(self, *args, **options):
        self.stdout.write('Checking Russian translations...')
        
        # Проверяем основные категории
        self.stdout.write('\n=== ОСНОВНЫЕ КАТЕГОРИИ ===')
        main_categories = Category.objects.filter(parent__isnull=True)[:10]
        
        for category in main_categories:
            try:
                russian_name = category.safe_translation_getter('name', category.slug)
                self.stdout.write(f'{category.slug} -> {russian_name}')
            except:
                self.stdout.write(f'{category.slug} -> НЕТ ПЕРЕВОДА')
        
        # Проверяем подкатегории
        self.stdout.write('\n=== ПОДКАТЕГОРИИ ===')
        subcategories = Category.objects.filter(parent__isnull=False)[:10]
        
        for category in subcategories:
            try:
                russian_name = category.safe_translation_getter('name', category.slug)
                self.stdout.write(f'{category.slug} -> {russian_name}')
            except:
                self.stdout.write(f'{category.slug} -> НЕТ ПЕРЕВОДА')
        
        # Проверяем товары
        self.stdout.write('\n=== ТОВАРЫ ===')
        products = Product.objects.all()[:10]
        
        for product in products:
            try:
                russian_name = product.safe_translation_getter('name', f'Товар {product.id}')
                self.stdout.write(f'Товар {product.id} -> {russian_name}')
            except:
                self.stdout.write(f'Товар {product.id} -> НЕТ ПЕРЕВОДА')
        
        # Статистика
        total_categories = Category.objects.count()
        categories_with_translations = Category.objects.filter(translations__language_code='ru').distinct().count()
        
        total_products = Product.objects.count()
        products_with_translations = Product.objects.filter(translations__language_code='ru').distinct().count()
        
        self.stdout.write('\n=== СТАТИСТИКА ===')
        self.stdout.write(f'Категории с переводами: {categories_with_translations}/{total_categories}')
        self.stdout.write(f'Товары с переводами: {products_with_translations}/{total_products}')
        
        self.stdout.write(self.style.SUCCESS('Проверка завершена!'))