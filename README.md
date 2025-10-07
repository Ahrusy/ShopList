# 🛒 ShopList - Интернет-магазин на Django

Современный интернет-магазин с полной русской локализацией, построенный на Django с использованием django-parler для многоязычности.

## ✨ Особенности

### 🌐 Многоязычность
- **Полная русская локализация** - 494 категории, 792 товара
- Поддержка русского, английского и арабского языков
- Использование django-parler для переводов

### 🛍️ Функциональность магазина
- **Каталог товаров** с категориями и подкатегориями
- **Корзина покупок** и система заказов
- **Система пользователей** с ролями (покупатель, продавец, менеджер, админ)
- **Избранные товары** и рейтинги
- **Поиск и фильтрация** товаров

### 🎨 Современный интерфейс
- Адаптивный дизайн в стиле Ozon
- Bootstrap 5 для стилизации
- AJAX для динамической загрузки контента
- Мега-меню с категориями

### 🔧 Технические возможности
- **Django 5.2.7** с современными практиками
- **PostgreSQL/SQLite** поддержка
- **Redis** для кеширования
- **Celery** для фоновых задач
- **REST API** с DRF
- **Аналитика** и уведомления

## 🚀 Быстрый старт

### Требования
- Python 3.11+
- Django 5.2.7
- PostgreSQL (опционально)
- Redis (для продакшена)

### Установка

1. **Клонирование репозитория**
```bash
git clone https://github.com/Ahrusy/ShopList.git
cd ShopList
```

2. **Создание виртуального окружения**
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate
```

3. **Установка зависимостей**
```bash
pip install -r requirements.txt
```

4. **Настройка базы данных**
```bash
python manage.py migrate
```

5. **Создание переводов**
```bash
python manage.py create_quality_translations
```

6. **Создание суперпользователя**
```bash
python manage.py createsuperuser
```

7. **Запуск сервера**
```bash
python manage.py runserver
```

Сайт будет доступен по адресу: http://127.0.0.1:8000/

## 📁 Структура проекта

```
ShopList/
├── products/                 # Основное приложение
│   ├── models.py            # Модели (Category, Product, Order, etc.)
│   ├── views.py             # Представления
│   ├── admin.py             # Админ-панель
│   ├── api_views.py         # REST API
│   ├── management/commands/ # Команды управления
│   │   ├── create_quality_translations.py
│   │   ├── update_russian_translations.py
│   │   └── check_translations.py
│   ├── migrations/          # Миграции БД
│   ├── templates/           # HTML шаблоны
│   └── static/             # CSS, JS, изображения
├── shoplist/               # Настройки проекта
│   ├── settings.py         # Конфигурация
│   ├── urls.py            # URL маршруты
│   └── celery.py          # Настройки Celery
├── requirements.txt        # Зависимости Python
└── README.md              # Документация
```

## 🛠️ Команды управления

### Переводы
```bash
# Создание качественных переводов
python manage.py create_quality_translations

# Обновление переводов
python manage.py update_russian_translations

# Создание переводов подкатегорий
python manage.py create_subcategory_translations

# Проверка статуса переводов
python manage.py check_translations
```

### Данные
```bash
# Загрузка тестовых товаров
python manage.py load_products

# Генерация фикстур
python manage.py generate_fixtures

# Проверка категорий
python manage.py check_categories
```

## 🌍 Локализация

Проект поддерживает следующие языки:
- **Русский (ru)** - основной язык, 100% переведен
- **Английский (en)** - частично переведен
- **Арабский (ar)** - базовая поддержка

### Статистика переводов:
- ✅ **494/494** категорий на русском
- ✅ **792/792** товаров на русском  
- ✅ **5/5** магазинов на русском
- ✅ **22/22** тегов на русском

## 🔧 Настройка

### Переменные окружения
Создайте файл `.env` в корне проекта:

```env
DEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///db.sqlite3
REDIS_URL=redis://localhost:6379/0
EMAIL_HOST_USER=your-email@example.com
EMAIL_HOST_PASSWORD=your-password
```

### База данных
По умолчанию используется SQLite. Для PostgreSQL:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'shoplist_db',
        'USER': 'postgres',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

## 📊 API

REST API доступен по адресу `/api/v1/`:

- `GET /api/v1/products/` - список товаров
- `GET /api/v1/categories/` - список категорий
- `GET /api/v1/products/{id}/` - детали товара
- `POST /api/v1/orders/` - создание заказа

Документация API: http://127.0.0.1:8000/api/schema/swagger-ui/

## 🎯 Основные модели

### Category (Категория)
- Многоуровневая иерархия категорий
- Переводы на несколько языков
- Мега-меню поддержка

### Product (Товар)
- Полная информация о товаре
- Изображения и характеристики
- Рейтинги и отзывы

### Order (Заказ)
- Система заказов с статусами
- Интеграция с платежными системами
- Email уведомления

### User (Пользователь)
- Расширенная модель пользователя
- Роли: покупатель, продавец, менеджер, админ
- Избранные товары

## 🚀 Развертывание

### Docker (рекомендуется)
```bash
# Сборка образа
docker build -t shoplist .

# Запуск контейнера
docker run -p 8000:8000 shoplist
```

### Heroku
```bash
# Установка Heroku CLI
heroku create your-app-name
git push heroku main
heroku run python manage.py migrate
```

## 🤝 Вклад в проект

1. Форкните репозиторий
2. Создайте ветку для новой функции (`git checkout -b feature/amazing-feature`)
3. Зафиксируйте изменения (`git commit -m 'Add amazing feature'`)
4. Отправьте в ветку (`git push origin feature/amazing-feature`)
5. Откройте Pull Request

## 📝 Лицензия

Этот проект распространяется под лицензией MIT. См. файл `LICENSE` для подробностей.

## 👨‍💻 Автор

**Ahrusy** - [GitHub](https://github.com/Ahrusy)

## 🙏 Благодарности

- Django команде за отличный фреймворк
- django-parler за многоязычность
- Bootstrap за UI компоненты
- Всем контрибьюторам проекта

---

⭐ Поставьте звезду, если проект был полезен!
