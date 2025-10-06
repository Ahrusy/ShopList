"""
Management команда для оптимизации изображений товаров
"""
from django.core.management.base import BaseCommand
from products.services import ImageProcessor
from products.models import ProductImage


class Command(BaseCommand):
    help = 'Оптимизирует изображения товаров, создавая миниатюры разных размеров'

    def add_arguments(self, parser):
        parser.add_argument(
            '--image-id',
            type=int,
            help='ID конкретного изображения для обработки'
        )
        parser.add_argument(
            '--cleanup',
            action='store_true',
            help='Удалить неиспользуемые файлы изображений'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Пересоздать миниатюры даже если они уже существуют'
        )

    def handle(self, *args, **options):
        processor = ImageProcessor()
        
        if options['cleanup']:
            self.stdout.write('Очистка неиспользуемых файлов изображений...')
            deleted_count = processor.cleanup_unused_images()
            self.stdout.write(
                self.style.SUCCESS(f'Удалено {deleted_count} неиспользуемых файлов')
            )
            return
        
        # Определяем какие изображения обрабатывать
        if options['image_id']:
            try:
                images = ProductImage.objects.filter(id=options['image_id'])
                if not images.exists():
                    self.stdout.write(
                        self.style.ERROR(f'Изображение с ID {options["image_id"]} не найдено')
                    )
                    return
            except ValueError:
                self.stdout.write(
                    self.style.ERROR('Некорректный ID изображения')
                )
                return
        else:
            if options['force']:
                images = ProductImage.objects.all()
                self.stdout.write('Обработка всех изображений (принудительно)...')
            else:
                images = ProductImage.objects.filter(thumbnail__isnull=True)
                self.stdout.write('Обработка изображений без миниатюр...')
        
        total_images = images.count()
        if total_images == 0:
            self.stdout.write('Нет изображений для обработки')
            return
        
        self.stdout.write(f'Найдено {total_images} изображений для обработки')
        
        processed_count = 0
        error_count = 0
        
        for i, product_image in enumerate(images.select_related('product'), 1):
            try:
                self.stdout.write(f'Обработка {i}/{total_images}: {product_image}')
                
                if product_image.image:
                    from PIL import Image
                    
                    # Открываем оригинальное изображение
                    image = Image.open(product_image.image.path)
                    image = processor._prepare_image(image)
                    
                    # Создаем миниатюры (только если их нет или принудительно)
                    if options['force'] or not product_image.thumbnail:
                        processor._create_thumbnails(product_image, image)
                        product_image.save()
                    
                    processed_count += 1
                    
                    if i % 10 == 0:  # Показываем прогресс каждые 10 изображений
                        self.stdout.write(f'  Обработано: {processed_count}/{i}')
                        
            except Exception as e:
                error_count += 1
                self.stdout.write(
                    self.style.WARNING(f'  Ошибка при обработке {product_image}: {str(e)}')
                )
                continue
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Обработка завершена. Успешно: {processed_count}, Ошибок: {error_count}'
            )
        )
        
        if error_count > 0:
            self.stdout.write(
                self.style.WARNING(
                    f'При обработке {error_count} изображений возникли ошибки. '
                    'Проверьте файлы и повторите команду.'
                )
            )