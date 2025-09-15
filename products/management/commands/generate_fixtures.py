import os
import random
from django.core.management.base import BaseCommand
from django.core.files import File
from django.conf import settings
from faker import Faker
from factory import fuzzy
from factory.django import DjangoModelFactory
from parler.utils.context import switch_language
from products.models import Category, Shop, Product, ProductImage, Tag, User
import requests
import json
import environ

# Initialize environment variables
env = environ.Env()
environ.Env.read_env(os.path.join(settings.BASE_DIR, '.env'))

UNSPLASH_ACCESS_KEY = env('UNSPLASH_ACCESS_KEY')

class CategoryFactory(DjangoModelFactory):
    class Meta:
        model = Category

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        obj = model_class()
        for lang_code, _ in settings.LANGUAGES:
            with switch_language(obj, lang_code):
                obj.name = Faker(lang_code).word().capitalize()
                obj.slug = Faker(lang_code).slug()
        obj.save()
        return obj

class ShopFactory(DjangoModelFactory):
    class Meta:
        model = Shop

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        obj = model_class()
        for lang_code, _ in settings.LANGUAGES:
            with switch_language(obj, lang_code):
                obj.name = Faker(lang_code).company()
                obj.address = Faker(lang_code).address()
                obj.city = Faker(lang_code).city()
        obj.latitude = fuzzy.FuzzyFloat(-90, 90).evaluate(2, None, False)
        obj.longitude = fuzzy.FuzzyFloat(-180, 180).evaluate(2, None, False)
        obj.save()
        return obj

class TagFactory(DjangoModelFactory):
    class Meta:
        model = Tag

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        obj = model_class()
        for lang_code, _ in settings.LANGUAGES:
            with switch_language(obj, lang_code):
                obj.name = Faker(lang_code).word()
        obj.save()
        return obj

class ProductFactory(DjangoModelFactory):
    class Meta:
        model = Product

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        obj = model_class()
        for lang_code, _ in settings.LANGUAGES:
            with switch_language(obj, lang_code):
                obj.name = Faker(lang_code).sentence(nb_words=3).replace('.', '').capitalize()
                obj.description = Faker(lang_code).paragraph(nb_sentences=3)
        obj.price = fuzzy.FuzzyDecimal(100, 100000, decimal_places=2).evaluate(2, None, False)
        obj.discount_price = fuzzy.FuzzyDecimal(10, obj.price - 1, decimal_places=2).evaluate(2, None, False) if random.random() > 0.5 else None
        obj.currency = random.choice(['RUB', 'USD', 'EUR'])
        obj.category = random.choice(Category.objects.all())
        obj.save() # Save product first to get an ID for ManyToMany
        obj.shops.set(random.sample(list(Shop.objects.all()), random.randint(1, 3)))
        obj.tags.set(random.sample(list(Tag.objects.all()), random.randint(1, 5)))
        obj.save()
        return obj

def download_image(url, filename):
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        path = os.path.join(settings.MEDIA_ROOT, 'products', filename)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return path
    except requests.exceptions.RequestException as e:
        print(f"Error downloading image {url}: {e}")
        return None

def get_unsplash_image_url(query):
    if not UNSPLASH_ACCESS_KEY:
        print("UNSPLASH_ACCESS_KEY not set in .env. Skipping image download.")
        return None
    url = f"https://api.unsplash.com/photos/random?query={query}&client_id={UNSPLASH_ACCESS_KEY}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data['urls']['regular']
    except requests.exceptions.RequestException as e:
        print(f"Error fetching image from Unsplash for query '{query}': {e}")
        return None
    except KeyError:
        print(f"No image found for query '{query}' on Unsplash.")
        return None

class Command(BaseCommand):
    help = 'Generates initial data for categories, shops, tags, products, and product images.'

    def add_arguments(self, parser):
        parser.add_argument('--categories', type=int, default=5, help='Number of categories to create.')
        parser.add_argument('--shops', type=int, default=10, help='Number of shops to create.')
        parser.add_argument('--tags', type=int, default=15, help='Number of tags to create.')
        parser.add_argument('--products', type=int, default=50, help='Number of products to create.')
        parser.add_argument('--output', type=str, default='fixtures/initial_data.json', help='Output fixture file path.')

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Generating initial data...'))

        num_categories = options['categories']
        num_shops = options['shops']
        num_tags = options['tags']
        num_products = options['products']
        output_file = options['output']

        # Clear existing data (optional, for fresh generation)
        ProductImage.objects.all().delete()
        Product.objects.all().delete()
        Category.objects.all().delete()
        Shop.objects.all().delete()
        Tag.objects.all().delete()
        User.objects.filter(is_superuser=False).delete() # Clear non-superuser users

        self.stdout.write(self.style.SUCCESS(f'Creating {num_categories} categories...'))
        categories = [CategoryFactory() for _ in range(num_categories)]

        self.stdout.write(self.style.SUCCESS(f'Creating {num_shops} shops...'))
        shops = [ShopFactory() for _ in range(num_shops)]

        self.stdout.write(self.style.SUCCESS(f'Creating {num_tags} tags...'))
        tags = [TagFactory() for _ in range(num_tags)]

        self.stdout.write(self.style.SUCCESS(f'Creating {num_products} products and images...'))
        products_data = []
        for i in range(num_products):
            product = ProductFactory()
            products_data.append(product)

            # Download 1-3 images for each product
            num_images = random.randint(1, 3)
            for j in range(num_images):
                image_query = f"{product.name} {product.category.name}"
                image_url = get_unsplash_image_url(image_query)
                if image_url:
                    filename = f"{product.slug}_{j}.webp" # Use webp format
                    local_path = download_image(image_url, filename)
                    if local_path:
                        with open(local_path, 'rb') as f:
                            image_file = File(f)
                            ProductImage.objects.create(
                                product=product,
                                image=image_file,
                                alt_text=f"{product.name} image {j+1}",
                                order=j
                            )
                        self.stdout.write(self.style.SUCCESS(f'  Downloaded image for {product.name}: {filename}'))
                    else:
                        self.stdout.write(self.style.WARNING(f'  Failed to download image for {product.name}'))
                else:
                    self.stdout.write(self.style.WARNING(f'  No image URL found for {product.name}'))

        self.stdout.write(self.style.SUCCESS('Data generation complete.'))

        # Optional: Dump data to a JSON fixture
        # This part is commented out as the models are already created in the DB.
        # If you need a JSON fixture, you can uncomment and adjust.
        # from django.core import serializers
        # all_data = list(Category.objects.all()) + list(Shop.objects.all()) + list(Tag.objects.all()) + list(Product.objects.all()) + list(ProductImage.objects.all())
        # with open(output_file, 'w', encoding='utf-8') as f:
        #     json.dump(json.loads(serializers.serialize('json', all_data, indent=4, use_natural_foreign_keys=True, use_natural_primary_keys=True)), f, indent=4, ensure_ascii=False)
        # self.stdout.write(self.style.SUCCESS(f'Data dumped to {output_file}'))