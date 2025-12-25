import logging
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.core.exceptions import PermissionDenied
from django.core.handlers.wsgi import WSGIRequest
from django.db import transaction
from django.db.models import Exists, OuterRef, Value
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, DetailView, CreateView, UpdateView
from django_registration.backends.one_step.views import RegistrationView
from main.forms import AskForm, SettingsForm, CreateAnswerForm, RegistrationForm
from main.models import Profile, Question, Answer, QuestionLike, Tag, AnswerLike
from main.paginators import paginate
from main.views.api import publish_answer
from main.views.base import create_base_context, create_context, get_paginated_nav_context


logger = logging.getLogger('default')


class LoginPage(LoginView):
    """
    View for handling user login.
    Displays the login form and handles authentication. After successful login,
    redirects to the 'next' URL if provided, otherwise to the home page.
    """
    template_name = 'registration/login.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(create_base_context())
        return context

    def get_success_url(self):
        logger.info('%s logged in', self.request.user)
        next_url = self.request.POST.get('next', '')
        if next_url:
            return next_url
        return reverse_lazy('index')


class PasswordChangePage(PasswordChangeView):
    template_name = 'registration/password_change_form.html'
    success_url = reverse_lazy('index')

    def form_valid(self, form):
        messages.add_message(self.request, messages.INFO, 'Password changed successfully')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(create_context(self.request))
        return context

def logout_view(request: WSGIRequest) -> HttpResponseRedirect:
    """
    Logout the user and redirect to the referer page.
    """
    logger.info('%s logged out', request.user)
    logout(request)
    referer = request.headers['referer']
    return redirect(referer)


class RegistrationPage(RegistrationView):
    """
    View for handling user registration.
    Displays the registration form and creates a new user account
    along with their profile when the form is submitted.
    """
    template_name = 'django_registration/registration_form.html'
    form_class = RegistrationForm
    success_url = reverse_lazy('index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(create_base_context())
        return context

    def register(self, form):
        with transaction.atomic():
            new_user = super().register(form)
            new_profile = Profile.get_profile_of_user(new_user)
            nickname = form.cleaned_data['nickname']
            email = form.cleaned_data['email']
            avatar = None
            if 'avatar' in form.cleaned_data:
                avatar = form.cleaned_data['avatar']
            new_user.email = email
            new_user.save()
            new_profile.update(nickname=nickname, avatar=avatar)
            logger.info('%s registered', new_user)
            return new_user


class ClosedRegistrationPage(TemplateView):
    template_name = 'django_registration/registration_closed.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(create_base_context())
        return context


class IndexPage(TemplateView):
    """
    View for displaying the home page with a list of questions.
    Shows the most recent questions by default, paginated.
    """
    template_name = 'index/index.html'

    def get_context_data(self, **kwargs):
        logger.info('%s view main page', self.request.user)
        context = super().get_context_data(**kwargs)
        context.update(create_context(self.request))
        questions = paginate(Question.new.get_queryset()
                             .select_related('author', 'author__profile')
                             .prefetch_related('tags'), self.request)
        context.update(get_paginated_nav_context(questions))
        return context


class HotQuestionsPage(TemplateView):
    """
    View for displaying the most popular questions.
    Shows questions ordered by their rating (most popular first), paginated.
    """
    template_name = 'index/hot_questions.html'

    def get_context_data(self, **kwargs):
        logger.info('%s view hot page', self.request.user)
        context = super().get_context_data(**kwargs)
        context.update(create_context(self.request))
        questions = paginate(Question.popular.get_queryset()
                             .select_related('author', 'author__profile')
                             .prefetch_related('tags'), self.request)
        context.update(get_paginated_nav_context(questions))
        return context


class QuestionPage(DetailView):
    """
    View for displaying a single question and its answers.
    Shows the question details, all its answers, and provides a form
    for submitting new answers. Also handles answer submissions.
    """
    template_name = 'question/question.html'
    model = Question
    context_object_name = 'question'

    def get_object(self, queryset = ...):
        self.object = (Question.objects.filter(id=self.kwargs['id'])
                       .select_related('author', 'author__profile')
                       .prefetch_related('tags', 'questionlike_set').first())
        if self.object is None:
            raise Http404()
        return self.object

    def get_context_data(self, **kwargs):
        logger.info('%s view question (id=%s) page', self.request.user, self.kwargs['id'])
        context = super().get_context_data()
        context.update(create_context(self.request))
        question = self.object
        context['is_author'] = self.request.user == question.author
        context['is_question_liked'] = QuestionLike.is_liked(question, self.request.user)
        if self.request.user.is_authenticated:
            context['answers'] = Answer.get_answers_by_question(question).annotate(is_liked=Exists(
                AnswerLike.objects.filter(answer=OuterRef('pk'), author=self.request.user)
            ))
        else:
            context['answers'] = Answer.get_answers_by_question(question).annotate(is_liked=Value(False))
        context['form'] = CreateAnswerForm()
        return context

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise PermissionDenied()
        question = self.get_object()
        context = self.get_context_data(**kwargs)
        form = CreateAnswerForm(request.POST)
        if form.is_valid():
            form.instance.author = request.user
            form.instance.question = question
            answer = form.save()
            is_author = request.user == question.author
            publish_answer(request, answer, is_author)
            logger.info('%s created answer (id=%s) to question (id=%s)', self.request.user, answer.id, question.id)
            return redirect('question', id=question.id)
        else:
            logger.warning('%s failed validation of answer to question (id=%s)', self.request.user, question.id)
            context['form'] = form
        return render(request, QuestionPage.template_name, context)


class AskPage(LoginRequiredMixin, CreateView):
    """
    View for asking a new question.
    Displays a form for submitting a new question and handles the form submission.
    Only accessible to authenticated users.
    """
    template_name = 'question/ask.html'
    model = Question
    form_class = AskForm

    def get_success_url(self):
        return reverse_lazy('index')

    def form_valid(self, form):
        form.instance.author = self.request.user
        logger.info('%s ask new question', self.request.user)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        logger.info('%s view ask page', self.request.user)
        context = super().get_context_data(**kwargs)
        context.update(create_context(self.request))
        return context


class TagPage(TemplateView):
    """
    View for displaying questions filtered by a specific tag.
    Shows all questions that have been tagged with the specified tag, paginated.
    """
    template_name = 'tag/index.html'

    def get_context_data(self, **kwargs):
        logger.info('%s view tag page', self.request.user)
        context = super().get_context_data(**kwargs)
        context.update(create_context(self.request))
        tag = self.kwargs['tag']
        context['tag_text'] = tag
        context['tag'] = Tag.get(tag)
        questions = paginate(Question.get_questions_by_tag(tag), self.request)
        context.update(get_paginated_nav_context(questions))
        return context


class SettingsPage(LoginRequiredMixin, UpdateView):
    """
    View for user profile settings.
    Allows users to update their account information including
    username, email, nickname, and avatar. Only accessible to the account owner.
    """
    template_name = 'profile/settings.html'
    model = User
    form_class = SettingsForm

    def get_object(self, queryset = ...):
        self.object = self.request.user
        return self.object

    def get_success_url(self):
        logger.info('%s updated settings', self.request.user)
        return reverse_lazy('index')

    def get_initial(self):
        initial = super().get_initial()
        initial['username'] = self.request.user.username
        initial['email'] = self.request.user.email
        initial['nickname'] = self.request.user.profile.nickname
        initial['avatar'] = self.request.user.profile.avatar
        return initial

    def get_context_data(self, **kwargs):
        logger.info('%s view settings page', self.request.user)
        context = super().get_context_data(**kwargs)
        context.update(create_context(self.request))
        return context


class ProfilePage(DetailView):
    """
    View for user profile.
    Displays the profile of a specific user, including their questions and answers.
    """
    template_name = 'profile/index.html'
    model = Profile
    context_object_name = 'object'

    def get_object(self, queryset = ...):
        self.object = get_object_or_404(Profile, user=self.kwargs['id'])
        return self.object

    def get_context_data(self, **kwargs):
        logger.info('%s view profile page', self.request.user)
        context = super().get_context_data(**kwargs)
        context.update(create_context(self.request))
        context['is_author'] = self.request.user == self.object.user
        context['questions'] = Question.get_questions_by_author(self.object.user)
        return context
