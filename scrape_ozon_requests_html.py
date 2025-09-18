"""
Альтернативный парсер Ozon с использованием Requests-HTML
Обходит блокировки через ротацию User-Agent и задержки
"""
import random
import time
from requests_html import HTMLSession
from django.utils import timezone
from products.models import Category, Product, ProductCharacteristic, ProductImage, Seller

session = HTMLSession()
session.headers.update({
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1'
})

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36'
]

def get_page(url):
    """Получение страницы со случайным User-Agent и задержкой"""
    session.headers['User-Agent'] = random.choice(USER_AGENTS)
    time.sleep(random.uniform(1, 3))
    response = session.get(url)
    response.html.render(timeout=20, sleep=random.uniform(2, 4))
    return response.html

def parse_product(url):
    """Парсинг страницы товара"""
    try:
        page = get_page(url)
        
        # Название товара
        name = page.find('h1', first=True).text if page.find('h1') else "Без названия"
        
        # Цена
        price_text = page.xpath("//span[contains(@class, 'tsHeadline500Medium')]//text()")
        price = float(''.join(filter(str.isdigit, price_text[0]))) if price_text else 0
        
        # Описание
        description = ""
        desc_section = page.find('div[data-widget="webDescription"]', first=True)
        if desc_section:
            description = desc_section.text
        
        # Характеристики
        characteristics = []
        char_section = page.find('dl[data-widget="webCharacteristics"]', first=True)
        if char_section:
            for item in char_section.find('div.k6d'):
                name_elem = item.find('dt', first=True)
                value_elem = item.find('dd', first=True)
                if name_elem and value_elem:
                    characteristics.append({
                        "name": name_elem.text.strip(),
                        "value": value_elem.text.strip()
                    })
        
        # Изображения
        images = []
        for img in page.find('img[loading="lazy"]')[:3]:
            src = img.attrs.get('src') or img.attrs.get('data-src')
            if src and 'http' in src:
                images.append(src)
                
        return {
            "name": name,
            "price": price,
            "description": description,
            "characteristics": characteristics,
            "images": images
        }
    except Exception as e:
        print(f"Ошибка парсинга товара: {e}")
        return None

def main():
    # Создаем продавца Ozon
    seller = Seller.objects.get_or_create(company_name="Ozon Marketplace")[0]
    
    # Получаем список категорий
    categories = Category.objects.all()
    
    # Парсим товары для каждой категории
    for category in categories:
        print(f"Парсим категорию: {category.name}")
        
        # Получаем URL категории из модели
        category_url = getattr(category, 'ozon_url', None)
        if not category_url:
            continue
            
        # Получаем страницу категории
        page = get_page(category_url)
        
        # Собираем ссылки на товары
        product_links = []
        for link in page.find('a[href*="/product/"]'):
            href = link.attrs.get('href')
            if href and 'https://www.ozon.ru' not in href:
                href = f'https://www.ozon.ru{href}'
            if href and href not in product_links:
                product_links.append(href)
                
        # Парсим товары
        for url in product_links[:10]:  # Берем первые 10 товаров из категории
            print(f"Парсим товар: {url}")
            product_data = parse_product(url)
            
            if not product_data or not product_data.get('name'):
                continue
                
            # Создаем товар
            product = Product.objects.create(
                name=product_data['name'][:255],
                description=product_data['description'],
                price=product_data['price'],
                category=category,
                seller=seller,
                stock_quantity=random.randint(10, 100)
            )
            
            # Добавляем характеристики
            for char in product_data['characteristics']:
                ProductCharacteristic.objects.create(
                    product=product,
                    name=char['name'][:100],
                    value=char['value'][:255]
                )
            
            print(f"Добавлен товар: {product.name}")

if __name__ == "__main__":
    main()