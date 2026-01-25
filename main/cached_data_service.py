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
    POPULAR_TAGS_KEY = 'popular_tags'
    POPULAR_USERS_KEY = 'popular_users'
    LAST_UPDATED_KEY = 'last_updated'

    def update_cache(self):
        logger.debug('updating cache')
        popular_tags = self.get_popular_tags()
        popular_users = self.get_popular_users()
        cache.set(self.POPULAR_TAGS_KEY, popular_tags, None)
        cache.set(self.POPULAR_USERS_KEY, popular_users, None)
        cache.set(self.LAST_UPDATED_KEY, timezone.now(), None)
        return {
            'popular_tags': popular_tags,
            'popular_users': popular_users,
        }

    @staticmethod
    def get_popular_tags():
        return Tag.popular.get_queryset()[:5]

    def get_cached_tags(self):
        popular_tags = cache.get(self.POPULAR_TAGS_KEY)
        if not popular_tags:
            return self.update_cache()['popular_tags']
        return popular_tags

    @staticmethod
    def get_popular_users():
        return Profile.popular.select_related('user')[:5]

    def get_cached_users(self):
        popular_users = cache.get(self.POPULAR_USERS_KEY)
        if not popular_users:
            return self.update_cache()['popular_users']
        return popular_users
