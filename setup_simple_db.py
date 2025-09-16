#!/usr/bin/env python
"""
Скрипт для настройки упрощенной базы данных
"""
import os
import sys
import django
import subprocess

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shoplist.settings_simple')
django.setup()

from django.core.management import execute_from_command_line

def run_command(command):
    """Выполняет команду Django"""
    print(f"Выполнение: {command}")
    try:
        execute_from_command_line(command.split())
        print(f"✅ Успешно: {command}")
        return True
    except Exception as e:
        print(f"❌ Ошибка в {command}: {e}")
        return False

def main():
    print("🔧 НАСТРОЙКА УПРОЩЕННОЙ БАЗЫ ДАННЫХ")
    print("=" * 50)
    
    # Создаем миграции
    print("📋 Создание миграций...")
    if not run_command("makemigrations"):
        print("❌ Не удалось создать миграции")
        return False
    
    # Применяем миграции
    print("📋 Применение миграций...")
    if not run_command("migrate"):
        print("❌ Не удалось применить миграции")
        return False
    
    # Создаем суперпользователя
    print("📋 Создание суперпользователя...")
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='admin123'
            )
            print("✅ Суперпользователь создан: admin/admin123")
        else:
            print("ℹ️ Суперпользователь уже существует")
    except Exception as e:
        print(f"⚠️ Ошибка при создании суперпользователя: {e}")
    
    print("🎉 Настройка базы данных завершена!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
