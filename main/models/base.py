from __future__ import annotations
import logging
from typing import Any
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db import models
from main.models.managers import PopularManager


logger = logging.getLogger('default')


class RatingModel(models.Model):
    """
    Abstract base model that provides rating functionality for inheriting models.

    This model includes a rating field and methods to increment and decrement the rating.
    It uses a custom manager 'popular' for querying popular items.

    Attributes:
        rating (int): The current rating of the model instance (default: 0, min: 0)
    """
    rating = models.IntegerField(default=0, validators=[MinValueValidator(0)])

    objects = models.Manager()
    popular = PopularManager()

    class Meta:
        abstract = True
        indexes = [
            models.Index(fields=['-rating'], name='%(class)s_rating_desc'),
        ]

    def increase_rating(self):
        logger.debug('increase rating of "%s"', self.__class__.__name__)
        self.rating += 1
        self.save()

    def decrease_rating(self):
        logger.debug('decrease rating of "%s"', self.__class__.__name__)
        self.rating -= 1
        self.save()

    def update_rating(self):
        raise NotImplementedError()


class Like(models.Model):
    """
    Abstract base model for implementing like functionality.

    This model serves as a base for creating like relationships between users and other models.
    It must be subclassed with specific implementations for the abstract methods.

    Attributes:
        is_active (bool): Indicates if the like is currently active (default: True)
        author (User): The user who created the like
    """
    is_active = models.BooleanField(default=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        abstract = True

    def update_ratings(self):
        raise NotImplementedError()

    @staticmethod
    def like(obj, user: User, need_to_update: bool):
        raise NotImplementedError()

    @staticmethod
    def is_liked(obj, user: User) -> bool:
        raise NotImplementedError()

    @staticmethod
    def create(obj, user: User) -> tuple[Any, bool]:
        raise NotImplementedError()
