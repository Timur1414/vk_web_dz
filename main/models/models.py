from __future__ import annotations
from typing import Optional
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import QuerySet
from random import choice
from main.models.managers import PopularManager, NewManager


class Tag(models.Model):
    COLORS = [
        ('primary', 'primary'),
        ('secondary', 'secondary'),
        ('success', 'success'),
        ('danger', 'danger'),
        ('warning', 'warning'),
        ('info', 'info'),
        ('dark', 'dark'),
    ]

    text = models.CharField(max_length=50)
    rating = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    color = models.CharField(max_length=50, choices=COLORS, default='dark')

    objects = models.Manager()
    popular = PopularManager()

    def save(self, *args, **kwargs):
        if not self.color:
            self.color = choice([color[0] for color in self.COLORS])
        super().save(*args, **kwargs)

    @staticmethod
    def get_popular(limit: int = 5) -> QuerySet:
        return Tag.objects.order_by('-rating')[:limit]

    def __str__(self):
        return self.text


class Question(models.Model):
    title = models.CharField(max_length=100)
    text = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    tags = models.ManyToManyField(Tag)
    rating = models.IntegerField(default=0, validators=[MinValueValidator(0)])

    objects = models.Manager()
    popular = PopularManager()
    new = NewManager()

    @staticmethod
    def get_question_by_id(id: int) -> Optional[Question]:
        try:
            return Question.objects.get(id)
        except Question.DoesNotExist:
            return None

    @staticmethod
    def get_questions_by_tag(tag: str) -> QuerySet:
        return Question.objects.filter(tags__text__contains=tag).order_by('-rating')


class Answer(models.Model):
    text = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_correct = models.BooleanField(default=False)
    rating = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    question = models.ForeignKey(Question, on_delete=models.CASCADE)

    objects = models.Manager()
    new = NewManager()

    @staticmethod
    def get_answers_by_question(question: Question) -> QuerySet:
        return Answer.objects.filter(question=question).order_by('-rating')


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(default='default.png', upload_to='uploads/')
    rating = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    nickname = models.CharField(max_length=50)

    objects = models.Manager()
    popular = PopularManager()

    @staticmethod
    def get_popular_users(limit: int = 5) -> list[User]:
        profiles = Profile.objects.order_by('-rating')[:limit]
        users = [profile.user for profile in profiles]
        return users

    @staticmethod
    def get_popular(limit: int = 5) -> QuerySet:
        return Profile.objects.order_by('-rating')[:limit]

    @staticmethod
    def create(user: User) -> Profile:
        profile = Profile(user=user)
        profile.save()
        return profile

    @staticmethod
    def get_profile_of_user(user: User) -> Optional[Profile]:
        if user.is_anonymous:
            return None
        try:
            return Profile.objects.get(user=user)
        except Profile.DoesNotExist:
            return None

    def __str__(self):
        return self.nickname


class QuestionLike(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'question'],
                name='question_like_unique',
            )
        ]

    @staticmethod
    def create(user: User, question: Question) -> QuestionLike:
        obj, created = QuestionLike.objects.get_or_create(author=user, question=question)
        return obj


class AnswerLike(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'answer'],
                name='answer_like_unique',
            )
        ]

    @staticmethod
    def create(user: User, answer: Answer) -> AnswerLike:
        obj, created = AnswerLike.objects.get_or_create(author=user, answer=answer)
        return obj
