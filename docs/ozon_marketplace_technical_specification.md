# Финальное техническое задание для маркетплейса Ozon-style

## 1. Введение

### 1.1. О заказчике
**Компания**: RetailNet Solutions — локальный IT-интегратор для розничных сетей.
**Клиенты**: Магазины электроники, одежды и продуктов, желающие публиковать ассортимент и адреса без полноценного интернет-магазина.
**Цель заказчика**: Создать высокопроизводительный, масштабируемый и визуально привлекательный маркетплейс с продвинутыми админ-панелями, мультиязычностью, интеграциями и аналитикой.

### 1.2. Цель проекта
Разработать веб-маркетплейс на Django с REST API, обеспечивающий:

- **Для покупателей**: Просмотр товаров с высококачественными изображениями, ценами, характеристиками, отзывами и рейтингами
- **Для продавцов**: Управление товарами, заказами, аналитикой продаж, комиссиями
- **Для администраторов**: Полный контроль над платформой, модерация, аналитика
- **Мультиязычность**: Русский, английский, арабский (включая RTL)
- **Интеграции**: Карты, платежи, уведомления, аналитика
- **Предзагруженная база**: Реалистичные данные для демонстрации

## 2. Описание проекта

### 2.1. Основные функции

#### Для покупателей:
- Просмотр товаров с WebP-изображениями (ленивая загрузка, зум)
- Полнотекстовый поиск и фильтрация (категории, цены, продавцы, характеристики, рейтинги)
- Добавление в избранное и корзину
- Система отзывов и рейтингов
- Мультиязычный интерфейс (русский, английский, арабский)
- Интерактивная карта для адресов магазинов
- Система заказов и отслеживания

#### Для продавцов:
- Управление товарами через фронтенд-панель (CRUD, массовые действия)
- Управление заказами и их статусами
- Аналитика продаж и комиссий
- Управление характеристиками товаров
- Уведомления о действиях (email, push)

#### Для администраторов:
- Полный доступ через Django admin и фронтенд-панель
- Модерация товаров и продавцов
- Управление комиссиями и настройками платформы
- Аналитика: просмотры, заказы, конверсии, поведение пользователей

#### REST API:
- Версионированные эндпоинты (/api/v1/)
- Документация через Swagger/OpenAPI
- Поддержка кэширования и throttling
- JWT аутентификация

### 2.2. Целевая аудитория

- **Покупатели**: Пользователи, ищущие товары и совершающие покупки
- **Продавцы**: Владельцы магазинов, управляющие ассортиментом и заказами
- **Администраторы**: Сотрудники RetailNet Solutions, управляющие платформой

## 3. Функциональные требования

### 3.1. Главная страница

#### Список товаров:
- Сетка: 4 колонки (десктоп), 2 (планшеты), 1 (мобильные)
- Карточка: название, цена (с учетом скидок), рейтинг, продавец, миниатюра (WebP), эффект наведения
- Слайдер с лайфстайл-фотографиями (3–5 изображений)
- Сортировка по популярности, цене, рейтингу, дате добавления

#### Поиск и фильтрация:
- Полнотекстовый поиск (PostgreSQL SearchVector) по названию, описанию, характеристикам
- Фильтры: категории, ценовой диапазон, продавцы, характеристики, рейтинг, теги
- AJAX-фильтрация с индикатором загрузки
- Обработка пустых состояний ("Товары не найдены")

#### Пагинация:
- 12 товаров на страницу, бесконечная прокрутка (опционально)

#### Навигация:
- Липкое меню: категории, язык, вход/регистрация, корзина
- Боковая панель фильтров (сворачиваемая, с ARIA-атрибутами)

### 3.2. Страница товара

#### Элементы:
- Название (H1, SEO-оптимизированное)
- Галерея изображений (PhotoSwipe, WebP, зум)
- Цена (мультивалютность: RUB, USD, скидки)
- Характеристики товара (таблица)
- Описание (markdown, мультиязычное)
- Информация о продавце
- Отзывы и рейтинги
- Таблица магазинов с картой (Google Maps/OpenStreetMap)
- Теги (например, "новинка", "хит")
- Кнопки "Добавить в корзину", "Добавить в избранное"

#### Навигация:
- Кнопка "Назад"
- Похожие товары (по категории/характеристикам)
- Рекомендации

### 3.3. Система заказов

#### Корзина:
- Добавление/удаление товаров
- Изменение количества
- Расчет общей стоимости
- Применение скидок и промокодов

#### Оформление заказа:
- Выбор способа доставки
- Выбор адреса доставки
- Выбор способа оплаты
- Подтверждение заказа

#### Управление заказами:
- История заказов
- Отслеживание статуса
- Возвраты и обмены

### 3.4. Аутентификация и роли

#### Регистрация:
- Поля: username, email, пароль (мин. 12 символов), подтверждение, политика конфиденциальности
- Подтверждение email, восстановление пароля
- Раздельная регистрация для покупателей и продавцов

#### Вход/выход:
- Форма: email/username, пароль, "Запомнить меня"
- 2FA (TOTP через django-two-factor-auth)

#### Роли:
- **Покупатель**: Просмотр, фильтрация, избранное, корзина, заказы
- **Продавец**: CRUD товары, управление заказами, аналитика
- **Администратор**: Полный доступ, модерация, аналитика

#### Ограничение доступа:
- LoginRequiredMixin, PermissionRequiredMixin
- Проверка прав на товары и заказы

### 3.5. Управление товарами

#### Фронтенд-панель продавца:
- Доступ через /seller/
- Таблица: название, цена, категория, характеристики, статус, действия
- Массовые действия: удаление, смена категории/статуса
- Аналитика: просмотры, заказы, конверсии (Chart.js)
- Экспорт в CSV/Excel
- Уведомления о действиях (email, push)

#### Добавление/редактирование:
- Форма: название, описание (markdown), цена, скидка, категория, характеристики, изображения
- Предпросмотр изображений, защита от конфликтов редактирования
- Валидация характеристик

#### Удаление:
- Модальное окно (Alpine.js)

#### Django Admin:
- Кастомизация через django-admin-interface
- Фильтры, поиск, массовые действия, история изменений

### 3.6. REST API

#### Эндпоинты:
- `GET /api/v1/products/` — список (пагинация, фильтрация)
- `GET /api/v1/products/<id>/` — детали
- `POST/PUT/DELETE /api/v1/products/` — CRUD (для продавцов/админов)
- `GET /api/v1/categories/`, `GET /api/v1/sellers/` — списки
- `GET /api/v1/orders/` — заказы
- `POST /api/v1/cart/` — корзина

#### Аутентификация: 
- JWT с refresh-токенами

#### Формат ошибок: 
- JSON:API

#### Документация: 
- Swagger/OpenAPI (drf-spectacular)

#### Кэширование: 
- Redis, инвалидация по событиям

#### Throttling: 
- Ограничение запросов по ролям

### 3.7. Предзагруженные данные

#### Объем:
- 10 категорий
- 20 продавцов
- 100 товаров (с характеристиками, отзывами, 1–5 изображениями)
- 50 отзывов
- 30 заказов

#### Формат: 
- JSON-фикстура, изображения через Unsplash API
- Генерация: factory-boy для случайных данных
- Загрузка: `python manage.py loaddata fixtures/initial_data.json`

## 4. Нефункциональные требования

### Технологии:
- **Язык**: Python 3.10+
- **Фреймворк**: Django 4.x, Django REST Framework
- **Шаблоны**: Django Templates, Tailwind CSS
- **База данных**: PostgreSQL
- **Хранение изображений**: MEDIA_ROOT (разработка), Cloudinary (продакшен)
- **Форматы**: WebP, JPEG, автоматический ресайз (1920x1080)

### Дизайн:
- **Стиль**: Минималистичный в стиле Ozon
- **Цвета**: Белый фон, серые акценты, синий CTA (#005BFF)
- **Шрифты**: Inter, Roboto, Noto Sans Arabic (для RTL)
- **Анимации**: Tailwind, ленивая загрузка
- **Доступность**: WCAG 2.1 (AA), ARIA-атрибуты

### Производительность:
- **API**: < 300 мс для сложных запросов
- **Поддержка**: 2000 одновременных пользователей, 1000 RPS
- **Кэширование**: Redis, инвалидация по событиям

### Безопасность:
- **Стандарты**: OWASP Top 10, rate limiting, 2FA (TOTP)
- **Защита**: Secure cookies, CSP, HSTS
- **Пароли**: Минимальная длина 12 символов

### Тестирование:
- **Покрытие**: ≥ 85% (pytest, coverage)
- **E2E-тесты**: Cypress
- **Нагрузочные**: Locust, 1000 RPS

### Код:
- **Стандарты**: PEP 8, type hints, сервисный слой, репозитории

### Локализация:
- **Языки**: Русский, английский, арабский (django-parler)
- **Форматирование**: Даты, числа, валюты

### Инфраструктура:
- **Контейнеризация**: Docker, Kubernetes (zero-downtime деплой)
- **CI/CD**: GitHub Actions
- **Мониторинг**: Sentry, Prometheus, Grafana
- **Логирование**: ELK
- **Резервное копирование**: S3, pg_dump

## 5. Стек технологий

### Backend:
- Django 4.x, Django REST Framework, Celery
- PostgreSQL, Redis
- Pillow, django-crispy-forms, django-filter, django-parler
- django-admin-interface, djangorestframework-simplejwt, drf-spectacular
- django-two-factor-auth, django-ratelimit, django-notifications
- factory-boy, pytest, cypress

### Frontend:
- Django Templates, Tailwind CSS, Alpine.js, Chart.js, PhotoSwipe
- HTMX для AJAX-запросов

### Инфраструктура:
- Docker, Kubernetes, Nginx, Gunicorn
- Cloudinary (CDN), Unsplash API
- Sentry, Prometheus, Grafana, ELK

## 6. Модели данных

### 6.1. Модель Seller (Продавец)
```python
from django.db import models
from django.contrib.auth.models import User

class Seller(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='seller_profile')
    company_name = models.CharField(max_length=255, verbose_name="Название компании")
    description = models.TextField(blank=True, verbose_name="Описание")
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=5.00, verbose_name="Комиссия %")
    is_verified = models.BooleanField(default=False, verbose_name="Верифицирован")
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00, verbose_name="Рейтинг")
    total_sales = models.PositiveIntegerField(default=0, verbose_name="Всего продаж")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата регистрации")
    
    def __str__(self):
        return self.company_name
```

### 6.2. Модель ProductCharacteristic (Характеристика товара)
```python
class ProductCharacteristic(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='characteristics')
    name = models.CharField(max_length=100, verbose_name="Название характеристики")
    value = models.CharField(max_length=255, verbose_name="Значение")
    unit = models.CharField(max_length=20, blank=True, verbose_name="Единица измерения")
    
    def __str__(self):
        return f"{self.name}: {self.value}"
```

### 6.3. Модель Order (Заказ)
```python
class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Ожидает подтверждения'),
        ('confirmed', 'Подтвержден'),
        ('processing', 'В обработке'),
        ('shipped', 'Отправлен'),
        ('delivered', 'Доставлен'),
        ('cancelled', 'Отменен'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    order_number = models.CharField(max_length=20, unique=True, verbose_name="Номер заказа")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Общая сумма")
    shipping_address = models.TextField(verbose_name="Адрес доставки")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    
    def __str__(self):
        return f"Заказ {self.order_number}"
```

### 6.4. Модель OrderItem (Позиция заказа)
```python
class OrderItem(models.Model):
    order = models.ForeignKey('Order', on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(verbose_name="Количество")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена за единицу")
    
    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
```

### 6.5. Модель Review (Отзыв)
```python
class Review(models.Model):
    RATING_CHOICES = [(i, i) for i in range(1, 6)]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveIntegerField(choices=RATING_CHOICES, verbose_name="Оценка")
    title = models.CharField(max_length=200, verbose_name="Заголовок отзыва")
    text = models.TextField(verbose_name="Текст отзыва")
    is_verified_purchase = models.BooleanField(default=False, verbose_name="Подтвержденная покупка")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    
    def __str__(self):
        return f"Отзыв на {self.product.name} от {self.user.username}"
```

### 6.6. Обновленная модель Product
```python
class Product(TranslatableModel):
    translations = TranslatedFields(
        name=models.CharField(max_length=255, verbose_name="Название товара"),
        description=models.TextField(blank=True, verbose_name="Описание")
    )
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="Цена со скидкой")
    currency = models.CharField(max_length=3, default='RUB', verbose_name="Валюта")
    category = models.ForeignKey('Category', on_delete=models.CASCADE, related_name='products', verbose_name="Категория")
    seller = models.ForeignKey('Seller', on_delete=models.CASCADE, related_name='products', verbose_name="Продавец")
    shops = models.ManyToManyField('Shop', related_name='products', verbose_name="Магазины")
    tags = models.ManyToManyField('Tag', blank=True, verbose_name="Теги")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    views_count = models.PositiveIntegerField(default=0, verbose_name="Количество просмотров")
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00, verbose_name="Рейтинг")
    reviews_count = models.PositiveIntegerField(default=0, verbose_name="Количество отзывов")
    search_vector = SearchVectorField(null=True, verbose_name="Вектор поиска")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    
    def __str__(self):
        return self.name
```

## 7. План разработки

### Этап 1: Базовая настройка и модели
- Создать новые модели (Seller, ProductCharacteristic, Order, OrderItem, Review)
- Обновить существующие модели
- Создать миграции
- Настроить админ-панель

### Этап 2: Система продавцов
- Реализовать регистрацию и управление продавцами
- Создать панель продавца
- Настроить комиссии и аналитику

### Этап 3: Система заказов
- Реализовать корзину покупок
- Создать процесс оформления заказа
- Добавить управление заказами

### Этап 4: Система отзывов и рейтингов
- Реализовать добавление отзывов
- Создать систему рейтингов
- Добавить модерацию отзывов

### Этап 5: Характеристики товаров
- Создать систему характеристик
- Добавить фильтрацию по характеристикам
- Реализовать управление характеристиками

### Этап 6: Тестовые данные
- Создать команду генерации данных
- Загрузить товары с изображениями
- Добавить отзывы и заказы

### Этап 7: Тестирование и документация
- Написать тесты
- Создать документацию
- Провести нагрузочное тестирование

## 8. Критерии успешного выполнения

- **Покупатель**: мультиязычный интерфейс, поиск, фильтрация, корзина, заказы, отзывы
- **Продавец**: управление товарами, заказами, аналитика, комиссии
- **Администратор**: полный доступ, модерация, аналитика
- **API**: версионированное, документированное, < 300 мс
- **Дизайн**: WCAG 2.1, RTL, адаптивный в стиле Ozon
- **Данные**: 100+ товаров, 10 категорий, 20 продавцов, отзывы
- **Тестирование**: покрытие ≥ 85%, E2E, нагрузочные тесты
- **Код**: PEP 8, сервисный слой, type hints
- **Деплой**: zero-downtime, мониторинг, логирование

## 9. Структура проекта

```
ozon_marketplace/
├── manage.py
├── ozon_marketplace/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
├── products/
│   ├── __init__.py
│   ├── admin.py
│   ├── api/
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   ├── forms.py
│   ├── management/
│   │   ├── commands/
│   │   │   ├── generate_marketplace_data.py
│   ├── migrations/
│   ├── models.py
│   ├── services/
│   │   ├── product_service.py
│   │   ├── order_service.py
│   │   ├── review_service.py
│   ├── repositories/
│   │   ├── product_repository.py
│   │   ├── order_repository.py
│   ├── templates/
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── product_detail.html
│   │   ├── seller_dashboard.html
│   │   ├── cart.html
│   │   ├── order_detail.html
│   ├── tests/
│   │   ├── test_models.py
│   │   ├── test_views.py
│   │   ├── test_api.py
│   ├── urls.py
│   ├── views.py
├── media/
│   ├── products/
│   ├── sellers/
├── static/
│   ├── css/
│   ├── js/
├── fixtures/
│   ├── marketplace_data.json
├── docker/
│   ├── Dockerfile
│   ├── docker-compose.yml
├── README.md
├── requirements.txt
```

## 10. Дополнительные замечания

- **SEO**: Мета-теги, sitemap.xml, robots.txt, canonical URLs
- **Мониторинг**: Метрики здоровья (uptime, latency) через Prometheus
- **Масштабируемость**: Celery для асинхронных задач (уведомления, аналитика)
- **Документация**: Архитектурные диаграммы (C4 model) в `/docs/`
- **Безопасность**: Валидация данных, защита от SQL-инъекций, XSS
- **Производительность**: Кэширование запросов, оптимизация изображений
- **Доступность**: Поддержка скрин-ридеров, клавиатурная навигация
