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
- **Документация**: Все документация находится в папке `documentation/`.