from django.db import models


class PopularManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().order_by('-rating')

    def get_popular(self, limit=5):
        return self.get_queryset().order_by('-rating')[:limit]


class NewManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().order_by('-created_at')

    def get_new(self, limit=5):
        return self.get_queryset().order_by('-created_at')[:limit]
