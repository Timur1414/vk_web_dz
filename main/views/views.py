from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.core.exceptions import PermissionDenied
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, DetailView, CreateView, UpdateView
from django_registration.backends.one_step.views import RegistrationView
from main.forms import AskForm, SettingsForm, CreateAnswerForm, RegistrationForm
from main.models import Profile, Question, Answer, QuestionLike
from main.paginators import paginate
from main.views.base import create_base_context, create_context, get_paginated_nav_context


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
        next_url = self.request.POST.get('continue', '')
        if next_url:
            return next_url
        return reverse_lazy('index')


def logout_view(request: WSGIRequest) -> HttpResponseRedirect:
    """
    Logout the user and redirect to the referer page.
    """
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(create_base_context())
        return context

    def register(self, form):
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
        return new_user


class IndexPage(TemplateView):
    """
    View for displaying the home page with a list of questions.
    Shows the most recent questions by default, paginated.
    """
    template_name = 'index/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(create_context(self.request))
        questions = paginate(Question.new.get_queryset(), self.request)
        context.update(get_paginated_nav_context(questions))
        return context


class HotQuestionsPage(TemplateView):
    """
    View for displaying the most popular questions.
    Shows questions ordered by their rating (most popular first), paginated.
    """
    template_name = 'index/hot_questions.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(create_context(self.request))
        questions = paginate(Question.popular.get_queryset(), self.request)
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
        self.object = get_object_or_404(Question, id=self.kwargs['id'])
        return self.object


    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context.update(create_context(self.request))
        question = self.get_object()
        context['is_author'] = self.request.user == question.author
        context['is_question_liked'] = QuestionLike.is_liked(question, self.request.user)
        context['answers'] = Answer.get_answers_by_question(question)
        initial = {
            'question': question,
            'author': self.request.user,
        }
        context['form'] = CreateAnswerForm(initial=initial)
        return context

    def post(self, request, *args, **kwargs):
        question = self.get_object()
        context = self.get_context_data(**kwargs)
        form = CreateAnswerForm(request.POST)
        if form.is_valid():
            if form.cleaned_data['author'] != request.user:
                raise PermissionDenied()
            form.save()
            return redirect('question', id=question.id)
        else:
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

    def get_initial(self):
        initial = super().get_initial()
        initial['author'] = self.request.user
        return initial

    def form_valid(self, form):
        if form.instance.author != self.request.user:
            raise PermissionDenied()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(create_context(self.request))
        return context


class TagePage(TemplateView):
    """
    View for displaying questions filtered by a specific tag.
    Shows all questions that have been tagged with the specified tag, paginated.
    """
    template_name = 'tag/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(create_context(self.request))
        tag = self.kwargs['tag']
        context['tag'] = tag
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
        return reverse_lazy('index')

    def get_initial(self):
        initial = super().get_initial()
        initial['username'] = self.request.user.username
        initial['email'] = self.request.user.email
        initial['nickname'] = self.request.user.profile.nickname
        initial['avatar'] = self.request.user.profile.avatar
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(create_context(self.request))
        return context
