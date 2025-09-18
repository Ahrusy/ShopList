#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shoplist.settings')
django.setup()

from django.db import connection

with connection.cursor() as cursor:
    cursor.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'products_product'")
    columns = cursor.fetchall()
    print("Структура таблицы products_product:")
    for column in columns:
        print(f"  - {column[0]}: {column[1]}")

