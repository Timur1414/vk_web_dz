from django.contrib.auth.models import User
from django.test import TestCase, Client
from main.models import Question, Tag, Answer


class IndexPageTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='username',
            email='abc@example.com',
            password='password',
        )
        self.user.profile.nickname = 'nickname'
        self.user.profile.save()

    def test_status_code(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_templates(self):
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'index/index.html')

    def test_content(self):
        response = self.client.get('/')
        self.assertContains(response, 'New Questions')
        self.assertContains(response, 'Hot Questions')
        self.assertContains(response, 'Темиров Тимур')
        self.assertInHTML('<p class="fs-3 d-inline-flex">New Questions</p>', response.content.decode())

    def test_anonymous_user(self):
        response = self.client.get('/')
        self.assertNotContains(response, 'log out')
        self.assertContains(response, 'log in')

    def test_authenticated_user(self):
        self.client.force_login(self.user)
        response = self.client.get('/')
        self.assertContains(response, 'log out')
        self.assertContains(response, self.user.profile.nickname)
        self.assertNotContains(response, 'log in')


class HotPageTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='username',
            email='abc@example.com',
            password='password',
        )
        self.user.profile.nickname = 'nickname'
        self.user.profile.save()

    def test_status_code(self):
        response = self.client.get('/hot/')
        self.assertEqual(response.status_code, 200)

    def test_templates(self):
        response = self.client.get('/hot/')
        self.assertTemplateUsed(response, 'index/hot_questions.html')

    def test_content(self):
        response = self.client.get('/hot/')
        self.assertContains(response, 'New Questions')
        self.assertContains(response, 'Hot Questions')
        self.assertInHTML('<p class="fs-3 mx-2 d-inline-flex">Hot Questions</p>', response.content.decode())
        self.assertInHTML('<a class="fs-4" href="/">New Questions</a>', response.content.decode())

    def test_anonymous_user(self):
        response = self.client.get('/hot/')
        self.assertNotContains(response, 'log out')
        self.assertContains(response, 'log in')

    def test_authenticated_user(self):
        self.client.force_login(self.user)
        response = self.client.get('/hot/')
        self.assertContains(response, 'log out')
        self.assertContains(response, self.user.profile.nickname)
        self.assertNotContains(response, 'log in')


class QuestionPageTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='username',
            email='abc@example.com',
            password='password',
        )
        self.user.profile.nickname = 'nickname'
        self.user.profile.save()
        self.question = Question.create(
            title='title',
            text='text',
            author=self.user,
        )

    def test_status_code(self):
        response = self.client.get(f'/question/{self.question.pk}/')
        self.assertEqual(response.status_code, 200)

    def test_templates(self):
        response = self.client.get(f'/question/{self.question.pk}/')
        self.assertTemplateUsed(response, 'question/question.html')

    def test_content(self):
        response = self.client.get(f'/question/{self.question.pk}/')
        self.assertContains(response, 'title')
        self.assertContains(response, 'text')
        self.assertInHTML('<p class="fs-3">title</p>', response.content.decode())
        self.assertInHTML('<p>text</p>', response.content.decode())

    def test_anonymous_user(self):
        response = self.client.get(f'/question/{self.question.pk}/')
        self.assertNotContains(response, 'log out')
        self.assertContains(response, 'log in')
        self.assertNotContains(response, 'button')

    def test_authenticated_user(self):
        self.client.force_login(self.user)
        response = self.client.get(f'/question/{self.question.pk}/')
        self.assertContains(response, 'log out')
        self.assertContains(response, self.user.profile.nickname)
        self.assertNotContains(response, 'log in')
        self.assertContains(response, 'button')
        self.assertContains(response, '👍: 0')

    def test_wrong_id(self):
        response = self.client.get('/question/2/')
        self.assertEqual(response.status_code, 404)
        response = self.client.get('/question/0/')
        self.assertEqual(response.status_code, 404)
        response = self.client.get('/question/-1/')
        self.assertEqual(response.status_code, 404)
        response = self.client.get('/question/abc/')
        self.assertEqual(response.status_code, 404)
        response = self.client.get('/question//')
        self.assertEqual(response.status_code, 404)

    def test_add_valid_answer(self):
        self.client.force_login(self.user)
        data = {
            'text': 'text',
        }
        response = self.client.post(f'/question/{self.question.pk}/', data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Answer.objects.count(), 1)
        answer = Answer.objects.get(id=1)
        self.question.refresh_from_db()
        self.assertEqual(answer.text, 'text')
        self.assertEqual(self.question.count_answers, 1)

    def test_add_invalid_answer(self):
        self.client.force_login(self.user)
        data = {
            'text': '',
        }
        response = self.client.post(f'/question/{self.question.pk}/', data)
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.question.refresh_from_db()
        self.assertNotEqual(form.errors, {})
        self.assertEqual(Answer.objects.count(), 0)
        self.assertEqual(self.question.count_answers, 0)

    def test_add_anonymous_answer(self):
        data = {
            'text': 'text',
        }
        response = self.client.post(f'/question/{self.question.pk}/', data)
        self.assertEqual(response.status_code, 403)
        self.question.refresh_from_db()
        self.assertEqual(Answer.objects.count(), 0)
        self.assertEqual(self.question.count_answers, 0)


class AskPageTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='username',
            email='abc@example.com',
            password='password',
        )
        self.user.profile.nickname = 'nickname'
        self.user.profile.save()

    def test_status_code(self):
        self.client.force_login(self.user)
        response = self.client.get('/ask/')
        self.assertEqual(response.status_code, 200)

    def test_templates(self):
        self.client.force_login(self.user)
        response = self.client.get('/ask/')
        self.assertTemplateUsed(response, 'question/ask.html')

    def test_content(self):
        self.client.force_login(self.user)
        response = self.client.get('/ask/')
        self.assertContains(response, 'New Question')
        self.assertContains(response, '<div class="ck-editor-container">')
        self.assertInHTML(
            '<textarea  name="text" class="django_ckeditor_5" required id="id_text">',
            response.content.decode())

    def test_anonymous_user(self):
        response = self.client.get('/ask/')
        self.assertEqual(response.status_code, 302)

    def test_authenticated_user(self):
        self.client.force_login(self.user)
        response = self.client.get('/ask/')
        self.assertContains(response, 'log out')
        self.assertContains(response, self.user.profile.nickname)
        self.assertNotContains(response, 'log in')

    def test_valid_data(self):
        self.client.force_login(self.user)
        data = {
            'title': 'title',
            'text': 'text',
            'tags': 'test'
        }
        response = self.client.post('/ask/', data=data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Question.objects.count(), 1)
        question = Question.objects.get(id=1)
        self.assertEqual(question.title, 'title')
        self.assertEqual(question.text, 'text')
        self.assertEqual(question.author, self.user)
        self.assertEqual(question.tags.count(), 1)
        tag = Tag.objects.get(id=1)
        self.assertEqual(tag, question.tags.first())

    def test_invalid_data(self):
        self.client.force_login(self.user)
        data = {
            'title': '',
            'text': 'text',
            'tags': 'test'
        }
        response = self.client.post('/ask/', data=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Question.objects.count(), 0)
        form = response.context['form']
        self.assertNotEqual(form.errors, {})


class TagPageTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='username',
            email='abc@example.com',
            password='password',
        )
        self.user.profile.nickname = 'nickname'
        self.user.profile.save()

    def test_status_code(self):
        response = self.client.get('/tag/abc/')
        self.assertEqual(response.status_code, 200)

    def test_templates(self):
        response = self.client.get('/tag/abc/')
        self.assertTemplateUsed(response, 'tag/index.html')

    def test_content(self):
        response = self.client.get('/tag/abc/')
        self.assertContains(response, 'abc')
        self.assertInHTML('<span class="fw-semibold">abc</span>', response.content.decode())

    def test_anonymous_user(self):
        response = self.client.get('/tag/abc/')
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'log out')
        self.assertContains(response, 'log in')
        self.assertNotContains(response, 'button')

    def test_authenticated_user(self):
        self.client.force_login(self.user)
        response = self.client.get('/tag/abc/')
        self.assertContains(response, 'log out')
        self.assertContains(response, self.user.profile.nickname)
        self.assertNotContains(response, 'log in')

    def test_valid_tag(self):
        question = Question.create(
            title='title',
            text='text',
            author=self.user
        )
        tag = Tag.get_or_create('test')
        question.add_tag(tag)
        response = self.client.get('/tag/test/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, question.title)

    def test_invalid_tag(self):
        response = self.client.get('/tag/')
        self.assertEqual(response.status_code, 404)
        response = self.client.get('/tag//')
        self.assertEqual(response.status_code, 404)


class SettingsPageTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='username',
            email='abc@example.com',
            password='password',
        )
        self.user.profile.nickname = 'nickname'
        self.user.profile.save()

    def test_status_code(self):
        self.client.force_login(self.user)
        response = self.client.get('/profile/edit/')
        self.assertEqual(response.status_code, 200)

    def test_templates(self):
        self.client.force_login(self.user)
        response = self.client.get('/profile/edit/')
        self.assertTemplateUsed(response, 'profile/settings.html')

    def test_content(self):
        self.client.force_login(self.user)
        response = self.client.get('/profile/edit/')
        self.assertContains(response, self.user.profile.nickname)
        self.assertInHTML(f'<span>{self.user.profile.nickname}</span>', response.content.decode())

    def test_anonymous_user(self):
        response = self.client.get('/profile/edit/')
        self.assertEqual(response.status_code, 302)

    def test_authenticated_user(self):
        self.client.force_login(self.user)
        response = self.client.get('/profile/edit/')
        self.assertContains(response, 'log out')
        self.assertContains(response, self.user.profile.nickname)
        self.assertContains(response, self.user.username)
        self.assertContains(response, self.user.email)
        self.assertNotContains(response, 'log in')

    def test_post_request(self):
        self.client.force_login(self.user)
        data = {
            'username': self.user.username,
            'email': 'abc@example.ru',
            'nickname': 'new_nickname',
            'avatar': self.user.profile.avatar,
        }
        response = self.client.post('/profile/edit/', data=data)
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.email, 'abc@example.ru')
        self.assertEqual(self.user.profile.nickname, 'new_nickname')


class ProfilePageTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='username',
            email='abc@example.com',
            password='password',
        )
        self.user.profile.nickname = 'nickname'
        self.user.profile.save()

    def test_status_code(self):
        response = self.client.get('/profile/1/')
        self.assertEqual(response.status_code, 200)

    def test_templates(self):
        response = self.client.get('/profile/1/')
        self.assertTemplateUsed(response, 'profile/index.html')

    def test_content(self):
        response = self.client.get('/profile/1/')
        self.assertContains(response, self.user.profile.nickname)
        self.assertContains(response, 'Rating: 0')
        self.assertInHTML(f'<p class="fs-2">{self.user.profile.nickname}</p>', response.content.decode())

    def test_anonymous_user(self):
        response = self.client.get('/profile/1/')
        self.assertNotContains(response, 'log out')
        self.assertContains(response, 'log in')

    def test_authenticated_user(self):
        self.client.force_login(self.user)
        response = self.client.get('/profile/1/')
        self.assertContains(response, 'log out')
        self.assertContains(response, self.user.profile.nickname)
        self.assertNotContains(response, 'log in')
