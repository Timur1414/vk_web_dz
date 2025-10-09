# from __future__ import annotations
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db import models


class Tag(models.Model):
    text = models.CharField(max_length=50)

class Question(models.Model):
    title = models.CharField(max_length=100)
    text = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    tags = models.ManyToManyField(Tag)
    rating = models.IntegerField(default=0, validators=[MinValueValidator(0)])

class Answer(models.Model):
    text = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_correct = models.BooleanField(default=False)
    rating = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    question = models.ForeignKey(Question, on_delete=models.CASCADE)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(default='default.jpg', upload_to='uploads/')
    rating = models.IntegerField(default=0, validators=[MinValueValidator(0)])

class QuestionLike(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)

class AnswerLike(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)
