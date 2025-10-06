"""
Management команда для исправления пустых имен категорий
"""
from django.core.management.base import BaseCommand
from products.models import Category


class Command(BaseCommand):
    help = 'Исправляет пустые имена категорий, используя slug'

    def handle(self, *args, **options):
        # Находим категории с пустыми именами
        empty_name_categories = Category.objects.filter(name='')
        
        self.stdout.write(f'Найдено категорий с пустыми именами: {empty_name_categories.count()}')
        
        fixed_count = 0
        for category in empty_name_categories:
            if category.slug:
                # Создаем имя из slug
                name = category.slug.replace('-', ' ').replace('_', ' ').title()
                category.name = name
                category.save()
                fixed_count += 1
                self.stdout.write(f'Исправлено: ID {category.id}, slug "{category.slug}" -> name "{name}"')
        
        self.stdout.write(
            self.style.SUCCESS(f'Успешно исправлено {fixed_count} категорий')
        )
        
        # Проверяем результат
        remaining_empty = Category.objects.filter(name='').count()
        self.stdout.write(f'Осталось категорий с пустыми именами: {remaining_empty}')