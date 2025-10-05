# Быстрый запуск проекта ShopList

## Шаг 1: Установка зависимостей
```bash
pip install -r requirements_quick_start.txt
```

## Шаг 2: Применение миграций
```bash
python manage.py migrate
```

## Шаг 3: Создание суперпользователя (опционально)
```bash
python manage.py createsuperuser --username admin --email admin@example.com --noinput
python manage.py shell -c "from django.contrib.auth.models import User; u = User.objects.get(username='admin'); u.set_password('admin'); u.save()"
```

## Шаг 4: Запуск сервера
```bash
python manage.py runserver
```

## Доступ к приложению
- Основное приложение: http://127.0.0.1:8000/
- Админка Django: http://127.0.0.1:8000/admin/
- Логин для админки: admin / admin

## Основные команды
- Остановить сервер: Ctrl+C
- Создать миграции: `python manage.py makemigrations`
- Применить миграции: `python manage.py migrate`
- Создать суперпользователя: `python manage.py createsuperuser`