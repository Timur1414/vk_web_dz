from __future__ import annotations
from typing import Optional
from django.core.files.uploadedfile import UploadedFile
from django.contrib.auth.models import User
from django.db import models
from django.db.models import QuerySet, Q
from random import choice
from main.models.managers import NewManager
from main.models.base import RatingModel, Like


class Tag(RatingModel):
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
    color = models.CharField(max_length=50, choices=COLORS, default='dark')

    @staticmethod
    def get_or_create(text: str) -> Tag:
        obj, created = Tag.objects.get_or_create(text=text)
        return obj

    def save(self, *args, **kwargs):
        if not self.color:
            self.color = choice([color[0] for color in self.COLORS])
        super().save(*args, **kwargs)

    def __str__(self):
        return self.text


class Question(RatingModel):
    title = models.CharField(max_length=100)
    text = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    tags = models.ManyToManyField(Tag)

    new = NewManager()

    @staticmethod
    def create(title: str, text: str, author: User) -> Question:
        question = Question(title=title, text=text, author=author)
        question.save()
        return question

    def add_tag(self, tag: Tag):
        self.tags.add(tag)
        self.save()

    @staticmethod
    def find_by_text(text: str, limit: int = 5) -> QuerySet:
        return Question.popular.get_queryset().filter(Q(title__icontains=text) | Q(text__icontains=text))[:limit]

    @staticmethod
    def get_question_by_id(id: int) -> Optional[Question]:
        try:
            return Question.objects.get(id=id)
        except Question.DoesNotExist:
            return None

    @staticmethod
    def get_questions_by_tag(tag: str) -> QuerySet:
        return Question.objects.filter(tags__text__contains=tag).order_by('-rating')


class Answer(RatingModel):
    text = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_correct = models.BooleanField(default=False)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)

    new = NewManager()

    def change_correct(self):
        self.is_correct = not self.is_correct
        self.save()

    @staticmethod
    def get_answer_by_id(id: int) -> Optional[Answer]:
        try:
            return Answer.objects.get(id=id)
        except Answer.DoesNotExist:
            return None

    @staticmethod
    def get_answers_by_question(question: Question) -> QuerySet:
        return Answer.objects.filter(question=question).order_by('-rating')


class Profile(RatingModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(default='default.png', upload_to='uploads/')
    nickname = models.CharField(max_length=50)

    @staticmethod
    def get_popular_users(limit: int = 5) -> list[User]:
        profiles = Profile.objects.order_by('-rating')[:limit]
        users = [profile.user for profile in profiles]
        return users

    def update(self, avatar: UploadedFile = None, rating: int = None, nickname: str = None):
        if avatar:
            self.avatar.save(avatar.name, avatar)
        if rating:
            self.rating = rating
        if nickname:
            self.nickname = nickname
        self.save()

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


class QuestionLike(Like):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'question'],
                name='question_like_unique',
            )
        ]

    def update_ratings(self):
        if self.active:
            self.question.rating += 1
            self.author.profile.rating += 1
            for tag in self.question.tags.all():
                tag.increase_rating()
        else:
            self.question.rating -= 1
            self.author.profile.rating -= 1
            for tag in self.question.tags.all():
                tag.decrease_rating()
        self.question.save()
        self.author.profile.save()

    @staticmethod
    def like(question: Question, user: User) -> Optional[QuestionLike]:
        if user.is_anonymous:
            return None
        like, created = QuestionLike.create(user, question)
        if not created:
            like.active = not like.active
            like.save()
        like.update_ratings()
        return like

    @staticmethod
    def is_liked(question: Question, user: User) -> bool:
        if user.is_anonymous:
            return False
        return QuestionLike.objects.filter(question=question, author=user, active=True).exists()

    @staticmethod
    def create(user: User, question: Question) -> tuple[QuestionLike, bool]:
        obj, created = QuestionLike.objects.get_or_create(author=user, question=question)
        return obj, created


class AnswerLike(Like):
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'answer'],
                name='answer_like_unique',
            )
        ]

    @staticmethod
    def is_liked(answer: Answer, user: User) -> bool:
        if user.is_anonymous:
            return False
        return AnswerLike.objects.filter(answer=answer, author=user, active=True).exists()

    def update_ratings(self):
        if self.active:
            self.answer.rating += 1
            self.author.profile.rating += 1
        else:
            self.answer.rating -= 1
            self.author.profile.rating -= 1
        self.answer.save()
        self.author.profile.save()

    @staticmethod
    def like(answer: Answer, user: User) -> Optional[AnswerLike]:
        if user.is_anonymous:
            return None
        like, created = AnswerLike.create(user, answer)
        if not created:
            like.active = not like.active
            like.save()
        like.update_ratings()
        return like

    @staticmethod
    def create(user: User, answer: Answer) -> tuple[AnswerLike, bool]:
        obj, created = AnswerLike.objects.get_or_create(author=user, answer=answer)
        return obj, created
