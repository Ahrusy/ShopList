from django.core.management.base import BaseCommand
from products.models import Category


class Command(BaseCommand):
    help = 'Create specific Russian translations for subcategories'

    def handle(self, *args, **options):
        self.stdout.write('Creating subcategory translations...')
        
        # Специфичные переводы для подкатегорий
        subcategory_translations = {
            # Электроника подкатегории
            'smartphones': 'Смартфоны',
            'laptops': 'Ноутбуки', 
            'tablets': 'Планшеты',
            'headphones': 'Наушники',
            'cameras': 'Фотокамеры',
            'gaming': 'Игровые консоли',
            'tv': 'Телевизоры',
            'audio': 'Аудиотехника',
            'accessories': 'Аксессуары',
            
            # Одежда подкатегории
            'mens-clothing': 'Мужская одежда',
            'womens-clothing': 'Женская одежда', 
            'kids-clothing': 'Детская одежда',
            'shoes': 'Обувь',
            'bags': 'Сумки и рюкзаки',
            'jewelry': 'Украшения',
            'watches': 'Часы',
            
            # Красота подкатегории
            'skincare': 'Уход за кожей',
            'makeup': 'Декоративная косметика',
            'perfume': 'Парфюмерия',
            'haircare': 'Уход за волосами',
            'health': 'Здоровье',
            'supplements': 'БАДы и витамины',
            
            # Спорт подкатегории
            'fitness': 'Фитнес и тренажеры',
            'outdoor': 'Активный отдых',
            'team-sports': 'Командные виды спорта',
            'water-sports': 'Водные виды спорта',
            'winter-sports': 'Зимние виды спорта',
            'cycling': 'Велоспорт',
            'running': 'Бег и легкая атлетика',
            
            # Дом и сад подкатегории
            'furniture': 'Мебель',
            'decor': 'Декор и интерьер',
            'kitchen': 'Кухонные принадлежности',
            'garden': 'Сад и огород',
            'tools': 'Инструменты',
            'lighting': 'Освещение',
            'textiles': 'Текстиль для дома',
            
            # Автотовары подкатегории
            'car-parts': 'Запчасти',
            'car-accessories': 'Автоаксессуары',
            'oils': 'Масла и жидкости',
            'tires': 'Шины и диски',
            'car-electronics': 'Автоэлектроника',
            'car-care': 'Автохимия',
            
            # Книги подкатегории
            'fiction': 'Художественная литература',
            'non-fiction': 'Нехудожественная литература',
            'children-books': 'Детские книги',
            'textbooks': 'Учебная литература',
            'comics': 'Комиксы и манга',
            
            # Продукты подкатегории
            'groceries': 'Продукты питания',
            'beverages': 'Напитки',
            'snacks': 'Снеки и сладости',
            'organic': 'Органические продукты',
            'frozen': 'Замороженные продукты',
            
            # Животные подкатегории
            'pet-food': 'Корм для животных',
            'pet-toys': 'Игрушки для животных',
            'pet-care': 'Уход за животными',
            'aquarium': 'Аквариумистика',
            'bird-supplies': 'Товары для птиц'
        }
        
        # Обновляем переводы подкатегорий
        categories = Category.objects.filter(parent__isnull=False)  # Только подкатегории
        
        updated_count = 0
        for category in categories:
            # Пытаемся найти подходящий перевод
            russian_name = self.find_subcategory_translation(category.slug, subcategory_translations)
            
            if russian_name:
                try:
                    translation, created = category.translations.get_or_create(
                        language_code='ru',
                        defaults={
                            'name': russian_name,
                            'description': f'Подкатегория {russian_name}'
                        }
                    )
                    
                    if not created and translation.name != russian_name:
                        translation.name = russian_name
                        translation.description = f'Подкатегория {russian_name}'
                        translation.save()
                        updated_count += 1
                        
                    if updated_count < 20:  # Показываем первые 20
                        self.stdout.write(f'Updated subcategory: {category.slug} -> {russian_name}')
                        
                except Exception as e:
                    self.stdout.write(f'Error updating subcategory {category.slug}: {str(e)}')
        
        self.stdout.write(self.style.SUCCESS(f'Successfully updated {updated_count} subcategory translations'))

    def find_subcategory_translation(self, slug, translations_dict):
        """Находит подходящий перевод для подкатегории"""
        
        # Проверяем точные совпадения
        for key, translation in translations_dict.items():
            if key in slug.lower():
                return translation
        
        # Проверяем частичные совпадения
        slug_lower = slug.lower()
        
        if 'smartphone' in slug_lower or 'phone' in slug_lower:
            return 'Смартфоны'
        elif 'laptop' in slug_lower or 'notebook' in slug_lower:
            return 'Ноутбуки'
        elif 'tablet' in slug_lower:
            return 'Планшеты'
        elif 'headphone' in slug_lower or 'earphone' in slug_lower:
            return 'Наушники'
        elif 'camera' in slug_lower or 'photo' in slug_lower:
            return 'Фотокамеры'
        elif 'game' in slug_lower or 'console' in slug_lower:
            return 'Игровые консоли'
        elif 'tv' in slug_lower or 'television' in slug_lower:
            return 'Телевизоры'
        elif 'audio' in slug_lower or 'speaker' in slug_lower:
            return 'Аудиотехника'
        elif 'men' in slug_lower and 'cloth' in slug_lower:
            return 'Мужская одежда'
        elif 'women' in slug_lower and 'cloth' in slug_lower:
            return 'Женская одежда'
        elif 'kid' in slug_lower or 'child' in slug_lower:
            return 'Детские товары'
        elif 'shoe' in slug_lower or 'boot' in slug_lower:
            return 'Обувь'
        elif 'bag' in slug_lower or 'backpack' in slug_lower:
            return 'Сумки и рюкзаки'
        elif 'watch' in slug_lower or 'clock' in slug_lower:
            return 'Часы'
        elif 'skin' in slug_lower or 'face' in slug_lower:
            return 'Уход за кожей'
        elif 'makeup' in slug_lower or 'cosmetic' in slug_lower:
            return 'Косметика'
        elif 'perfume' in slug_lower or 'fragrance' in slug_lower:
            return 'Парфюмерия'
        elif 'hair' in slug_lower:
            return 'Уход за волосами'
        elif 'fitness' in slug_lower or 'gym' in slug_lower:
            return 'Фитнес'
        elif 'outdoor' in slug_lower or 'camping' in slug_lower:
            return 'Активный отдых'
        elif 'sport' in slug_lower:
            return 'Спортивные товары'
        elif 'furniture' in slug_lower or 'chair' in slug_lower or 'table' in slug_lower:
            return 'Мебель'
        elif 'kitchen' in slug_lower or 'cook' in slug_lower:
            return 'Кухонные принадлежности'
        elif 'garden' in slug_lower or 'plant' in slug_lower:
            return 'Сад и огород'
        elif 'tool' in slug_lower:
            return 'Инструменты'
        elif 'car' in slug_lower or 'auto' in slug_lower:
            return 'Автотовары'
        elif 'book' in slug_lower:
            return 'Книги'
        elif 'food' in slug_lower or 'eat' in slug_lower:
            return 'Продукты питания'
        elif 'pet' in slug_lower or 'animal' in slug_lower:
            return 'Товары для животных'
        
        return None