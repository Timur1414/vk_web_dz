import logging
from django.db import models


logger = logging.getLogger('default')


class BaseManager(models.Manager):
    """
    Base manager for retrieving base queryset with select_related or prefetch_related options.
    """

    def get_queryset_with_related(self, select_related: list = None, prefetch_related: list = None):
        if select_related is None and prefetch_related is None:
            return self.get_queryset()
        if prefetch_related is None:
            return self.get_queryset().select_related(*select_related)
        if select_related is None:
            return self.get_queryset().prefetch_related(*prefetch_related)
        return self.get_queryset().select_related(*select_related).prefetch_related(*prefetch_related)


class PopularManager(BaseManager):
    """
    Custom manager for retrieving popular items based on their rating.
    
    This manager provides methods to retrieve items ordered by their rating in descending order,
    making it easy to get the most popular items.
    
    Methods:
        get_queryset(): Returns the base queryset ordered by rating in descending order.
        get_popular(limit=5): Returns a limited number of the most popular items.
    """

    def get_queryset(self):
        logger.debug('get queryset by popular')
        return super().get_queryset().order_by('-rating')

    def get_popular(self, limit=5):
        logger.debug('get queryset by popular with limit')
        return self.get_queryset().order_by('-rating')[:limit]

    def get_popular_with_related(self, select_related: list = None, prefetch_related: list = None, limit: int = 5):
        logger.debug('get queryset by popular with related fields')
        if select_related is None and prefetch_related is None:
            return self.get_popular()
        if prefetch_related is None:
            return self.get_popular(limit=limit).select_related(*select_related)
        if select_related is None:
            return self.get_popular(limit=limit).prefetch_related(*prefetch_related)
        return self.get_popular(limit=limit).select_related(*select_related).prefetch_related(*prefetch_related)


class NewManager(BaseManager):
    """
    Custom manager for retrieving the most recently created items.
    
    This manager provides methods to retrieve items ordered by their creation date
    in descending order, making it easy to get the newest items.
    
    Methods:
        get_queryset(): Returns the base queryset ordered by creation date in descending order.
        get_new(limit=5): Returns a limited number of the most recently created items.
    """

    def get_queryset(self):
        logger.debug('get queryset by date')
        return super().get_queryset().order_by('-created_at')

    def get_new(self, limit=5):
        logger.debug('get queryset by date with limit')
        return self.get_queryset().order_by('-created_at')[:limit]

    def get_new_with_related(self, select_related: list = None, prefetch_related: list = None, limit: int = 5):
        logger.debug('get queryset by date with related fields')
        if select_related is None and prefetch_related is None:
            return self.get_new()
        if prefetch_related is None:
            return self.get_new(limit=limit).select_related(*select_related)
        if select_related is None:
            return self.get_new(limit=limit).prefetch_related(*prefetch_related)
        return self.get_new(limit=limit).select_related(*select_related).prefetch_related(*prefetch_related)
