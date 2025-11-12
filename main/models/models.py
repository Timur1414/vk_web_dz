from __future__ import annotations
import logging
import bleach
from bleach.css_sanitizer import CSSSanitizer
from typing import Optional
from vk_dz import settings
from django.core.files.uploadedfile import UploadedFile
from django.contrib.auth.models import User
from django.db import models
from django.db.models import QuerySet, Q
from random import choice
from main.models.managers import NewManager
from main.models.base import RatingModel, Like
from django_ckeditor_5.fields import CKEditor5Field


logger = logging.getLogger('default')


class Tag(RatingModel):
    """
    Model representing a tag that can be associated with questions.

    Inherits from RatingModel to support rating functionality.
    Each tag has a text and a color for display purposes.

    Attributes:
        COLORS: List of available color choices for tags
        text (str): The text content of the tag (max 50 chars)
        color (str): The display color of the tag, chosen from COLORS
    """
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
        if created:
            obj.color = choice([color[0] for color in Tag.COLORS])
            obj.save()
            logger.debug('created new tag (id=%s)', obj.id)
        return obj

    def save(self, *args, **kwargs):
        if not self.color:
            self.color = choice([color[0] for color in self.COLORS])
        super().save(*args, **kwargs)

    def __str__(self):
        return self.text


class Question(RatingModel):
    """
    Model representing a question.

    Inherits from RatingModel to support rating functionality.
    Questions can have multiple tags and are associated with an author.

    Attributes:
        title (str): The title of the question (max 100 chars)
        text (str): The full text/content of the question
        author (User): The user who asked
        created_at (datetime): When the question was created
        tags (ManyToManyField[Tag]): Tags associated with the question
        count_answers (int): Number of answers associated with the question
    """
    title = models.CharField(max_length=100)
    text = CKEditor5Field()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    tags = models.ManyToManyField(Tag)
    count_answers = models.IntegerField(default=0)

    new = NewManager()

    class Meta:
        indexes = [
            models.Index(fields=['-created_at'], name='question_created_at_desc'),
        ]

    def save(self, *args, **kwargs):
        self.text = bleach.clean(
            self.text,
            tags=settings.ALLOWED_TAGS,
            attributes=settings.ALLOWED_ATTRIBUTES,
            css_sanitizer=CSSSanitizer(allowed_css_properties=settings.ALLOWED_STYLES),
        )
        super().save(*args, **kwargs)

    @staticmethod
    def create(title: str, text: str, author: User) -> Question:
        question = Question(title=title, text=text, author=author)
        question.save()
        logger.debug('created new question (id=%s)', question.id)
        return question

    def add_tag(self, tag: Tag):
        self.tags.add(tag)
        self.save()
        logger.debug('added tag (id=%s) to question (id=%s)', tag.id, self.id)

    @staticmethod
    def find_by_text(text: str, limit: int = 5) -> QuerySet:
        select_related = ['author', 'author__profile']
        prefetch_related = ['tags']
        logger.debug('find questions by text=%s', text)
        return Question.popular.get_queryset_with_related(
            select_related=select_related,
            prefetch_related=prefetch_related).filter(Q(title__icontains=text) | Q(text__icontains=text))[:limit]

    @staticmethod
    def get_question_by_id(id: int) -> Optional[Question]:
        logger.debug('get question by id=%s', id)
        try:
            return Question.objects.get(id=id)
        except Question.DoesNotExist:
            logger.error('no question with id=%s', id)
            return None

    @staticmethod
    def get_questions_by_author(user: User) -> QuerySet:
        logger.debug('get questions by author (id=%s)', user.id)
        select_related = ['author', 'author__profile']
        prefetch_related = ['tags']
        return Question.popular.get_queryset_with_related(
            select_related=select_related,
            prefetch_related=prefetch_related
        ).filter(Q(author=user) | Q(answer__author=user)).distinct()

    @staticmethod
    def get_questions_by_tag(tag: str) -> QuerySet:
        logger.debug('get questions by tag=%s', tag)
        return (Question.objects.filter(tags__text__contains=tag).order_by('-rating').distinct()
                .select_related('author', 'author__profile').prefetch_related('tags'))


class Answer(RatingModel):
    """
    Model representing an answer to a question.

    Inherits from RatingModel to support rating functionality.
    Each answer is associated with a question and an author.

    Attributes:
        text (str): The content of the answer
        author (User): The user who posted the answer
        created_at (datetime): When the answer was created
        is_correct (bool): Whether this answer is marked as correct
        question (Question): The question this answer belongs to
    """
    text = CKEditor5Field()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_correct = models.BooleanField(default=False)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)

    new = NewManager()

    class Meta:
        indexes = [
            models.Index(fields=['-created_at'], name='answer_created_at_desc'),
        ]

    def save(self, *args, **kwargs):
        self.text = bleach.clean(
            self.text,
            tags=settings.ALLOWED_TAGS,
            attributes=settings.ALLOWED_ATTRIBUTES,
            css_sanitizer=CSSSanitizer(allowed_css_properties=settings.ALLOWED_STYLES),
        )
        self.question.count_answers += 1
        self.question.save()
        super().save(*args, **kwargs)

    def change_correct(self):
        self.is_correct = not self.is_correct
        self.save()
        logger.debug('answer (id=%s) now correct=%s', self.id, self.is_correct)

    @staticmethod
    def get_answer_by_id(id: int) -> Optional[Answer]:
        logger.debug('get answer by id=%s', id)
        try:
            return Answer.objects.get(id=id)
        except Answer.DoesNotExist:
            logger.error('no answer with id=%s', id)
            return None

    @staticmethod
    def get_answers_by_author(user: User) -> QuerySet:
        logger.debug('get answers by author (id=%s)', user.id)
        select_related = ['author', 'author__profile', 'question']
        return Answer.popular.get_queryset_with_related(select_related=select_related).filter(author=user)

    @staticmethod
    def get_answers_by_question(question: Question) -> QuerySet:
        logger.debug('get answers by question=%s', question.id)
        return Answer.objects.select_related('author', 'author__profile').filter(question=question).order_by('-rating')


class Profile(RatingModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(default='default.png', upload_to='uploads/')
    nickname = models.CharField(max_length=50)

    @staticmethod
    def get_popular_users(limit: int = 5) -> list[User]:
        logger.debug('get popular users')
        profiles = Profile.objects.order_by('-rating')[:limit]
        users = [profile.user for profile in profiles]
        return users

    def update(self, avatar: UploadedFile = None, rating: int = None, nickname: str = None):
        if avatar:
            logger.debug('update avatar of profile=%s', self.id)
            self.avatar.save(avatar.name, avatar)
        if rating:
            logger.debug('update rating of profile=%s', self.id)
            self.rating = rating
        if nickname:
            logger.debug('update nickname of profile=%s', self.id)
            self.nickname = nickname
        self.save()

    @staticmethod
    def create(user: User) -> Profile:
        profile = Profile(user=user)
        profile.save()
        logger.debug('created new profile (id=%s)', profile.id)
        return profile

    @staticmethod
    def get_profile_of_user(user: User) -> Optional[Profile]:
        logger.debug('get profile by user=%s', user.id)
        if user.is_anonymous:
            logger.error('user is anonymous')
            return None
        try:
            return Profile.objects.get(user=user)
        except Profile.DoesNotExist:
            logger.error('no profile with user=%s', user.id)
            return None

    def __str__(self):
        return self.nickname


class QuestionLike(Like):
    """
    Like model specifically for Questions.

    Inherits from the abstract Like model to implement like functionality
    for questions.

    Attributes:
        question (Question): The question being liked
    """
    question = models.ForeignKey(Question, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'question'],
                name='question_like_unique',
            )
        ]

    def update_ratings(self):
        logger.debug('update ratings of question (id=%s) and components', self.question.id)
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
        logger.debug('like question (id=%s)', question.id)
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
        if created:
            logger.debug('created new question like (id=%s)', question.id)
        return obj, created


class AnswerLike(Like):
    """
    Like model specifically for Answers.

    Inherits from the abstract Like model to implement like functionality
    for answers.

    Attributes:
        answer (Answer): The answer being liked
    """
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
        logger.debug('update ratings of answer (id=%s) and components', self.answer.id)
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
        logger.debug('like answer (id=%s)', answer.id)
        like, created = AnswerLike.create(user, answer)
        if not created:
            like.active = not like.active
            like.save()
        like.update_ratings()
        return like

    @staticmethod
    def create(user: User, answer: Answer) -> tuple[AnswerLike, bool]:
        obj, created = AnswerLike.objects.get_or_create(author=user, answer=answer)
        if created:
            logger.debug('created new answer like (id=%s)', answer.id)
        return obj, created
