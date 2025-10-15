from django.db import models


class PopularManager(models.Manager):
    """
    Custom manager for retrieving popular items based on their rating.
    
    This manager provides methods to retrieve items ordered by their rating in descending order,
    making it easy to get the most popular items.
    
    Methods:
        get_queryset(): Returns the base queryset ordered by rating in descending order.
        get_popular(limit=5): Returns a limited number of the most popular items.
    """
    def get_queryset(self):
        return super().get_queryset().order_by('-rating')

    def get_popular(self, limit=5):
        return self.get_queryset().order_by('-rating')[:limit]


class NewManager(models.Manager):
    """
    Custom manager for retrieving the most recently created items.
    
    This manager provides methods to retrieve items ordered by their creation date
    in descending order, making it easy to get the newest items.
    
    Methods:
        get_queryset(): Returns the base queryset ordered by creation date in descending order.
        get_new(limit=5): Returns a limited number of the most recently created items.
    """
    def get_queryset(self):
        return super().get_queryset().order_by('-created_at')

    def get_new(self, limit=5):
        return self.get_queryset().order_by('-created_at')[:limit]
