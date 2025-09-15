# Ozon-style Маркетплейс

## Описание
Современный маркетплейс в стиле Ozon, построенный на Django с REST API, мультиязычностью, системой заказов, отзывов и комиссий. Поддерживает управление продавцами, товарами, заказами и аналитику.

## Основные возможности

### Для покупателей:
- Просмотр товаров с высококачественными изображениями
- Полнотекстовый поиск и фильтрация по категориям, ценам, характеристикам
- Система корзины и заказов
- Отзывы и рейтинги товаров
- Мультиязычный интерфейс (русский, английский, арабский)
- Интерактивная карта магазинов

### Для продавцов:
- Управление товарами через фронтенд-панель
- Система характеристик товаров
- Аналитика продаж и комиссий
- Управление заказами
- Уведомления о действиях

### Для администраторов:
- Полный доступ через Django admin
- Модерация товаров и отзывов
- Управление продавцами и комиссиями
- Аналитика платформы

## Технологический стек

### Backend:
- **Django 4.x** - основной фреймворк
- **Django REST Framework** - API
- **PostgreSQL** - основная база данных
- **Redis** - кэширование и очереди
- **Celery** - асинхронные задачи

### Frontend:
- **Django Templates** - шаблоны
- **Tailwind CSS** - стилизация
- **Alpine.js** - интерактивность
- **Chart.js** - графики и аналитика
- **PhotoSwipe** - галерея изображений

### Дополнительные библиотеки:
- **django-parler** - мультиязычность
- **django-filter** - фильтрация
- **django-crispy-forms** - формы
- **djangorestframework-simplejwt** - JWT аутентификация
- **drf-spectacular** - документация API
- **factory-boy** - генерация тестовых данных

## Установка

### Требования:
- Python 3.10+
- PostgreSQL 12+
- Redis 6+
- Node.js 16+ (для фронтенда)

### 1. Клонирование репозитория:
```bash
git clone <repository_url>
cd ozon_marketplace
```

### 2. Создание виртуального окружения:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows
```

### 3. Установка зависимостей:
```bash
pip install -r requirements.txt
```

### 4. Настройка переменных окружения:
Создайте файл `.env` в корне проекта:
```env
DEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://user:password@localhost:5432/marketplace_db
REDIS_URL=redis://localhost:6379/0
CLOUDINARY_URL=cloudinary://key:secret@cloud
UNSPLASH_ACCESS_KEY=your-unsplash-key
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### 5. Настройка базы данных:
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Создание суперпользователя:
```bash
python manage.py createsuperuser
```

### 7. Загрузка тестовых данных:
```bash
python manage.py generate_marketplace_data --categories 10 --sellers 20 --products 100 --reviews 200 --orders 50
```

### 8. Запуск сервера:
```bash
python manage.py runserver
```

## Использование

### Основные URL:
- **Главная страница**: `/` - каталог товаров
- **Товар**: `/products/<id>/` - детальная страница товара
- **API документация**: `/api/v1/swagger/` - Swagger UI
- **Админ-панель**: `/admin/` - Django admin
- **Панель продавца**: `/seller/` - управление товарами
- **Регистрация**: `/register/` - регистрация пользователей
- **Вход**: `/login/` - авторизация

### API Endpoints:
- `GET /api/v1/products/` - список товаров
- `GET /api/v1/products/<id>/` - детали товара
- `POST /api/v1/products/` - создание товара (продавцы)
- `GET /api/v1/categories/` - список категорий
- `GET /api/v1/sellers/` - список продавцов
- `GET /api/v1/orders/` - заказы пользователя
- `POST /api/v1/cart/` - управление корзиной

## Модели данных

### Основные модели:
- **User** - пользователи (покупатели, продавцы, админы)
- **Seller** - профили продавцов с комиссиями
- **Product** - товары с характеристиками и изображениями
- **Category** - категории товаров (мультиязычные)
- **Order** - заказы с позициями
- **Review** - отзывы и рейтинги
- **Cart** - корзина покупок

### Дополнительные модели:
- **ProductCharacteristic** - характеристики товаров
- **ProductImage** - изображения товаров
- **OrderItem** - позиции заказов
- **CartItem** - позиции корзины
- **Commission** - комиссии продавцов

## Архитектура

### Структура проекта:
```
ozon_marketplace/
├── manage.py
├── ozon_marketplace/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── products/
│   ├── models.py          # Модели данных
│   ├── views.py           # Представления
│   ├── api/               # REST API
│   ├── services/          # Бизнес-логика
│   ├── repositories/      # Доступ к данным
│   ├── templates/         # HTML шаблоны
│   ├── management/        # Django команды
│   └── tests/            # Тесты
├── static/               # Статические файлы
├── media/                # Загружаемые файлы
└── docs/                 # Документация
```

### Принципы архитектуры:
- **MVC** - разделение логики, представления и данных
- **Сервисный слой** - бизнес-логика в сервисах
- **Репозитории** - абстракция доступа к данным
- **Dependency Injection** - внедрение зависимостей
- **SOLID** - принципы объектно-ориентированного программирования

## Развертывание

### Docker:
```bash
docker-compose up --build
```

### Kubernetes:
```bash
kubectl apply -f k8s/
```

### Переменные окружения для продакшена:
```env
DEBUG=False
SECRET_KEY=production-secret-key
DATABASE_URL=postgresql://user:pass@db:5432/marketplace
REDIS_URL=redis://redis:6379/0
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

## Тестирование

### Запуск тестов:
```bash
python manage.py test
```

### Покрытие кода:
```bash
coverage run --source='.' manage.py test
coverage report
coverage html
```

### Нагрузочное тестирование:
```bash
locust -f tests/load_tests.py --host=http://localhost:8000
```

## Мониторинг

### Логирование:
- **Django Logs** - логи приложения
- **Nginx Logs** - веб-сервер
- **PostgreSQL Logs** - база данных

### Метрики:
- **Prometheus** - сбор метрик
- **Grafana** - визуализация
- **Sentry** - отслеживание ошибок

## Безопасность

### Реализованные меры:
- **JWT аутентификация** - безопасная авторизация
- **2FA** - двухфакторная аутентификация
- **Rate Limiting** - ограничение запросов
- **CSRF Protection** - защита от CSRF атак
- **XSS Protection** - защита от XSS
- **SQL Injection Protection** - защита от SQL инъекций

### Рекомендации:
- Регулярно обновляйте зависимости
- Используйте HTTPS в продакшене
- Настройте файрвол
- Регулярно делайте резервные копии

## Производительность

### Оптимизации:
- **Кэширование** - Redis для часто запрашиваемых данных
- **Индексы БД** - оптимизация запросов
- **CDN** - Cloudinary для изображений
- **Пагинация** - ограничение количества записей
- **Lazy Loading** - ленивая загрузка изображений

### Мониторинг производительности:
- Время ответа API < 300ms
- Поддержка 2000+ одновременных пользователей
- 1000+ RPS

## Мультиязычность

### Поддерживаемые языки:
- **Русский** (ru) - основной
- **Английский** (en) - международный
- **Арабский** (ar) - RTL поддержка

### Переводы:
- Названия и описания товаров
- Категории и теги
- Интерфейс приложения
- Сообщения об ошибках

## API Документация

### Swagger UI:
- URL: `/api/v1/swagger/`
- Интерактивная документация
- Тестирование API
- Схемы данных

### ReDoc:
- URL: `/api/v1/redoc/`
- Альтернативная документация
- Более читаемый формат

## Лицензия

MIT License - см. файл LICENSE

## Поддержка

### Контакты:
- **Email**: support@marketplace.com
- **Telegram**: @marketplace_support
- **GitHub Issues**: [Создать issue](https://github.com/your-repo/issues)

### Документация:
- [Техническое задание](docs/ozon_marketplace_technical_specification.md)
- [Анализ архитектуры](docs/architecture_analysis.md)
- [API Reference](docs/api_reference.md)

## Changelog

### v1.0.0 (2024-09-14)
- Первоначальный релиз
- Базовая функциональность маркетплейса
- Система заказов и корзины
- Мультиязычность
- REST API
- Админ-панель

### Планы развития:
- Мобильное приложение
- Интеграция с платежными системами
- Система рекомендаций
- Чат с продавцами
- Программа лояльности
