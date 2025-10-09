from __future__ import annotations
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db import models

from main.models.managers import PopularManager, NewManager


class Tag(models.Model):
    text = models.CharField(max_length=50)

    popular = PopularManager()


class Question(models.Model):
    title = models.CharField(max_length=100)
    text = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    tags = models.ManyToManyField(Tag)
    rating = models.IntegerField(default=0, validators=[MinValueValidator(0)])

    popular = PopularManager()
    new = NewManager()


class Answer(models.Model):
    text = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_correct = models.BooleanField(default=False)
    rating = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    question = models.ForeignKey(Question, on_delete=models.CASCADE)

    new = NewManager()


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(default='default.png', upload_to='uploads/')
    rating = models.IntegerField(default=0, validators=[MinValueValidator(0)])

    popular = PopularManager()

    @staticmethod
    def create(user: User) -> Profile:
        profile = Profile(user=user)
        profile.save()
        return profile

    @staticmethod
    def get_profile_of_user(user: User) -> Profile:
        return Profile.objects.get(user=user)


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
