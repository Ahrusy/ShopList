# Финальное улучшенное техническое задание для проекта ShopList

## 1. Введение
### 1.1. О заказчике

Компания: RetailNet Solutions — локальный IT-интегратор для розничных сетей.
Клиенты: Магазины электроники, одежды и продуктов, желающие публиковать ассортимент и адреса без полноценного интернет-магазина.
Цель заказчика: Создать высокопроизводительный, масштабируемый и визуально привлекательный сайт с продвинутыми админ-панелями, мультиязычностью, интеграциями и аналитикой.

### 1.2. Цель проекта
Разработать веб-сайт на Django с REST API, обеспечивающий:

*   Просмотр товаров с высококачественными изображениями, ценами и адресами магазинов (с картой).
*   Полнотекстовый поиск, фильтрацию и мультиязычность (включая RTL).
*   Управление товарами через интуитивные фронтенд- и бэкенд-админки с аналитикой.
*   Интеграцию с картами, уведомлениями и внешними аналитическими сервисами.
*   Предзагруженную базу данных с реалистичными данными для демонстрации.

## 2. Описание проекта
### 2.1. Основные функции

**Для пользователей:**
*   Просмотр товаров с WebP-изображениями (ленивая загрузка, зум).
*   Полнотекстовый поиск и фильтрация (категории, цены, магазины, теги).
*   Добавление в избранное, мультиязычный интерфейс (русский, английский, арабский).
*   Интерактивная карта для адресов магазинов.

**Для менеджеров:**
*   Управление товарами своих магазинов через фронтенд-админку (CRUD, массовые действия).
*   Уведомления о действиях (email, push).

**Для администраторов:**
*   Полный доступ через Django admin и фронтенд-админку.
*   Аналитика: просмотры, избранное, конверсии, поведение пользователей.

**REST API:**
*   Версионированные эндпоинты (`/api/v1/`).
*   Документация через Swagger/OpenAPI.
*   Поддержка кэширования и throttling.

### 2.2. Целевая аудитория

*   **Пользователи**: Покупатели, ищущие товары и адреса магазинов.
*   **Менеджеры**: Сотрудники магазинов, управляющие ассортиментом.
*   **Администраторы**: Сотрудники RetailNet Solutions, управляющие системой и анализирующие данные.

## 3. Функциональные требования
### 3.1. Главная страница

**Список товаров:**
*   Сетка: 4 колонки (десктоп), 2 (планшеты), 1 (мобильные).
*   Карточка: название, цена (с учетом скидок), миниатюра (WebP), эффект наведения.
*   Слайдер с лайфстайл-фотографиями (3–5 изображений).

**Поиск и фильтрация:**
*   Полнотекстовый поиск (PostgreSQL SearchVector) по названию, описанию, тегам.
*   Фильтры: категории, ценовой диапазон, магазины, теги (AJAX, индикатор загрузки).
*   Обработка пустых состояний ("Товары не найдены").

**Пагинация:**
*   12 товаров на страницу, бесконечная прокрутка (опционально).

**Навигация:**
*   Липкое меню: категории, язык, вход/регистрация.
*   Боковая панель фильтров (сворачиваемая, с ARIA-атрибутами).

### 3.2. Страница товара

**Элементы:**
*   Название (H1, SEO-оптимизированное).
*   Галерея изображений (PhotoSwipe, WebP, зум).
*   Цена (мультивалютность: RUB, USD, скидки).
*   Описание (markdown, мультиязычное через django-parler).
*   Таблица магазинов с картой (Google Maps/OpenStreetMap).
*   Теги (например, "новинка", "хит").
*   Кнопка "Добавить в избранное".

**Навигация:**
*   Кнопка "Назад".
*   Похожие товары (по категории/тегам).

### 3.3. Аутентификация и роли

**Регистрация:**
*   Поля: username, email, пароль (мин. 12 символов), подтверждение, политика конфиденциальности.
*   Подтверждение email, восстановление пароля.

**Вход/выход:**
*   Форма: email/username, пароль, "Запомнить меня".
*   2FA (TOTP через django-two-factor-auth).

**Роли:**
*   Пользователь: Просмотр, фильтрация, избранное.
*   Менеджер: CRUD товары своих магазинов.
*   Администратор: Полный доступ, аналитика.

**Ограничение доступа:**
*   LoginRequiredMixin, PermissionRequiredMixin.
*   Проверка магазинов менеджера.

### 3.4. Управление товарами

**Фронтенд-админка:**
*   Доступ через `/manager/`.
*   Таблица: название, цена, категория, теги, магазины, действия.
*   Массовые действия: удаление, смена категории/тегов.
*   Аналитика: просмотры, избранное, конверсии (Chart.js).
*   Экспорт в CSV/Excel.
*   Уведомления о действиях (email, push через django-notifications).

**Добавление/редактирование:**
*   Форма: название, описание (markdown), цена, скидка, категория, теги, магазины, изображения.
*   Предпросмотр изображений, защита от конфликтов редактирования.

**Удаление:**
*   Модальное окно (Alpine.js).

**Django Admin:**
*   Кастомизация через django-admin-interface.
*   Фильтры, поиск, массовые действия, история изменений.

### 3.5. REST API

**Эндпоинты:**
*   `GET /api/v1/products/` — список (пагинация, фильтрация).
*   `GET /api/v1/products/<id>/` — детали.
*   `POST/PUT/DELETE /api/v1/products/` — CRUD (для менеджеров/админов).
*   `GET /api/v1/categories/`, `GET /api/v1/shops/` — списки.

**Аутентификация:** JWT с refresh-токенами.
**Формат ошибок:** JSON:API.
**Документация:** Swagger/OpenAPI (drf-spectacular).
**Кэширование:** Redis, инвалидация по событиям.
**Throttling:** Ограничение запросов по ролям.

### 3.6. Предзагруженные данные

**Объем:**
*   5 категорий.
*   10 магазинов (по 2 в 5 городах).
*   50 товаров (с тегами, скидками, 1–3 изображениями).

**Формат:** JSON-фикстура, изображения через Unsplash API.
**Генерация:** factory-boy для случайных данных.
**Загрузка:** `python manage.py generate_fixtures` (кастомная команда).

## 4. Нефункциональные требования

**Язык:** Python 3.10+.
**Фреймворк:** Django 4.x, Django REST Framework.
**Шаблоны:** Django Templates, Tailwind CSS.
**База данных:** PostgreSQL.
**Хранение изображений:**
*   `MEDIA_ROOT` (разработка), Cloudinary (продакшен).
*   Форматы: WebP, JPEG, автоматический ресайз (1920x1080).

**Дизайн:**
*   Минималистичный: белый фон, серые акценты, зеленый CTA.
*   Шрифты: Inter, Roboto, Noto Sans Arabic (для RTL).
*   Анимации: Tailwind, ленивая загрузка.
*   Доступность: WCAG 2.1 (AA), ARIA-атрибуты.

**Производительность:**
*   API: < 300 мс для сложных запросов.
*   Поддержка 2000 одновременных пользователей, 1000 RPS.
*   Кэширование: Redis, инвалидация по событиям.

**Безопасность:**
*   OWASP Top 10, rate limiting, 2FA (TOTP).
*   Secure cookies, CSP, HSTS.
*   Минимальная длина пароля: 12 символов.

**Тестирование:**
*   Покрытие: ≥ 85% (pytest, coverage).
*   E2E-тесты (Cypress), нагрузочные (Locust, 1000 RPS).

**Код:**
*   PEP 8, type hints, сервисный слой, репозитории.

**Локализация:**
*   Русский, английский, арабский (django-parler).
*   Локализация дат, чисел, валют.

**Инфраструктура:**
*   Docker, Kubernetes (zero-downtime деплой).
*   CI/CD: GitHub Actions.
*   Мониторинг: Sentry, Prometheus, Grafana.
*   Логирование: ELK.
*   Резервное копирование: S3, pg_dump.

## 5. Стек технологий

**Backend:** Django 4.x, Django REST Framework, Celery.
**Frontend:** Django Templates, Tailwind CSS, Alpine.js, Chart.js, PhotoSwipe.
**База данных:** PostgreSQL, Redis.
**Библиотеки:**
*   Pillow, django-crispy-forms, django-filter, django-parler.
*   django-admin-interface, djangorestframework-simplejwt, drf-spectacular.
*   django-two-factor-auth, django-ratelimit, django-notifications.
*   factory-boy, pytest, cypress.

**Инфраструктура:**
*   Docker, Kubernetes, Nginx, Gunicorn.
*   Cloudinary (CDN), Unsplash API.
*   Sentry, Prometheus, Grafana, ELK.

## 6. Модели данных
### 6.1. Модель Category
```python
from django.db import models
from django.utils.text import slugify
from parler.models import TranslatableModel, TranslatedFields
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class Category(TranslatableModel):
    translations = TranslatedFields(
        name=models.CharField(max_length=100, verbose_name=_("Название")),
        slug=models.SlugField(max_length=100, unique=True, verbose_name=_("Слаг"))
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Дата создания"))

    def save(self, *args, **kwargs):
        if not self.pk: # Only generate slug on creation
            for lang_code, _ in settings.LANGUAGES:
                self.set_current_language(lang_code)
                if not self.slug:
                    self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Категория")
        verbose_name_plural = _("Категории")
        ordering = ['translations__name']
```

### 6.2. Модель Shop
```python
from django.db import models
from parler.models import TranslatableModel, TranslatedFields
from django.utils.translation import gettext_lazy as _

class Shop(TranslatableModel):
    translations = TranslatedFields(
        name=models.CharField(max_length=255, verbose_name=_("Название")),
        address=models.TextField(verbose_name=_("Адрес")),
        city=models.CharField(max_length=100, verbose_name=_("Город"))
    )
    latitude = models.FloatField(blank=True, null=True, verbose_name=_("Широта"))
    longitude = models.FloatField(blank=True, null=True, verbose_name=_("Долгота"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Дата создания"))

    def __str__(self):
        return f"{self.name}, {self.city}"

    class Meta:
        verbose_name = _("Магазин")
        verbose_name_plural = _("Магазины")
        ordering = ['translations__city', 'translations__name']
```

### 6.3. Модель Product
```python
from django.db import models
from django.contrib.postgres.search import SearchVectorField, SearchVector
from django.db.models.signals import post_save
from django.dispatch import receiver
from parler.models import TranslatableModel, TranslatedFields
from django.utils.translation import gettext_lazy as _
from django.conf import settings

class Product(TranslatableModel):
    translations = TranslatedFields(
        name=models.CharField(max_length=255, verbose_name=_("Название товара")),
        description=models.TextField(blank=True, verbose_name=_("Описание"))
    )
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Цена"))
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name=_("Цена со скидкой"))
    currency = models.CharField(max_length=3, default='RUB', verbose_name=_("Валюта"))
    category = models.ForeignKey('Category', on_delete=models.CASCADE, related_name='products', verbose_name=_("Категория"))
    shops = models.ManyToManyField('Shop', related_name='products', verbose_name=_("Магазины"))
    tags = models.ManyToManyField('Tag', blank=True, verbose_name=_("Теги"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Дата создания"))
    views_count = models.PositiveIntegerField(default=0, verbose_name=_("Количество просмотров"))
    search_vector = SearchVectorField(null=True, verbose_name=_("Вектор поиска"))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Товар")
        verbose_name_plural = _("Товары")
        ordering = ['translations__name']
        indexes = [models.Index(fields=['search_vector'])]

@receiver(post_save, sender=Product)
def update_product_search_vector(sender, instance, **kwargs):
    # Avoid recursion when saving the instance itself
    if kwargs.get('update_fields') is not None and 'search_vector' in kwargs['update_fields']:
        return

    search_text = []
    for lang_code, _ in settings.LANGUAGES:
        instance.set_current_language(lang_code)
        search_text.append(instance.name)
        search_text.append(instance.description)

    from django.contrib.postgres.search import SearchVector
    instance.search_vector = SearchVector(*search_text)
    instance.save(update_fields=['search_vector'])
```

### 6.4. Модель ProductImage
```python
from django.db import models
from django.utils.translation import gettext_lazy as _

class ProductImage(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='images', verbose_name=_("Товар"))
    image = models.ImageField(upload_to='products/%Y/%m/%d/', blank=True, verbose_name=_("Изображение"))
    alt_text = models.CharField(max_length=255, blank=True, verbose_name=_("Альтернативный текст"))
    order = models.PositiveIntegerField(default=0, verbose_name=_("Порядок"))

    def __str__(self):
        return self.alt_text or self.image.name

    class Meta:
        verbose_name = _("Изображение товара")
        verbose_name_plural = _("Изображения товаров")
        ordering = ['order']
```

### 6.5. Модель Tag
```python
from django.db import models
from parler.models import TranslatableModel, TranslatedFields
from django.utils.translation import gettext_lazy as _

class Tag(TranslatableModel):
    translations = TranslatedFields(
        name=models.CharField(max_length=50, unique=True, verbose_name=_("Название тега"))
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Тег")
        verbose_name_plural = _("Теги")
        ordering = ['translations__name']
```

### 6.6. Модель User
```python
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    ROLE_CHOICES = (
        ('user', _('Пользователь')),
        ('manager', _('Менеджер')),
        ('admin', _('Администратор')),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user', verbose_name=_("Роль"))
    favorites = models.ManyToManyField('Product', related_name='favorited_by', blank=True, verbose_name=_("Избранные товары"))
    shops = models.ManyToManyField('Shop', related_name='managers', blank=True, verbose_name=_("Управляемые магазины"))

    def __str__(self):
        return self.username
```

## 7. План разработки
**Этап 1: Базовая настройка**
*   Создать проект, приложение products.
*   Настроить settings.py: PostgreSQL, Redis, AUTH_USER_MODEL, библиотеки.
*   Реализовать модели, миграции.

**Этап 2: Аутентификация и API**
*   Настроить User, 2FA (TOTP), восстановление пароля.
*   Реализовать API (`/api/v1/`) с JWT, Swagger.
*   Добавить throttling, кэширование.

**Этап 3: Список и карточка товара**
*   Главная страница: ListView, полнотекстовый поиск, фильтры, бесконечная прокрутка.
*   Страница товара: DetailView, галерея, карта, теги.

**Этап 4: Админка и CRUD**
*   Фронтенд-админка: таблица, массовые действия, экспорт, уведомления.
*   Django admin: кастомизация, аналитика, история изменений.
*   Формы: предпросмотр, защита от конфликтов.

**Этап 5: Дизайн**
*   Подключить Tailwind CSS, Alpine.js, PhotoSwipe.
*   Реализовать адаптивные шаблоны (WCAG 2.1, RTL).
*   Добавить карты, анимации, ленивую загрузку.

**Этап 6: Данные и тестирование**
*   Генерация фикстур (factory-boy, Unsplash API).
*   Тесты: модульные, E2E (Cypress), нагрузочные (Locust, 1000 RPS).

**Этап 7: Деплой**
*   Docker, Kubernetes, zero-downtime деплой.
*   CI/CD: GitHub Actions.
*   Мониторинг: Sentry, Prometheus, Grafana.
*   Резервное копирование: S3, pg_dump.

## 8. Критерии успешного выполнения

*   **Пользователь**: мультиязычный интерфейс, поиск, фильтрация, избранное, карта.
*   **Менеджер**: управление товарами своих магазинов, уведомления.
*   **Администратор**: полный доступ, аналитика (Google Analytics, Chart.js).
*   **API**: версионированное, документированное, < 300 мс.
*   **Дизайн**: WCAG 2.1, RTL, адаптивный.
*   **Данные**: 50+ товаров, 5 категорий, 10 магазинов.
*   **Тестирование**: покрытие ≥ 85%, E2E, нагрузочные тесты.
*   **Код**: PEP 8, сервисный слой, type hints.
*   **Деплой**: zero-downtime, мониторинг, логирование.

## 9. Пример структуры проекта
```
shoplist/
├── manage.py
├── shoplist/
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
│   │   ├── permissions.py
│   ├── forms.py
│   ├── management/
│   │   ├── commands/
│   │   │   ├── generate_fixtures.py
│   ├── migrations/
│   ├── models.py
│   ├── services/
│   │   ├── product_service.py
│   ├── repositories/
│   │   ├── product_repository.py
│   ├── templates/
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── product_detail.html
│   │   ├── manager_dashboard.html
│   │   ├── product_form.html
│   │   ├── login.html
│   │   ├── register.html
│   ├── tests/
│   │   ├── test_views.py
│   │   ├── test_api.py
│   ├── urls.py
│   ├── views.py
│   ├── filters.py
├── media/
│   ├── products/
├── static/
│   ├── css/
│   ├── js/
├── fixtures/
│   ├── initial_data.json
├── docker/
│   ├── Dockerfile
│   ├── docker-compose.yml
├── nginx/
│   ├── nginx.conf
├── docs/
│   ├── technical_specification.md
├── README.md
├── requirements.txt
├── .env
```

## 10. Пример фикстуры (initial_data.json)
```json
[
    {
        "model": "products.category",
        "pk": 1,
        "fields": {
            "translations": [
                {"language_code": "ru", "name": "Электроника", "slug": "electronics"},
                {"language_code": "en", "name": "Electronics", "slug": "electronics"}
            ],
            "created_at": "2025-09-12T10:00:00Z"
        }
    },
    {
        "model": "products.shop",
        "pk": 1,
        "fields": {
            "translations": [
                {"language_code": "ru", "name": "ТехноМир", "address": "ул. Ленина, 10", "city": "Москва"},
                {"language_code": "en", "name": "TechnoWorld", "address": "Lenin St, 10", "city": "Moscow"}
            ],
            "latitude": 55.7558,
            "longitude": 37.6173,
            "created_at": "2025-09-12T10:00:00Z"
        }
    },
    {
        "model": "products.product",
        "pk": 1,
        "fields": {
            "translations": [
                {"language_code": "ru", "name": "Смартфон X", "description": "Современный смартфон."},
                {"language_code": "en", "name": "Smartphone X", "description": "Modern smartphone."}
            ],
            "price": 29990.00,
            "discount_price": 26990.00,
            "currency": "RUB",
            "category": 1,
            "shops": [1],
            "tags": [1],
            "created_at": "2025-09-12T10:00:00Z",
            "views_count": 0
        }
    },
    {
        "model": "products.productimage",
        "pk": 1,
        "fields": {
            "product": 1,
            "image": "products/2025/09/12/smartphone_x.webp",
            "alt_text": "Смартфон X",
            "order": 0
        }
    },
    {
        "model": "products.tag",
        "pk": 1,
        "fields": {
            "translations": [
                {"language_code": "ru", "name": "Новинка"},
                {"language_code": "en", "name": "New"}
            ]
        }
    }
]
```

## 11. Пример README.md
```markdown
# ShopList

## Описание
ShopList — масштабируемый e-commerce сайт с REST API, мультиязычностью, картами, уведомлениями и аналитикой. Поддерживает просмотр товаров, управление ассортиментом и интеграции.

## Требования
- Python 3.10+
- Django 4.x, Django REST Framework
- PostgreSQL, Redis
- Docker, Kubernetes
- Tailwind CSS, Alpine.js, Chart.js, PhotoSwipe

## Установка
1. Клонируйте репозиторий:
   ```bash
   git clone <repository_url>
   cd shoplist
   ```

2. Настройте .env:
   ```
   DATABASE_URL=postgresql://user:pass@localhost/db
   SECRET_KEY=your-secret-key
   REDIS_URL=redis://localhost:6379/0
   CLOUDINARY_URL=cloudinary://key:secret@cloud
   UNSPLASH_ACCESS_KEY=your-unsplash-access-key
   ```

3. Запустите Docker:
   ```bash
   docker-compose up --build
   ```

4. Выполните миграции:
   ```bash
   docker-compose exec web python manage.py makemigrations
   docker-compose exec web python manage.py migrate
   ```

5. Загрузите данные:
   ```bash
   docker-compose exec web python manage.py generate_fixtures --categories 5 --shops 10 --tags 15 --products 50
   ```

6. Создайте суперпользователя:
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

## Использование

*   **Главная**: `/` — товары, поиск, фильтры, карта.
*   **Товар**: `/products/<id>/` — детали.
*   **API**: `/api/v1/` — Swagger.
*   **Фронтенд-админка**: `/manager/` — управление.
*   **Django admin**: `/admin/` — полный доступ.
*   **Регистрация**: `/register/`, вход: `/login/`.

## Деплой

Zero-downtime: Kubernetes.
CI/CD: GitHub Actions.
Мониторинг: Sentry, Prometheus, Grafana.
Логирование: ELK.
CDN: Cloudinary.
Резервное копирование: S3, pg_dump.

## Дополнительные замечания
- **SEO**: Мета-теги, sitemap.xml, robots.txt, canonical URLs.
- **Мониторинг**: Метрики здоровья (uptime, latency) через Prometheus.
- **Масштабируемость**: Celery для асинхронных задач (уведомления, аналитика).
- **Документация**: Архитектурные диаграммы (C4 model) в `/docs/`.