import os
import django
import requests
import json
from decimal import Decimal
from django.core.files.base import ContentFile

# Настройка Django должна быть ПЕРЕД импортом моделей
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shoplist.settings')
django.setup()

# Импорт моделей ПОСЛЕ настройки Django
from products_simple.models import Category, Product, ProductCharacteristic, ProductImage, Seller, User

def download_image(url):
    """Скачивает изображение по URL и возвращает ContentFile"""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return ContentFile(response.content)
    except Exception as e:
        print(f"Ошибка загрузки изображения: {e}")
        return None

def load_products():
    # URL для получения 100 товаров
    url = "https://dummyjson.com/products?limit=100"
    
    # Получаем данные
    response = requests.get(url)
    if response.status_code != 200:
        print("Ошибка при получении данных от DummyJSON")
        return
    
    data = response.json()
    products = data.get('products', [])
    print(f"Получено {len(products)} товаров")
    
    # Создаем пользователя и продавца по умолчанию
    user, _ = User.objects.get_or_create(
        username="dummy_seller",
        defaults={
            'email': 'dummy@example.com',
            'role': 'seller',
            'first_name': 'Dummy',
            'last_name': 'Seller'
        }
    )
    if not user.password:
        user.set_password('password123')
        user.save()
    
    seller, _ = Seller.objects.get_or_create(
        user=user,
        defaults={
            'company_name': "Dummy Seller",
            'description': "Продавец демо-товаров"
        }
    )
    
    # Обрабатываем каждый товар
    for i, product_data in enumerate(products):
        # Создаем или получаем категорию
        category_name = product_data.get('category', 'Uncategorized')
        category, _ = Category.objects.get_or_create(
            name=category_name,
            defaults={'description': f"Категория {category_name}"}
        )
        
        # Рассчитываем цену со скидкой
        price = Decimal(str(product_data.get('price', 0)))
        discount_percentage = Decimal(str(product_data.get('discountPercentage', 0)))
        discount_price = price * (1 - discount_percentage / 100) if discount_percentage else None
        
        # Создаем товар
        product = Product.objects.create(
            name=product_data.get('title', f"Товар {i+1}")[:255],
            description=product_data.get('description', '')[:500],
            price=price,
            discount_price=discount_price,
            category=category,
            seller=seller,
            brand=product_data.get('brand', '')[:100],
            stock_quantity=product_data.get('stock', 0),
            rating=Decimal(str(product_data.get('rating', 0))),
            weight=product_data.get('weight', None),
            dimensions=product_data.get('dimensions', {}),
            warranty=product_data.get('warrantyInformation', '')[:100]
        )
        
        # Добавляем характеристики
        characteristics = []
        # Добавляем бренд как характеристику
        if product.brand:
            characteristics.append({'name': 'Бренд', 'value': product.brand})
        
        # Добавляем другие характеристики
        if 'dimensions' in product_data:
            dim = product_data['dimensions']
            characteristics.append({'name': 'Ширина', 'value': f"{dim.get('width', 0)} см"})
            characteristics.append({'name': 'Высота', 'value': f"{dim.get('height', 0)} см"})
            characteristics.append({'name': 'Глубина', 'value': f"{dim.get('depth', 0)} см"})
        
        # Сохраняем характеристики
        for char in characteristics:
            ProductCharacteristic.objects.create(
                product=product,
                name=char['name'][:100],
                value=char['value'][:255]
            )
        
        # Добавляем изображения
        images = product_data.get('images', [])
        for j, img_url in enumerate(images[:3]):  # Берем первые 3 изображения
            image_data = download_image(img_url)
            if image_data:
                img = ProductImage(
                    product=product,
                    alt_text=f"{product.name} - изображение {j+1}",
                    is_primary=(j == 0),
                    order=j
                )
                img.image.save(
                    f"product_{product.id}_img_{j}.jpg", 
                    image_data,
                    save=True
                )
        
        print(f"Добавлен товар: {product.name}")
    
    print("Загрузка товаров завершена!")

if __name__ == "__main__":
    load_products()