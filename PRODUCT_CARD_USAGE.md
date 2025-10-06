# Использование компонента карточки товара

## Описание
Компонент `products/templates/components/product_card.html` - это единый шаблонизированный компонент для отображения карточек товаров во всем проекте.

## Структура компонента
- **Фиксированная ширина**: 270px
- **Высота изображения**: 360px
- **Адаптивный дизайн**: подходит для всех устройств
- **Единообразный стиль**: соответствует дизайн-системе проекта

## Как использовать

### В шаблонах Django
```django
{% for product in products %}
    {% include 'components/product_card.html' %}
{% endfor %}
```

### Контейнер для карточек
Используйте flexbox контейнер с отступами:

```html
<div class="flex flex-wrap gap-6 justify-start">
    {% for product in products %}
        {% include 'components/product_card.html' %}
    {% endfor %}
</div>
```

## Примеры использования в проекте

### 1. Главная страница (`index_ozon.html`)
```django
<div id="products-grid" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
    {% for product in products %}
        {% include 'components/product_card.html' %}
    {% endfor %}
</div>
```

### 2. Страница товара - похожие товары (`product_detail.html`)
```django
<div class="flex flex-wrap gap-6 justify-start">
    {% for product in related_products %}
        {% include 'components/product_card.html' %}
    {% endfor %}
</div>
```

### 3. Страница категории
```django
<div class="flex flex-wrap gap-6 justify-start">
    {% for product in category_products %}
        {% include 'components/product_card.html' %}
    {% endfor %}
</div>
```

## CSS стили

### Основные стили (уже включены в base_ozon.html)
```css
.product-card {
    width: 270px;
    background: white;
    border-radius: 8px;
    border: 1px solid #e5e7eb;
    overflow: hidden;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    transition: all 0.3s ease;
    display: flex;
    flex-direction: column;
    flex-shrink: 0;
}

.product-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
    border-color: #005bff;
}
```

### Контейнер с отступами
```css
.flex.flex-wrap.gap-6 {
    gap: 1.5rem !important;
}
```

## Функциональность

### Включенные функции:
- ✅ Отображение изображения товара
- ✅ Название товара с ссылкой на детальную страницу
- ✅ Рейтинг со звездами
- ✅ Цена (обычная и со скидкой)
- ✅ Статус наличия
- ✅ Кнопка "Добавить в корзину"
- ✅ Кнопка "Избранное"
- ✅ Бейдж скидки
- ✅ Название продавца

### JavaScript функции:
- `addToCart(productId)` - добавление в корзину
- `toggleFavorite(productId)` - добавление/удаление из избранного

## Требования к данным

Компонент ожидает объект `product` со следующими полями:
- `id` - ID товара
- `name` - название товара
- `price` - цена товара
- `discount_price` - цена со скидкой (опционально)
- `discount_percentage` - процент скидки (опционально)
- `stock_quantity` - количество на складе
- `rating` - рейтинг товара
- `reviews_count` - количество отзывов
- `images.first` - первое изображение товара
- `seller.company_name` - название продавца

## Преимущества использования компонента

1. **Единообразие**: все карточки товаров выглядят одинаково
2. **Легкость поддержки**: изменения в одном файле применяются везде
3. **Производительность**: оптимизированная структура и стили
4. **Адаптивность**: работает на всех устройствах
5. **Функциональность**: включает все необходимые элементы

## Миграция существующих карточек

Если у вас есть старые карточки товаров, замените их на:
```django
{% include 'components/product_card.html' %}
```

И используйте flexbox контейнер вместо grid для правильных отступов.