from random import choice, sample, randint
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import QuerySet
from faker import Faker
from main.models.models import Tag, Question, Answer, AnswerLike, QuestionLike, Profile
from tqdm import tqdm


class Command(BaseCommand):
    """
    Management command to populate the database with test data.
    
    This command creates random users, tags, questions, answers, and likes
    to help with development and testing.
    
    Usage:
        python manage.py fill_db <ratio>
        
    Where <ratio> is the base number of entities to create. The actual number
    of created entities will be a multiple of this ratio.
    """

    help = 'Fill database with random data'

    def create_users(self, ratio: int, faker: Faker) -> QuerySet[User]:
        users = []
        for i in tqdm(range(ratio), desc='Creating users'):
            username = f'{faker.user_name()}_{i}'
            email = f'{i}{faker.email()}'
            user = User(username=username, email=email)
            user.set_password('qwerty123')
            user.save()
            users.append(user)
            profile = user.profile
            nickname = f'{faker.user_name()}_{user.id}'
            rating = randint(1, 100)
            profile.rating = rating
            profile.nickname = nickname
            profile.save()
        users = User.objects.all()
        return users

    def create_tags(self, ratio: int, faker: Faker) -> QuerySet[Tag]:
        tags = []
        for i in tqdm(range(ratio), desc='Creating tags'):
            text = f'{faker.word()}_{i}'
            rating = randint(1, 100)
            color = choice([color[0] for color in Tag.COLORS])
            tag = Tag(text=text, rating=rating, color=color)
            tags.append(tag)
        Tag.objects.bulk_create(tags)
        return Tag.objects.all()

    def create_questions(self, ratio: int, users: QuerySet[User], tags: QuerySet[Tag], faker: Faker) -> QuerySet[Question]:
        questions = []
        for _ in tqdm(range(ratio), desc='Creating questions'):
            author = choice(users)
            title = faker.sentence()[:100]
            text = faker.text(max_nb_chars=1000)
            rating = randint(0, 100)
            question = Question(author=author, title=title, text=text, rating=rating)
            questions.append(question)
        Question.objects.bulk_create(questions)
        questions = Question.objects.all()
        for i in tqdm(range(ratio), desc='Adding tags'):
            question = questions[i]
            selected_tags = sample(list(tags), randint(1, 5))
            question.tags.add(*selected_tags)
        return questions

    def create_answers(self, ratio: int, questions: QuerySet[Question], users: QuerySet[User], faker: Faker) -> QuerySet[Answer]:
        answers = []
        for _ in tqdm(range(ratio), desc='Creating answers'):
            question = choice(questions)
            author = choice(users)
            text = faker.text(max_nb_chars=1000)
            rating = randint(0, 100)
            is_correct = bool(randint(0, 1))
            answer = Answer(author=author, text=text, question=question, rating=rating, is_correct=is_correct)
            question.count_answers += 1
            question.save()
            answers.append(answer)
        Answer.objects.bulk_create(answers)
        return Answer.objects.all()

    def create_likes(self, ratio: int, questions: QuerySet[Question], answers: QuerySet[Answer], users: QuerySet[User]):
        with tqdm(total=ratio, desc='Creating likes') as pbar:
            question_likes = set()
            count = 0
            while count < ratio // 2:
                author = choice(list(users))
                question = choice(list(questions))
                if (author.id, question.id) not in question_likes:
                    question_likes.add((author.id, question.id))
                    question_like = QuestionLike(author=author, question=question)
                    question_like.save()
                    count += 1
                    pbar.update(1)
            answer_likes = set()
            count = 0
            while count < ratio // 2:
                author = choice(list(users))
                answer = choice(list(answers))
                if (author.id, answer.id) not in answer_likes:
                    answer_likes.add((author.id, answer.id))
                    answer_like = AnswerLike(author=author, answer=answer)
                    answer_like.save()
                    count += 1
                    pbar.update(1)

    def add_arguments(self, parser):
        parser.add_argument('ratio', type=int)

    def handle(self, *args, **options):
        print('start...')
        ratio = options['ratio']
        faker = Faker()
        try:
            with transaction.atomic():
                users = self.create_users(ratio, faker)
                tags = self.create_tags(ratio, faker)
                questions = self.create_questions(ratio * 10, users, tags, faker)
                answers = self.create_answers(ratio * 100, questions, users, faker)
                self.create_likes(ratio * 200, questions, answers, users)
                print('end successfully')
        except Exception as e:
            print(e)
