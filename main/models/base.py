from __future__ import annotations
from typing import Any
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db import models
from main.models.managers import PopularManager


class RatingModel(models.Model):
    rating = models.IntegerField(default=0, validators=[MinValueValidator(0)])

    objects = models.Manager()
    popular = PopularManager()

    class Meta:
        abstract = True

    def increase_rating(self):
        self.rating += 1
        self.save()

    def decrease_rating(self):
        self.rating -= 1
        self.save()


class Like(models.Model):
    active = models.BooleanField(default=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        abstract = True

    def update_ratings(self):
        raise NotImplementedError()

    @staticmethod
    def like(obj, user: User):
        raise NotImplementedError()

    @staticmethod
    def is_liked(obj, user: User) -> bool:
        raise NotImplementedError()

    @staticmethod
    def create(obj, user: User) -> tuple[Any, bool]:
        raise NotImplementedError()
