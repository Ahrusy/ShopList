#!/usr/bin/env python
"""
Главный скрипт для создания 500 товаров
"""
import os
import sys
import subprocess
import logging

# Настройка логгера
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('product_creation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def run_script(script_name, description):
    """Запускает скрипт и обрабатывает ошибки"""
    logger.info(f"🚀 Запуск: {description}")
    
    try:
        result = subprocess.run([sys.executable, script_name], 
                              capture_output=True, text=True, check=True)
        logger.info(f"✅ Успешно: {description}")
        if result.stdout:
            logger.info(f"Вывод: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Ошибка в {description}: {e}")
        if e.stdout:
            logger.error(f"Вывод: {e.stdout}")
        if e.stderr:
            logger.error(f"Ошибки: {e.stderr}")
        return False
    except Exception as e:
        logger.error(f"❌ Неожиданная ошибка в {description}: {e}")
        return False

def main():
    logger.info("🎯 НАЧАЛО СОЗДАНИЯ 500 ТОВАРОВ")
    logger.info("=" * 60)
    
    # Шаг 1: Проверяем настройки Django
    logger.info("📋 Шаг 1: Проверка настроек Django")
    if not run_script("check_products.py", "Проверка текущего состояния базы данных"):
        logger.warning("⚠️ Продолжаем несмотря на ошибки проверки")
    
    # Шаг 2: Создаем товары
    logger.info("📋 Шаг 2: Создание товаров")
    if not run_script("scrape_real_products.py", "Создание 500 товаров с характеристиками"):
        logger.error("❌ КРИТИЧЕСКАЯ ОШИБКА: Не удалось создать товары")
        return False
    
    # Шаг 3: Проверяем результаты
    logger.info("📋 Шаг 3: Проверка результатов")
    if not run_script("check_products.py", "Проверка созданных товаров"):
        logger.warning("⚠️ Не удалось проверить результаты")
    
    logger.info("🎉 ПРОЦЕСС ЗАВЕРШЕН!")
    logger.info("=" * 60)
    
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("\n✅ Все задачи выполнены успешно!")
        print("📊 Проверьте результаты с помощью: python check_products.py")
    else:
        print("\n❌ Процесс завершился с ошибками")
        print("📋 Проверьте логи для деталей")
    
    sys.exit(0 if success else 1)
