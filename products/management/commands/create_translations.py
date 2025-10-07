from django.core.management.base import BaseCommand
from products.models import Category, Product, Shop, Tag


class Command(BaseCommand):
    help = 'Create basic translations for existing models'

    def handle(self, *args, **options):
        self.stdout.write('Creating translations...')
        
        # Create Category translations
        categories = Category.objects.all()
        for category in categories:
            if not hasattr(category, 'translations') or not category.translations.filter(language_code='ru').exists():
                category.create_translation(
                    language_code='ru',
                    name=category.slug.replace('-', ' ').title(),
                    description=f'Описание для категории {category.slug}'
                )
                self.stdout.write(f'Created translation for category: {category.slug}')
        
        # Create Product translations
        products = Product.objects.all()
        for product in products:
            if not hasattr(product, 'translations') or not product.translations.filter(language_code='ru').exists():
                product.create_translation(
                    language_code='ru',
                    name=f'Товар {product.id}' if not product.sku else product.sku,
                    description=f'Описание товара {product.id}'
                )
                self.stdout.write(f'Created translation for product: {product.id}')
        
        # Create Shop translations
        shops = Shop.objects.all()
        for shop in shops:
            if not hasattr(shop, 'translations') or not shop.translations.filter(language_code='ru').exists():
                shop.create_translation(
                    language_code='ru',
                    name=f'Магазин {shop.id}',
                    address=f'Адрес магазина {shop.id}',
                    city='Москва'
                )
                self.stdout.write(f'Created translation for shop: {shop.id}')
        
        # Create Tag translations
        tags = Tag.objects.all()
        for tag in tags:
            if not hasattr(tag, 'translations') or not tag.translations.filter(language_code='ru').exists():
                tag.create_translation(
                    language_code='ru',
                    name=f'Тег {tag.id}'
                )
                self.stdout.write(f'Created translation for tag: {tag.id}')
        
        self.stdout.write(self.style.SUCCESS('Successfully created translations'))