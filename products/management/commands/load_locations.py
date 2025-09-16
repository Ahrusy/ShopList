from django.core.management.base import BaseCommand
from products.models import Location


class Command(BaseCommand):
    help = 'Загружает базовые локации'

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
            }
        ]

        for location_data in locations_data:
            location, created = Location.objects.get_or_create(
                name=location_data['name'],
                region=location_data['region'],
                defaults=location_data
            )
            if created:
                self.stdout.write(f'Создана локация: {location.name}, {location.region}')
            else:
                self.stdout.write(f'Локация уже существует: {location.name}, {location.region}')

        self.stdout.write(
            self.style.SUCCESS('Успешно загружены все локации!')
        )