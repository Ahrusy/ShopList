#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shoplist.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Создаем суперпользователя
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='admin123'
    )
    print("Суперпользователь 'admin' создан успешно!")
else:
    print("Суперпользователь 'admin' уже существует!")
