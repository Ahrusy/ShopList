#!/usr/bin/env python3
"""
Скрипт для тестирования контекста шаблона
"""
import os
import sys
import django

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shoplist.settings')
django.setup()

from products.models import Category
from products.views import index
from django.test import RequestFactory
from django.contrib.auth.models import AnonymousUser

def test_template_context():
    print("🧪 Тестирование контекста шаблона...")
    
    # Создаем фиктивный запрос
    factory = RequestFactory()
    request = factory.get('/')
    request.user = AnonymousUser()
    
    # Получаем корневые категории напрямую
    root_categories = Category.objects.filter(
        parent__isnull=True, 
        is_active=True
    ).order_by('sort_order')
    
    print(f"📊 Корневых категорий в базе: {root_categories.count()}")
    
    # Показываем первые 5 категорий
    for i, cat in enumerate(root_categories[:5]):
        print(f"   {i+1}. {cat.name} (ID: {cat.id}, Slug: {cat.slug})")
    
    print("\n✅ Тест завершен!")

if __name__ == "__main__":
    test_template_context()