import logging
from django.core.cache import cache
from django.utils import timezone
from main.models import Tag, Profile


logger = logging.getLogger('default')


class CachedDataService:
    CACHE_KEYS = {
        'popular_tags': 'popular_tags',
        'popular_users': 'popular_users',
        'last_updated': 'last_updated'
    }

    def update_cache(self):
        logger.debug('updating cache')
        popular_tags = self.get_popular_tags()
        popular_users = self.get_popular_users()
        cache.set(self.CACHE_KEYS['popular_tags'], popular_tags, None)
        cache.set(self.CACHE_KEYS['popular_users'], popular_users, None)
        cache.set(self.CACHE_KEYS['last_updated'], timezone.now(), None)
        return {
            'popular_tags': popular_tags,
            'popular_users': popular_users,
        }

    @staticmethod
    def get_popular_tags():
        return Tag.popular.get_popular()

    def get_cached_tags(self):
        popular_tags = cache.get(self.CACHE_KEYS['popular_tags'])
        if not popular_tags:
            return self.update_cache()['popular_tags']
        return popular_tags

    @staticmethod
    def get_popular_users():
        return Profile.popular.get_popular_with_related(select_related=['user'])

    def get_cached_users(self):
        popular_users = cache.get(self.CACHE_KEYS['popular_users'])
        if not popular_users:
            return self.update_cache()['popular_users']
        return popular_users
