import logging
from django.core.cache import cache
from django.utils import timezone
from main.models import Tag, Profile


logger = logging.getLogger('default')


class CachedDataService:
    """
    A class for managing cached data operations, particularly popular tags and users to improve performance.
    This class provides methods to retrieve and update cached data, with fallback mechanisms
    to fetch fresh data when the cache is empty or invalid.
    """
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
        return Tag.popular

    def get_cached_tags(self):
        popular_tags = cache.get(self.CACHE_KEYS['popular_tags'])
        if not popular_tags:
            return self.update_cache()['popular_tags']
        return popular_tags

    @staticmethod
    def get_popular_users():
        return Profile.popular.select_related('user')

    def get_cached_users(self):
        popular_users = cache.get(self.CACHE_KEYS['popular_users'])
        if not popular_users:
            return self.update_cache()['popular_users']
        return popular_users
