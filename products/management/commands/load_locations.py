from django.core.management.base import BaseCommand
from products.models import Location


class Command(BaseCommand):
    help = 'Загружает начальные данные локаций'

    def handle(self, *args, **options):
        locations_data = [
            {
                'name': 'Москва',
                'region': 'Московская область',
                'country': 'Россия',
                'latitude': 55.7558,
                'longitude': 37.6176,
                'is_active': True
            },
            {
                'name': 'Санкт-Петербург',
                'region': 'Ленинградская область',
                'country': 'Россия',
                'latitude': 59.9311,
                'longitude': 30.3609,
                'is_active': True
            },
            {
                'name': 'Новосибирск',
                'region': 'Новосибирская область',
                'country': 'Россия',
                'latitude': 55.0084,
                'longitude': 82.9357,
                'is_active': True
            },
            {
                'name': 'Екатеринбург',
                'region': 'Свердловская область',
                'country': 'Россия',
                'latitude': 56.8431,
                'longitude': 60.6454,
                'is_active': True
            },
            {
                'name': 'Казань',
                'region': 'Республика Татарстан',
                'country': 'Россия',
                'latitude': 55.8304,
                'longitude': 49.0661,
                'is_active': True
            },
            {
                'name': 'Нижний Новгород',
                'region': 'Нижегородская область',
                'country': 'Россия',
                'latitude': 56.2965,
                'longitude': 43.9361,
                'is_active': True
            },
            {
                'name': 'Челябинск',
                'region': 'Челябинская область',
                'country': 'Россия',
                'latitude': 55.1644,
                'longitude': 61.4368,
                'is_active': True
            },
            {
                'name': 'Самара',
                'region': 'Самарская область',
                'country': 'Россия',
                'latitude': 53.2001,
                'longitude': 50.1500,
                'is_active': True
            },
            {
                'name': 'Омск',
                'region': 'Омская область',
                'country': 'Россия',
                'latitude': 54.9885,
                'longitude': 73.3242,
                'is_active': True
            },
            {
                'name': 'Ростов-на-Дону',
                'region': 'Ростовская область',
                'country': 'Россия',
                'latitude': 47.2357,
                'longitude': 39.7015,
                'is_active': True
            },
            {
                'name': 'Уфа',
                'region': 'Республика Башкортостан',
                'country': 'Россия',
                'latitude': 54.7388,
                'longitude': 55.9721,
                'is_active': True
            },
            {
                'name': 'Красноярск',
                'region': 'Красноярский край',
                'country': 'Россия',
                'latitude': 56.0184,
                'longitude': 92.8672,
                'is_active': True
            },
            {
                'name': 'Воронеж',
                'region': 'Воронежская область',
                'country': 'Россия',
                'latitude': 51.6720,
                'longitude': 39.1843,
                'is_active': True
            },
            {
                'name': 'Пермь',
                'region': 'Пермский край',
                'country': 'Россия',
                'latitude': 58.0105,
                'longitude': 56.2502,
                'is_active': True
            },
            {
                'name': 'Волгоград',
                'region': 'Волгоградская область',
                'country': 'Россия',
                'latitude': 48.7080,
                'longitude': 44.5133,
                'is_active': True
            }
        ]

        created_count = 0
        updated_count = 0

        for location_data in locations_data:
            location, created = Location.objects.get_or_create(
                name=location_data['name'],
                defaults=location_data
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Создана локация: {location.name}')
                )
            else:
                # Обновляем существующую локацию
                for key, value in location_data.items():
                    setattr(location, key, value)
                location.save()
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'Обновлена локация: {location.name}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'Загрузка завершена. Создано: {created_count}, обновлено: {updated_count}'
            )
        )

