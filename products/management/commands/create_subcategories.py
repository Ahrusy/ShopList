"""
Management команда для создания подкатегорий
"""
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from products.models import Category
from products.utils import CategorySubcategoryGenerator


class Command(BaseCommand):
    help = 'Создает подкатегории 2-го и 3-го уровня для всех корневых категорий'

    def add_arguments(self, parser):
        parser.add_argument(
            '--category-id',
            type=int,
            help='ID конкретной категории для создания подкатегорий'
        )
        parser.add_argument(
            '--category-name',
            type=str,
            help='Название категории для создания подкатегорий'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Показать что будет создано без фактического создания'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Пересоздать подкатегории даже если они уже существуют'
        )

    def handle(self, *args, **options):
        generator = CategorySubcategoryGenerator()
        
        # Определяем какие категории обрабатывать
        if options['category_id']:
            try:
                categories = [Category.objects.get(id=options['category_id'])]
            except Category.DoesNotExist:
                raise CommandError(f'Категория с ID {options["category_id"]} не найдена')
        elif options['category_name']:
            categories = Category.objects.filter(name__icontains=options['category_name'])
            if not categories.exists():
                raise CommandError(f'Категории с названием "{options["category_name"]}" не найдены')
        else:
            # Обрабатываем все корневые категории
            categories = Category.objects.filter(parent=None, is_active=True)

        if options['dry_run']:
            self.stdout.write(
                self.style.WARNING('РЕЖИМ ПРЕДВАРИТЕЛЬНОГО ПРОСМОТРА - изменения не будут сохранены')
            )

        total_created = 0
        
        for category in categories:
            self.stdout.write(f'\nОбработка категории: {category.name}')
            
            if options['dry_run']:
                # Показываем что будет создано
                self._show_preview(generator, category)
            else:
                # Создаем подкатегории
                with transaction.atomic():
                    if options['force']:
                        # Удаляем существующие подкатегории
                        existing_children = category.children.all()
                        if existing_children.exists():
                            self.stdout.write(
                                f'  Удаление {existing_children.count()} существующих подкатегорий...'
                            )
                            existing_children.delete()
                    
                    created = generator.ensure_subcategories_for_category(category)
                    total_created += len(created)
                    
                    if created:
                        self.stdout.write(
                            self.style.SUCCESS(f'  Создано {len(created)} подкатегорий')
                        )
                        for cat in created:
                            level_indicator = '  ' * (cat.category_level + 1)
                            self.stdout.write(f'{level_indicator}- {cat.name}')
                    else:
                        self.stdout.write('  Подкатегории уже существуют или шаблон не найден')

        if not options['dry_run']:
            self.stdout.write(
                self.style.SUCCESS(f'\nВсего создано подкатегорий: {total_created}')
            )
        
        # Обновляем счетчики товаров
        if not options['dry_run'] and total_created > 0:
            self.stdout.write('\nОбновление счетчиков товаров...')
            self._update_products_count()
            self.stdout.write(self.style.SUCCESS('Счетчики товаров обновлены'))

    def _show_preview(self, generator, category):
        """Показывает предварительный просмотр создаваемых подкатегорий"""
        category_name_lower = category.name.lower()
        
        # Ищем подходящий шаблон
        template_key = None
        for key in generator.SUBCATEGORIES_MAP.keys():
            if key in category_name_lower or category_name_lower in key:
                template_key = key
                break
        
        if not template_key:
            template_key = generator._get_generic_template_key(category_name_lower)
        
        if template_key:
            template = generator.SUBCATEGORIES_MAP[template_key]
            self.stdout.write(f'  Будет использован шаблон: {template_key}')
            
            for subcategory_name in template['level_2']:
                self.stdout.write(f'    + {subcategory_name} (уровень 2)')
                
                if subcategory_name in template['level_3']:
                    for sub_subcategory_name in template['level_3'][subcategory_name]:
                        self.stdout.write(f'      + {sub_subcategory_name} (уровень 3)')
        else:
            self.stdout.write('  Подходящий шаблон не найден')

    def _update_products_count(self):
        """Обновляет счетчики товаров для всех категорий"""
        categories = Category.objects.all()
        for category in categories:
            category.update_products_count()
            category.save(update_fields=['products_count', 'has_products'])