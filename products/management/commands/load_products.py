"""
Management команда для загрузки товаров с реальными данными
"""
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from products.models import Category, Product
from products.services import ProductLoader


class Command(BaseCommand):
    help = 'Загружает товары с реальными данными в указанные категории'

    def add_arguments(self, parser):
        parser.add_argument(
            '--category-id',
            type=int,
            help='ID конкретной категории для загрузки товаров'
        )
        parser.add_argument(
            '--category-name',
            type=str,
            help='Название категории для загрузки товаров (поиск по вхождению)'
        )
        parser.add_argument(
            '--count',
            type=int,
            default=20,
            help='Количество товаров для создания в каждой категории (по умолчанию: 20)'
        )
        parser.add_argument(
            '--all-categories',
            action='store_true',
            help='Загрузить товары во все категории 3-го уровня'
        )
        parser.add_argument(
            '--level',
            type=int,
            choices=[0, 1, 2],
            help='Уровень категорий для загрузки (0-корневые, 1-второй уровень, 2-третий уровень)'
        )
        parser.add_argument(
            '--clear-existing',
            action='store_true',
            help='Удалить существующие товары в категориях перед загрузкой новых'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Показать что будет создано без фактического создания'
        )

    def handle(self, *args, **options):
        loader = ProductLoader()
        
        # Определяем какие категории обрабатывать
        categories = self._get_categories(options)
        
        if not categories:
            self.stdout.write(self.style.ERROR('Категории для обработки не найдены'))
            return
        
        if options['dry_run']:
            self.stdout.write(
                self.style.WARNING('РЕЖИМ ПРЕДВАРИТЕЛЬНОГО ПРОСМОТРА - товары не будут созданы')
            )
            self._show_preview(categories, options['count'])
            return
        
        # Очищаем существующие товары если нужно
        if options['clear_existing']:
            self._clear_existing_products(categories)
        
        # Загружаем товары
        total_created = 0
        
        for category in categories:
            self.stdout.write(f'\nЗагрузка товаров в категорию: {category.name}')
            
            try:
                with transaction.atomic():
                    created_products = loader.create_realistic_products(
                        category, 
                        options['count']
                    )
                    
                    total_created += len(created_products)
                    
                    self.stdout.write(
                        self.style.SUCCESS(f'  Создано товаров: {len(created_products)}')
                    )
                    
                    # Показываем примеры созданных товаров
                    for i, product in enumerate(created_products[:3]):
                        price_info = f"{product.price:,.0f} ₽"
                        if product.discount_price:
                            price_info += f" (со скидкой: {product.discount_price:,.0f} ₽)"
                        
                        self.stdout.write(f'    - {product.name} - {price_info}')
                    
                    if len(created_products) > 3:
                        self.stdout.write(f'    ... и еще {len(created_products) - 3} товаров')
                        
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'  Ошибка при загрузке товаров: {str(e)}')
                )
                continue
        
        # Обновляем счетчики товаров в категориях
        self.stdout.write('\nОбновление счетчиков товаров в категориях...')
        self._update_category_counters()
        
        self.stdout.write(
            self.style.SUCCESS(f'\nЗагрузка завершена. Всего создано товаров: {total_created}')
        )

    def _get_categories(self, options):
        """Получает список категорий для обработки"""
        if options['category_id']:
            try:
                return [Category.objects.get(id=options['category_id'])]
            except Category.DoesNotExist:
                raise CommandError(f'Категория с ID {options["category_id"]} не найдена')
        
        elif options['category_name']:
            categories = Category.objects.filter(
                name__icontains=options['category_name'],
                is_active=True
            )
            if not categories.exists():
                raise CommandError(f'Категории с названием "{options["category_name"]}" не найдены')
            return categories
        
        elif options['all_categories']:
            # По умолчанию берем категории 3-го уровня (самые глубокие)
            level = options.get('level', 2)
            return Category.objects.filter(
                category_level=level,
                is_active=True
            ).order_by('name')
        
        elif options['level'] is not None:
            return Category.objects.filter(
                category_level=options['level'],
                is_active=True
            ).order_by('name')
        
        else:
            raise CommandError(
                'Необходимо указать одну из опций: --category-id, --category-name, '
                '--all-categories или --level'
            )

    def _show_preview(self, categories, count):
        """Показывает предварительный просмотр"""
        self.stdout.write(f'Будет обработано категорий: {len(categories)}')
        self.stdout.write(f'Товаров в каждой категории: {count}')
        self.stdout.write(f'Общее количество товаров: {len(categories) * count}')
        
        self.stdout.write('\nКатегории для обработки:')
        for category in categories[:10]:  # Показываем первые 10
            path = self._get_category_path(category)
            self.stdout.write(f'  - {path}')
        
        if len(categories) > 10:
            self.stdout.write(f'  ... и еще {len(categories) - 10} категорий')

    def _get_category_path(self, category):
        """Возвращает полный путь категории"""
        path_parts = []
        current = category
        
        while current:
            path_parts.append(current.name)
            current = current.parent
        
        return ' > '.join(reversed(path_parts))

    def _clear_existing_products(self, categories):
        """Удаляет существующие товары в категориях"""
        total_deleted = 0
        
        for category in categories:
            # Получаем все товары в категории и её подкатегориях
            all_subcategories = [category] + list(category.get_all_children())
            products = Product.objects.filter(category__in=all_subcategories)
            
            count = products.count()
            if count > 0:
                products.delete()
                total_deleted += count
                self.stdout.write(f'  Удалено товаров из "{category.name}": {count}')
        
        if total_deleted > 0:
            self.stdout.write(
                self.style.WARNING(f'Всего удалено товаров: {total_deleted}')
            )

    def _update_category_counters(self):
        """Обновляет счетчики товаров во всех категориях"""
        categories = Category.objects.all()
        updated_count = 0
        
        for category in categories:
            old_count = category.products_count
            new_count = category.update_products_count()
            
            if old_count != new_count:
                category.save(update_fields=['products_count', 'has_products'])
                updated_count += 1
        
        self.stdout.write(f'Обновлено счетчиков: {updated_count}')