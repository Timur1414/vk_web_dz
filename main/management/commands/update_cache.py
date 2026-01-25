from django.core.management.base import BaseCommand
from main.cached_data_service import CachedDataService


class Command(BaseCommand):
    help = 'Update cache data: popular tags and best users'

    def handle(self, *args, **options):
        print('start updating cache...')
        cache = CachedDataService()
        cache.update_cache()
        print('cache updated')
