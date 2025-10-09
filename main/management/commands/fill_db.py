from random import choice, sample, randint
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction
from faker import Faker
from main.models.models import Tag, Question, Answer, AnswerLike, QuestionLike


class Command(BaseCommand):
    help = 'Fill database with random data'

    def create_users(self, ratio: int, faker: Faker) -> list[User]:
        users = []
        for i in range(ratio):
            username = f'{faker.user_name()}_{i}'
            email = f'{i}{faker.email()}'
            user = User(username=username, email=email, password='qwerty123')
            users.append(user)
        return User.objects.bulk_create(users)

    def create_tags(self, ratio: int, faker: Faker) -> list[Tag]:
        tags = []
        for i in range(ratio):
            text = f'{faker.word()}_{i}'
            tag = Tag(text=text)
            tags.append(tag)
        return Tag.objects.bulk_create(tags)

    def create_questions(self, ratio: int, users: list[User], tags: list[Tag], faker: Faker) -> list[Question]:
        questions = []
        for _ in range(ratio):
            author = choice(users)
            title = faker.sentence()[:100]
            text = faker.text(max_nb_chars=1000)
            question = Question(author=author, title=title, text=text)
            questions.append(question)
        questions = Question.objects.bulk_create(questions)
        for question in questions:
            selected_tags = sample(tags, randint(1, 5))
            question.tags.add(*selected_tags)
        return questions

    def create_answers(self, ratio: int, questions: list[Question], users: list[User], faker: Faker) -> list[Answer]:
        answers = []
        for _ in range(ratio):
            question = choice(questions)
            author = choice(users)
            text = faker.text(max_nb_chars=1000)
            answer = Answer(author=author, text=text, question=question)
            answers.append(answer)
        return Answer.objects.bulk_create(answers)

    def create_likes(self, ratio: int, questions: list, answers: list, users: list):
        question_likes = set()
        count = 0
        while count < ratio // 2:
            author = choice(users)
            question = choice(questions)
            if (author.id, question.id) not in question_likes:
                question_likes.add((author.id, question.id))
                question_like = QuestionLike(author=author, question=question)
                question_like.save()
                count += 1
        answer_likes = set()
        count = 0
        while count < ratio // 2:
            author = choice(users)
            answer = choice(answers)
            if (author.id, answer.id) not in answer_likes:
                answer_likes.add((author.id, answer.id))
                answer_like = AnswerLike(author=author, answer=answer)
                answer_like.save()
                count += 1

    def add_arguments(self, parser):
        parser.add_argument('ratio', type=int)

    def handle(self, *args, **options):
        print('start...')
        ratio = options['ratio']
        faker = Faker()
        try:
            with transaction.atomic():
                users = self.create_users(ratio, faker)
                print('users created')
                tags = self.create_tags(ratio, faker)
                print('tags created')
                questions = self.create_questions(ratio * 10, users, tags, faker)
                print('questions created')
                answers = self.create_answers(ratio * 100, questions, users, faker)
                print('answers created')
                self.create_likes(ratio * 200, questions, answers, users)
        except Exception as e:
            print(e)
