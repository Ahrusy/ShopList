#!/usr/bin/env python
"""
Главный скрипт для запуска парсинга товаров с Ozon
"""
import os
import sys
import subprocess
import logging
import time

# Настройка логгера
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('run_parsing.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def check_requirements():
    """Проверяет установленные зависимости"""
    try:
        import django
        import requests
        import selenium
        import psycopg2
        import beautifulsoup4
        logger.info("✅ Все зависимости установлены")
        return True
    except ImportError as e:
        logger.error(f"❌ Отсутствует зависимость: {e}")
        logger.error("Установите зависимости: pip install -r requirements.txt")
        return False

def run_setup_postgres():
    """Запускает настройку PostgreSQL"""
    logger.info("Настройка PostgreSQL...")
    try:
        result = subprocess.run([sys.executable, 'setup_postgres.py'], 
                              capture_output=True, text=True, timeout=300)
        if result.returncode == 0:
            logger.info("✅ Настройка PostgreSQL завершена")
            return True
        else:
            logger.error(f"❌ Ошибка настройки PostgreSQL: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        logger.error("❌ Таймаут при настройке PostgreSQL")
        return False
    except Exception as e:
        logger.error(f"❌ Ошибка при запуске настройки PostgreSQL: {e}")
        return False

def run_parsing():
    """Запускает парсинг товаров"""
    logger.info("Запуск парсинга товаров...")
    try:
        result = subprocess.run([sys.executable, 'scrape_ozon_products_postgres.py'], 
                              capture_output=True, text=True, timeout=3600)  # 1 час таймаут
        if result.returncode == 0:
            logger.info("✅ Парсинг завершен успешно")
            return True
        else:
            logger.error(f"❌ Ошибка парсинга: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        logger.error("❌ Таймаут при парсинге товаров")
        return False
    except Exception as e:
        logger.error(f"❌ Ошибка при запуске парсинга: {e}")
        return False

def main():
    logger.info("=== ЗАПУСК ПАРСИНГА ТОВАРОВ С OZON ===")
    
    # Проверяем зависимости
    if not check_requirements():
        return False
    
    # Настраиваем PostgreSQL
    if not run_setup_postgres():
        logger.error("Не удалось настроить PostgreSQL")
        return False
    
    # Запускаем парсинг
    if not run_parsing():
        logger.error("Не удалось выполнить парсинг")
        return False
    
    logger.info("🎉 Парсинг товаров завершен успешно!")
    logger.info("Проверьте базу данных PostgreSQL для просмотра результатов")
    
    return True

if __name__ == "__main__":
    main()

