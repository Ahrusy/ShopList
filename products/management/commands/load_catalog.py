from django.core.management.base import BaseCommand
from products.models import Category
from django.utils.text import slugify


class Command(BaseCommand):
    help = 'Loads OZON-style catalog categories into the database'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Начало загрузки каталога...'))

        # Основные категории как в OZON
        categories_data = [
            {
                'name': 'Электроника',
                'icon': 'fas fa-laptop',
                'sort_order': 10,
                'children': [
                    {
                        'name': 'Смартфоны и гаджеты',
                        'children': [
                            {'name': 'Смартфоны'},
                            {'name': 'Планшеты'},
                            {'name': 'Умные часы'},
                            {'name': 'Наушники'},
                            {'name': 'Портативные зарядки'},
                        ]
                    },
                    {
                        'name': 'Компьютеры и ноутбуки',
                        'children': [
                            {'name': 'Ноутбуки'},
                            {'name': 'Компьютеры'},
                            {'name': 'Мониторы'},
                            {'name': 'Клавиатуры и мыши'},
                            {'name': 'Веб-камеры'},
                        ]
                    },
                    {
                        'name': 'ТВ и видео',
                        'children': [
                            {'name': 'Телевизоры'},
                            {'name': 'Проекторы'},
                            {'name': 'ТВ-приставки'},
                            {'name': 'Антенны'},
                        ]
                    },
                ]
            },
            {
                'name': 'Одежда',
                'icon': 'fas fa-tshirt',
                'sort_order': 20,
                'children': [
                    {
                        'name': 'Женская одежда',
                        'children': [
                            {'name': 'Платья'},
                            {'name': 'Блузки и рубашки'},
                            {'name': 'Брюки и джинсы'},
                            {'name': 'Юбки'},
                            {'name': 'Куртки и пальто'},
                        ]
                    },
                    {
                        'name': 'Мужская одежда',
                        'children': [
                            {'name': 'Рубашки'},
                            {'name': 'Брюки и джинсы'},
                            {'name': 'Футболки и поло'},
                            {'name': 'Куртки и пальто'},
                            {'name': 'Свитеры и кардиганы'},
                        ]
                    },
                ]
            },
            {
                'name': 'Обувь',
                'icon': 'fas fa-shoe-prints',
                'sort_order': 30,
                'children': [
                    {
                        'name': 'Женская обувь',
                        'children': [
                            {'name': 'Туфли'},
                            {'name': 'Сапоги'},
                            {'name': 'Кроссовки'},
                            {'name': 'Босоножки'},
                        ]
                    },
                    {
                        'name': 'Мужская обувь',
                        'children': [
                            {'name': 'Кроссовки'},
                            {'name': 'Туфли'},
                            {'name': 'Ботинки'},
                            {'name': 'Сандалии'},
                        ]
                    },
                ]
            },
            {
                'name': 'Дом и сад',
                'icon': 'fas fa-home',
                'sort_order': 40,
                'children': [
                    {
                        'name': 'Посуда и кухонные принадлежности',
                        'children': [
                            {'name': 'Посуда для приготовления'},
                            {'name': 'Ножи и разделочные доски'},
                            {'name': 'Столовая посуда'},
                            {'name': 'Чайники и кофейники'},
                            {'name': 'Формы для выпечки'},
                        ]
                    },
                    {
                        'name': 'Текстиль',
                        'children': [
                            {'name': 'Шторы и карнизы'},
                            {'name': 'Постельное белье'},
                            {'name': 'Подушки'},
                            {'name': 'Одеяла'},
                            {'name': 'Покрывала'},
                        ]
                    },
                    {
                        'name': 'Освещение',
                        'children': [
                            {'name': 'Потолочные и подвесные светильники'},
                            {'name': 'Напольные и настольные светильники'},
                            {'name': 'Уличные светильники'},
                            {'name': 'Лампочки'},
                        ]
                    },
                    {
                        'name': 'Дача и сад',
                        'children': [
                            {'name': 'Садовая техника'},
                            {'name': 'Садовый инструмент'},
                            {'name': 'Садовая мебель'},
                            {'name': 'Парники и теплицы'},
                        ]
                    },
                ]
            },
            {
                'name': 'Детские товары',
                'icon': 'fas fa-baby',
                'sort_order': 50,
                'children': [
                    {
                        'name': 'Одежда для детей',
                        'children': [
                            {'name': 'Для мальчиков'},
                            {'name': 'Для девочек'},
                            {'name': 'Для малышей'},
                        ]
                    },
                    {
                        'name': 'Игрушки',
                        'children': [
                            {'name': 'Конструкторы'},
                            {'name': 'Куклы'},
                            {'name': 'Машинки'},
                            {'name': 'Настольные игры'},
                        ]
                    },
                ]
            },
            {
                'name': 'Красота и здоровье',
                'icon': 'fas fa-spa',
                'sort_order': 60,
                'children': [
                    {
                        'name': 'Косметика',
                        'children': [
                            {'name': 'Декоративная косметика'},
                            {'name': 'Уход за лицом'},
                            {'name': 'Уход за телом'},
                            {'name': 'Парфюмерия'},
                        ]
                    },
                    {
                        'name': 'Здоровье',
                        'children': [
                            {'name': 'Витамины и БАДы'},
                            {'name': 'Медицинские приборы'},
                            {'name': 'Средства гигиены'},
                        ]
                    },
                ]
            },
            {
                'name': 'Бытовая техника',
                'icon': 'fas fa-tv',
                'sort_order': 70,
                'children': [
                    {
                        'name': 'Крупная техника',
                        'children': [
                            {'name': 'Холодильники'},
                            {'name': 'Стиральные машины'},
                            {'name': 'Плиты и духовки'},
                            {'name': 'Посудомоечные машины'},
                        ]
                    },
                    {
                        'name': 'Малая техника',
                        'children': [
                            {'name': 'Микроволновки'},
                            {'name': 'Кофемашины'},
                            {'name': 'Пылесосы'},
                            {'name': 'Утюги'},
                        ]
                    },
                ]
            },
            {
                'name': 'Спорт и отдых',
                'icon': 'fas fa-dumbbell',
                'sort_order': 80,
                'children': [
                    {
                        'name': 'Фитнес',
                        'children': [
                            {'name': 'Тренажеры'},
                            {'name': 'Гантели и штанги'},
                            {'name': 'Коврики для йоги'},
                            {'name': 'Спортивная одежда'},
                        ]
                    },
                    {
                        'name': 'Активный отдых',
                        'children': [
                            {'name': 'Велосипеды'},
                            {'name': 'Ролики'},
                            {'name': 'Самокаты'},
                            {'name': 'Туризм'},
                        ]
                    },
                ]
            },
        ]

        def create_category(category_data, parent=None):
            """Рекурсивно создает категории"""
            # Создаем уникальный slug
            base_slug = slugify(category_data['name'])
            slug = base_slug
            counter = 1
            while Category.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            
            category, created = Category.objects.update_or_create(
                name=category_data['name'],
                parent=parent,
                defaults={
                    'slug': slug,
                    'icon': category_data.get('icon', ''),
                    'sort_order': category_data.get('sort_order', 0),
                    'show_in_megamenu': True,
                }
            )
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'Создана категория: {category.name}'))
            else:
                self.stdout.write(self.style.SUCCESS(f'Обновлена категория: {category.name}'))

            # Создаем дочерние категории
            for child_data in category_data.get('children', []):
                create_category(child_data, parent=category)

        # Создаем все категории
        for category_data in categories_data:
            create_category(category_data)

        self.stdout.write(self.style.SUCCESS('Успешно загружен каталог OZON!'))
