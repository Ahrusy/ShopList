# ShopList - Интернет-магазин товаров

## 📋 Описание проекта

ShopList — масштабируемый e-commerce сайт с REST API, мультиязычностью, картами, уведомлениями и аналитикой. Поддерживает просмотр товаров, управление ассортиментом и интеграции.

**Компания-заказчик:** RetailNet Solutions — локальный IT-интегратор для розничных сетей.

**Клиенты:** Магазины электроники, одежды и продуктов, желающие публиковать ассортимент и адреса без полноценного интернет-магазина.

---

## 🎯 Цель проекта

Создать высокопроизводительный, масштабируемый и визуально привлекательный сайт-витрину на Django с продвинутыми админ-панелями, обеспечивающий:

- Просмотр товаров с высококачественными изображениями, ценами и адресами магазинов (с картой)
- Полнотекстовый поиск, фильтрацию и мультиязычность (включая RTL)
- Управление товарами через интуитивные фронтенд- и бэкенд-админки с аналитикой
- Интеграцию с картами, уведомлениями и внешними аналитическими сервисами
- Предзагруженную базу данных с реалистичными данными для демонстрации

---

## 🚀 Основные функции

### Для пользователей:
- Просмотр товаров с WebP-изображениями (ленивая загрузка, зум)
- Полнотекстовый поиск и фильтрация (категории, цены, магазины, теги)
- Добавление в избранное, мультиязычный интерфейс (русский, английский, арабский)
- Интерактивная карта для адресов магазинов

### Для менеджеров:
- Управление товарами своих магазинов через фронтенд-админку (CRUD, массовые действия)
- Уведомления о действиях (email, push)

### Для администраторов:
- Полный доступ через Django admin и фронтенд-админку
- Аналитика: просмотры, избранное, конверсии, поведение пользователей

### REST API:
- Версионированные эндпоинты (`/api/v1/`)
- Документация через Swagger/OpenAPI
- Поддержка кэширования и throttling

---

## 🛠 Технические требования

### Системные требования:
- **Python:** 3.10+
- **Django:** 4.x, Django REST Framework
- **База данных:** PostgreSQL, Redis
- **Контейнеризация:** Docker, Kubernetes
- **Frontend:** Tailwind CSS, Alpine.js, Chart.js, PhotoSwipe

### Стек технологий:

**Backend:**
- Django 4.x, Django REST Framework, Celery
- PostgreSQL, Redis
- JWT аутентификация, 2FA (TOTP)

**Frontend:**
- Django Templates, Tailwind CSS
- Alpine.js, Chart.js, PhotoSwipe
- Адаптивная верстка, WCAG 2.1 (AA)

**Библиотеки:**
- Pillow, django-crispy-forms, django-filter, django-parler
- django-admin-interface, djangorestframework-simplejwt, drf-spectacular
- django-two-factor-auth, django-ratelimit, django-notifications
- factory-boy, pytest, cypress

**Инфраструктура:**
- Docker, Kubernetes, Nginx, Gunicorn
- Cloudinary (CDN), Unsplash API
- Sentry, Prometheus, Grafana, ELK

---

## 📦 Установка и запуск

### Быстрый старт:

1. **Клонируйте репозиторий:**
   ```bash
   git clone <repository_url>
   cd shoplist
   ```

2. **Настройте переменные окружения:**
   ```env
   DATABASE_URL=postgresql://user:pass@localhost/db
   SECRET_KEY=your-secret-key
   REDIS_URL=redis://localhost:6379/0
   CLOUDINARY_URL=cloudinary://key:secret@cloud
   UNSPLASH_ACCESS_KEY=your-unsplash-access-key
   ```

3. **Запустите через Docker:**
   ```bash
   docker-compose up --build
   ```

4. **Выполните миграции:**
   ```bash
   docker-compose exec web python manage.py makemigrations
   docker-compose exec web python manage.py migrate
   ```

5. **Загрузите тестовые данные:**
   ```bash
   docker-compose exec web python manage.py generate_fixtures --categories 5 --shops 10 --tags 15 --products 50
   ```

6. **Создайте суперпользователя:**
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

### Быстрая установка (без Docker):

1. **Создайте виртуальное окружение:**
   ```bash
   python -m venv .venv
   ```

2. **Активируйте виртуальное окружение:**
   ```bash
   # Windows
   .venv\Scripts\activate
   
   # Linux/Mac
   source .venv/bin/activate
   ```

3. **Установите зависимости:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Примените миграции:**
   ```bash
   python manage.py migrate
   ```

5. **Создайте суперпользователя:**
   ```bash
   python manage.py createsuperuser
   ```

6. **Запустите сервер:**
   ```bash
   python manage.py runserver
   ```

---

## 🌐 Использование

### Основные URL:
- **Главная страница:** `/` — товары, поиск, фильтры, карта
- **Страница товара:** `/products/<id>/` — детали товара
- **REST API:** `/api/v1/` — Swagger документация
- **Фронтенд-админка:** `/manager/` — управление товарами
- **Django admin:** `/admin/` — полный административный доступ
- **Аутентификация:** `/register/`, `/login/` — регистрация и вход

### Доступ к системе:
- **Основное приложение:** http://127.0.0.1:8000/
- **Админка Django:** http://127.0.0.1:8000/admin/
- **API документация:** http://127.0.0.1:8000/api/v1/docs/

---

## 📊 Функциональные требования

### 1. Главная страница
**Список товаров:**
- Сетка: 4 колонки (десктоп), 2 (планшеты), 1 (мобильные)
- Карточка: название, цена (с учетом скидок), миниатюра (WebP), эффект наведения
- Слайдер с лайфстайл-фотографиями (3–5 изображений)

**Поиск и фильтрация:**
- Полнотекстовый поиск (PostgreSQL SearchVector) по названию, описанию, тегам
- Фильтры: категории, ценовой диапазон, магазины, теги (AJAX, индикатор загрузки)
- Обработка пустых состояний ("Товары не найдены")

**Пагинация:**
- 12 товаров на страницу, бесконечная прокрутка (опционально)

### 2. Страница товара
**Элементы:**
- Название (H1, SEO-оптимизированное)
- Галерея изображений (PhotoSwipe, WebP, зум)
- Цена (мультивалютность: RUB, USD, скидки)
- Описание (markdown, мультиязычное)
- Таблица магазинов с картой (Google Maps/OpenStreetMap)
- Теги (например, "новинка", "хит")
- Кнопка "Добавить в избранное"

### 3. Аутентификация и роли
**Роли пользователей:**
- **Пользователь:** Просмотр, фильтрация, избранное
- **Менеджер:** CRUD товары своих магазинов
- **Администратор:** Полный доступ, аналитика

**Безопасность:**
- 2FA (TOTP через django-two-factor-auth)
- Минимальная длина пароля: 12 символов
- Rate limiting, OWASP Top 10

### 4. REST API
**Эндпоинты:**
- `GET /api/v1/products/` — список (пагинация, фильтрация)
- `GET /api/v1/products/<id>/` — детали
- `POST/PUT/DELETE /api/v1/products/` — CRUD (для менеджеров/админов)
- `GET /api/v1/categories/`, `GET /api/v1/shops/` — списки

**Характеристики:**
- JWT аутентификация с refresh-токенами
- Swagger/OpenAPI документация
- Redis кэширование
- Throttling по ролям

---

## 🗄 Модели данных

### Основные модели:

```python
# Пользователь с ролями
class User(AbstractUser):
    ROLE_CHOICES = (
        ('user', 'Пользователь'),
        ('manager', 'Менеджер'),
        ('admin', 'Администратор'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
    favorites = models.ManyToManyField('Product', related_name='favorited_by', blank=True)

# Категория товаров (мультиязычная)
class Category(TranslatableModel):
    translations = TranslatedFields(
        name=models.CharField(max_length=100),
        slug=models.SlugField(max_length=100, unique=True)
    )

# Магазин (мультиязычный)
class Shop(TranslatableModel):
    translations = TranslatedFields(
        name=models.CharField(max_length=255),
        address=models.TextField(),
        city=models.CharField(max_length=100)
    )
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)

# Товар (мультиязычный)
class Product(TranslatableModel):
    translations = TranslatedFields(
        name=models.CharField(max_length=255),
        description=models.TextField(blank=True)
    )
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    category = models.ForeignKey('Category', on_delete=models.CASCADE)
    shops = models.ManyToManyField('Shop', related_name='products')
    search_vector = SearchVectorField(null=True)  # Для полнотекстового поиска
```

---

## 📁 Структура проекта

```
shoplist/
├── manage.py
├── shoplist/                    # Основные настройки Django
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── products/                    # Основное приложение
│   ├── models.py               # Модели данных
│   ├── views.py                # Представления
│   ├── admin.py                # Админка Django
│   ├── api/                    # REST API
│   │   ├── serializers.py
│   │   ├── views.py
│   │   └── urls.py
│   ├── templates/              # HTML шаблоны
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── product_detail.html
│   │   └── components/         # Компоненты
│   ├── static/                 # Статические файлы
│   ├── management/commands/    # Команды управления
│   └── tests/                  # Тесты
├── media/                      # Загруженные файлы
├── static/                     # Статические файлы
├── documentation/              # Документация
├── docker/                     # Docker конфигурация
├── nginx/                      # Nginx конфигурация
├── requirements.txt            # Python зависимости
└── README.md                   # Этот файл
```

---

## 🎨 Дизайн и UX

### Дизайн-система:
- **Стиль:** Минималистичный, белый фон, серые акценты, синий CTA
- **Шрифты:** Inter, Roboto, Noto Sans Arabic (для RTL)
- **Анимации:** Tailwind transitions, ленивая загрузка
- **Доступность:** WCAG 2.1 (AA), ARIA-атрибуты

### Адаптивность:
- **Мобильные:** < 768px
- **Планшеты:** 768px - 1024px  
- **Десктоп:** > 1024px

### Мультиязычность:
- **Языки:** Русский, английский, арабский
- **RTL поддержка:** Для арабского языка
- **Локализация:** Даты, числа, валюты

---

## 🔧 Разработка и тестирование

### Команды разработки:
```bash
# Создание миграций
python manage.py makemigrations

# Применение миграций  
python manage.py migrate

# Сбор статических файлов
python manage.py collectstatic

# Запуск тестов
python manage.py test

# Создание фикстур
python manage.py generate_fixtures
```

### Тестирование:
- **Покрытие:** ≥ 85% (pytest, coverage)
- **E2E тесты:** Cypress
- **Нагрузочные тесты:** Locust (1000 RPS)
- **API тесты:** Django REST Framework test client

### Качество кода:
- **Стандарт:** PEP 8
- **Type hints:** Обязательно
- **Архитектура:** Сервисный слой, репозитории
- **Документация:** Docstrings для всех функций

---

## 🚀 Деплой и инфраструктура

### Продакшен деплой:
```bash
# Docker build
docker-compose -f docker-compose.prod.yml up --build

# Kubernetes деплой
kubectl apply -f k8s/

# Zero-downtime деплой
kubectl rollout restart deployment/shoplist-web
```

### Мониторинг и логирование:
- **Мониторинг:** Sentry, Prometheus, Grafana
- **Логирование:** ELK Stack (Elasticsearch, Logstash, Kibana)
- **Метрики:** Uptime, latency, error rate
- **Алерты:** Slack, email уведомления

### CI/CD:
- **Платформа:** GitHub Actions
- **Этапы:** Тесты → Build → Deploy
- **Окружения:** Development, Staging, Production

### Резервное копирование:
- **База данных:** pg_dump в S3
- **Медиа файлы:** Cloudinary CDN
- **Код:** Git репозиторий

---

## 📈 Производительность

### Требования к производительности:
- **API:** < 300 мс для сложных запросов
- **Пользователи:** 2000 одновременных пользователей
- **RPS:** 1000 запросов в секунду
- **Доступность:** 99.9% uptime

### Оптимизации:
- **Кэширование:** Redis для сессий и данных
- **CDN:** Cloudinary для изображений
- **База данных:** Индексы, оптимизация запросов
- **Frontend:** Ленивая загрузка, минификация

---

## 🔒 Безопасность

### Меры безопасности:
- **OWASP Top 10:** Защита от основных уязвимостей
- **2FA:** TOTP аутентификация
- **Rate limiting:** Ограничение запросов
- **HTTPS:** Secure cookies, CSP, HSTS
- **Валидация:** Строгая валидация входных данных

### Аудит безопасности:
- Регулярные проверки зависимостей
- Сканирование кода на уязвимости
- Пентестинг критических функций

---

## 📚 Дополнительная документация

### Файлы документации:
- `EMAIL_CONFIGURATION_GUIDE.md` - Настройка email уведомлений
- `PROJECT_COMPLIANCE_ANALYSIS.md` - Анализ соответствия ТЗ
- `QUICK_START_RU.md` - Быстрый старт на русском

### API документация:
- Swagger UI: `/api/v1/docs/`
- ReDoc: `/api/v1/redoc/`
- OpenAPI схема: `/api/v1/schema/`

---

## 🤝 Участие в разработке

### Как внести вклад:
1. Fork репозитория
2. Создайте feature branch
3. Внесите изменения
4. Добавьте тесты
5. Создайте Pull Request

### Стандарты кода:
- Следуйте PEP 8
- Добавляйте type hints
- Пишите тесты для новой функциональности
- Обновляйте документацию

---

## 📞 Поддержка

### Контакты:
- **Email:** support@shoplist.com
- **GitHub Issues:** [Создать issue](https://github.com/your-repo/shoplist/issues)
- **Документация:** `/documentation/`

### FAQ:
- **Как настроить email?** См. `EMAIL_CONFIGURATION_GUIDE.md`
- **Как добавить новый язык?** Используйте django-parler
- **Как настроить 2FA?** См. раздел "Безопасность"

---

## 📄 Лицензия

Этот проект распространяется под лицензией MIT. См. файл `LICENSE` для подробностей.

---

## 🎉 Заключение

ShopList — это современное решение для создания витрины товаров с богатой функциональностью, высокой производительностью и отличным пользовательским опытом. Проект готов к масштабированию и может быть адаптирован под различные бизнес-требования.

**Статус проекта:** ✅ Готов к использованию  
**Версия:** 1.0.0  
**Последнее обновление:** Октябрь 2024

---

*Создано с ❤️ командой RetailNet Solutions*