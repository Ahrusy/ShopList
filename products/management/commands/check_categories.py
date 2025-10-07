"""
Management команда для проверки категорий
"""
from django.core.management.base import BaseCommand
from products.models import Category


class Command(BaseCommand):
    help = 'Проверяет категории и их структуру'

    def handle(self, *args, **options):
        # Проверяем общее количество категорий
        total_categories = Category.objects.count()
        active_categories = Category.objects.filter(is_active=True).count()
        root_categories = Category.objects.filter(parent=None, is_active=True).count()
        
        self.stdout.write(f'Всего категорий: {total_categories}')
        self.stdout.write(f'Активных категорий: {active_categories}')
        self.stdout.write(f'Корневых категорий: {root_categories}')
        
        # Показываем первые 10 корневых категорий
        self.stdout.write('\n=== Корневые категории ===')
        root_cats = Category.objects.filter(
            parent=None, 
            is_active=True
        ).order_by('sort_order')[:10]
        
        for cat in root_cats:
            children_count = cat.children.filter(is_active=True).count()
            self.stdout.write(f'• {cat.name} (ID: {cat.id}, Slug: {cat.slug}, Детей: {children_count})')
            
            # Показываем первые 3 подкатегории
            children = cat.children.filter(is_active=True)[:3]
            for child in children:
                grandchildren_count = child.children.filter(is_active=True).count()
                self.stdout.write(f'  ├─ {child.name} (ID: {child.id}, Внуков: {grandchildren_count})')
                
                # Показываем первые 2 подкатегории 3-го уровня
                grandchildren = child.children.filter(is_active=True)[:2]
                for grandchild in grandchildren:
                    self.stdout.write(f'     └─ {grandchild.name} (ID: {grandchild.id})')
        
        # Проверяем категории с пустыми именами
        empty_names = Category.objects.filter(name='').count()
        if empty_names > 0:
            self.stdout.write(
                self.style.WARNING(f'\n⚠️  Найдено {empty_names} категорий с пустыми именами!')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('\n✅ Все категории имеют названия')
            )
        
        # Проверяем поля для мега меню
        with_megamenu_images = Category.objects.exclude(mega_menu_image='').count()
        with_megamenu_descriptions = Category.objects.exclude(mega_menu_description='').count()
        
        self.stdout.write(f'\nКатегорий с изображениями для мега меню: {with_megamenu_images}')
        self.stdout.write(f'Категорий с описаниями для мега меню: {with_megamenu_descriptions}')
        
        self.stdout.write(
            self.style.SUCCESS('\n✅ Проверка завершена!')
        )