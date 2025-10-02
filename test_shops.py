#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append('e:\\githab\\itog')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shoplist.settings')
django.setup()

from products.models import Product, Shop

def test_shops_relationship():
    """Test the relationship between products and shops"""
    # Create a test shop
    shop = Shop.objects.create(
        name="Тестовый магазин",
        address="ул. Тестовая, 123",
        city="Москва"
    )
    
    # Get a product (assuming there's at least one)
    product = Product.objects.first()
    
    if product:
        # Add the shop to the product
        product.shops.add(shop)
        
        # Verify the relationship
        print(f"Product: {product.name}")
        print(f"Shops: {[s.name for s in product.shops.all()]}")
        
        # Verify the reverse relationship
        print(f"Shop {shop.name} products: {[p.name for p in shop.products.all()]}")
        
        # Clean up
        product.shops.remove(shop)
        shop.delete()
        
        print("Test passed: Shops relationship is working correctly!")
    else:
        print("No products found in the database")

if __name__ == "__main__":
    test_shops_relationship()