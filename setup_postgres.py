#!/usr/bin/env python
"""
Скрипт для настройки PostgreSQL и выполнения миграций
"""
import os
import sys
import django
import psycopg2
from psycopg2 import sql
import logging

# Настройка логгера
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('setup_postgres.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shoplist.settings')
django.setup()

from django.core.management import execute_from_command_line
from django.db import connection
from django.conf import settings

def check_postgres_connection():
    """Проверяет подключение к PostgreSQL"""
    try:
        # Параметры подключения из settings
        db_config = settings.DATABASES['default']
        
        conn = psycopg2.connect(
            host=db_config['HOST'],
            port=db_config['PORT'],
            user=db_config['USER'],
            password=db_config['PASSWORD'],
            database=db_config['NAME']
        )
        
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        logger.info(f"✅ Подключение к PostgreSQL успешно: {version[0]}")
        
        cursor.close()
        conn.close()
        return True
        
    except psycopg2.OperationalError as e:
        logger.error(f"❌ Ошибка подключения к PostgreSQL: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Неожиданная ошибка: {e}")
        return False

def create_database_if_not_exists():
    """Создает базу данных если она не существует"""
    try:
        # Подключаемся к базе данных postgres для создания новой БД
        conn = psycopg2.connect(
            host=settings.DATABASES['default']['HOST'],
            port=settings.DATABASES['default']['PORT'],
            user=settings.DATABASES['default']['USER'],
            password=settings.DATABASES['default']['PASSWORD'],
            database='postgres'
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Проверяем, существует ли база данных
        cursor.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s",
            (settings.DATABASES['default']['NAME'],)
        )
        
        if not cursor.fetchone():
            # Создаем базу данных
            cursor.execute(
                sql.SQL("CREATE DATABASE {}").format(
                    sql.Identifier(settings.DATABASES['default']['NAME'])
                )
            )
            logger.info(f"✅ База данных {settings.DATABASES['default']['NAME']} создана")
        else:
            logger.info(f"✅ База данных {settings.DATABASES['default']['NAME']} уже существует")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Ошибка при создании базы данных: {e}")
        return False

def run_migrations():
    """Выполняет миграции Django"""
    try:
        logger.info("Выполнение миграций...")
        
        # Создаем миграции
        execute_from_command_line(['manage.py', 'makemigrations'])
        
        # Применяем миграции
        execute_from_command_line(['manage.py', 'migrate'])
        
        logger.info("✅ Миграции выполнены успешно")
        return True
        
    except Exception as e:
        logger.error(f"❌ Ошибка при выполнении миграций: {e}")
        return False

def create_superuser():
    """Создает суперпользователя"""
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='admin123',
                role='admin'
            )
            logger.info("✅ Суперпользователь создан: admin/admin123")
        else:
            logger.info("✅ Суперпользователь уже существует")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Ошибка при создании суперпользователя: {e}")
        return False

def check_database_tables():
    """Проверяет наличие таблиц в базе данных"""
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """)
            tables = cursor.fetchall()
            
            logger.info(f"✅ Найдено таблиц в базе данных: {len(tables)}")
            for table in tables:
                logger.info(f"  - {table[0]}")
            
            return True
            
    except Exception as e:
        logger.error(f"❌ Ошибка при проверке таблиц: {e}")
        return False

def main():
    logger.info("=== НАСТРОЙКА POSTGRESQL ===")
    
    # Проверяем подключение к PostgreSQL
    if not check_postgres_connection():
        logger.error("Не удалось подключиться к PostgreSQL. Проверьте настройки в settings.py")
        return False
    
    # Создаем базу данных если нужно
    if not create_database_if_not_exists():
        logger.error("Не удалось создать базу данных")
        return False
    
    # Выполняем миграции
    if not run_migrations():
        logger.error("Не удалось выполнить миграции")
        return False
    
    # Проверяем таблицы
    if not check_database_tables():
        logger.error("Не удалось проверить таблицы")
        return False
    
    # Создаем суперпользователя
    if not create_superuser():
        logger.error("Не удалось создать суперпользователя")
        return False
    
    logger.info("🎉 Настройка PostgreSQL завершена успешно!")
    logger.info("Теперь можно запускать скрипт парсинга: python scrape_ozon_products_postgres.py")
    
    return True

if __name__ == "__main__":
    main()
