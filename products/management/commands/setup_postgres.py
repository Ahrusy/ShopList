import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from django.core.management.base import BaseCommand
from django.conf import settings
import os


class Command(BaseCommand):
    help = 'Создает базу данных PostgreSQL для проекта'

    def add_arguments(self, parser):
        parser.add_argument(
            '--db-name',
            type=str,
            default='shoplist_db',
            help='Имя базы данных (по умолчанию: shoplist_db)'
        )
        parser.add_argument(
            '--db-user',
            type=str,
            default='postgres',
            help='Пользователь базы данных (по умолчанию: postgres)'
        )
        parser.add_argument(
            '--db-password',
            type=str,
            default='postgres',
            help='Пароль базы данных (по умолчанию: postgres)'
        )
        parser.add_argument(
            '--db-host',
            type=str,
            default='localhost',
            help='Хост базы данных (по умолчанию: localhost)'
        )
        parser.add_argument(
            '--db-port',
            type=str,
            default='5432',
            help='Порт базы данных (по умолчанию: 5432)'
        )

    def handle(self, *args, **options):
        db_name = options['db_name']
        db_user = options['db_user']
        db_password = options['db_password']
        db_host = options['db_host']
        db_port = options['db_port']

        self.stdout.write(f'Создание базы данных {db_name}...')

        try:
            # Подключаемся к PostgreSQL как суперпользователь
            conn = psycopg2.connect(
                host=db_host,
                port=db_port,
                user=db_user,
                password=db_password,
                database='postgres'  # Подключаемся к системной БД
            )
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cursor = conn.cursor()

            # Проверяем, существует ли база данных
            cursor.execute(
                "SELECT 1 FROM pg_database WHERE datname = %s",
                (db_name,)
            )
            
            if cursor.fetchone():
                self.stdout.write(
                    self.style.WARNING(f'База данных {db_name} уже существует')
                )
            else:
                # Создаем базу данных
                cursor.execute(f'CREATE DATABASE "{db_name}"')
                self.stdout.write(
                    self.style.SUCCESS(f'База данных {db_name} успешно создана')
                )

            # Создаем расширения для полнотекстового поиска
            # Подключаемся к созданной базе данных
            conn.close()
            conn = psycopg2.connect(
                host=db_host,
                port=db_port,
                user=db_user,
                password=db_password,
                database=db_name
            )
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cursor = conn.cursor()
            
            cursor.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
            cursor.execute('CREATE EXTENSION IF NOT EXISTS "unaccent"')
            cursor.execute('CREATE EXTENSION IF NOT EXISTS "pg_trgm"')
            
            self.stdout.write(
                self.style.SUCCESS('Расширения PostgreSQL установлены')
            )

            cursor.close()
            conn.close()

            # Обновляем настройки Django
            self.update_django_settings(db_name, db_user, db_password, db_host, db_port)

        except psycopg2.Error as e:
            self.stdout.write(
                self.style.ERROR(f'Ошибка при создании базы данных: {e}')
            )
            return

        self.stdout.write(
            self.style.SUCCESS('Настройка PostgreSQL завершена!')
        )
        self.stdout.write('Теперь выполните: python manage.py migrate')

    def update_django_settings(self, db_name, db_user, db_password, db_host, db_port):
        """Обновляет настройки Django для использования PostgreSQL"""
        settings_file = 'shoplist/settings.py'
        
        # Читаем текущий файл настроек
        with open(settings_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Заменяем настройки базы данных
        new_db_config = f'''    DATABASES = {{
        'default': {{
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': '{db_name}',
            'USER': '{db_user}',
            'PASSWORD': '{db_password}',
            'HOST': '{db_host}',
            'PORT': '{db_port}',
        }}
    }}'''
        
        # Ищем и заменяем блок DATABASES
        import re
        pattern = r"DATABASES\s*=\s*\{[^}]+\}"
        content = re.sub(pattern, new_db_config, content, flags=re.DOTALL)
        
        # Записываем обновленный файл
        with open(settings_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        self.stdout.write('Настройки Django обновлены для PostgreSQL')
