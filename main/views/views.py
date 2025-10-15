from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.core.exceptions import PermissionDenied
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django_registration.backends.one_step.views import RegistrationView
from main.forms import AskForm, SettingsForm, CreateAnswerForm
from main.models import Profile, Question, Answer, QuestionLike
from main.paginators import paginate
from main.views.base import create_base_context, create_context, get_paginated_nav_context


class LoginPage(LoginView):
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
    logout(request)
    referer = request.headers['referer']
    return redirect(referer)


class RegistrationPage(RegistrationView):
    template_name = 'django_registration/registration_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(create_base_context())
        return context

    def register(self, form):
        new_user = super().register(form)
        new_profile = Profile.get_profile_of_user(new_user)
        nickname = self.request.POST.get('nickname', 'user')
        new_profile.update(nickname=nickname)
        return new_user


def index_page(request: WSGIRequest) -> HttpResponse:
    context = create_context(request)
    questions = paginate(Question.new.get_queryset(), request)
    context.update(get_paginated_nav_context(questions))
    return render(request, 'index/index.html', context)


def hot_questions_page(request: WSGIRequest) -> HttpResponse:
    context = create_context(request)
    questions = paginate(Question.popular.get_queryset(), request)
    context.update(get_paginated_nav_context(questions))
    return render(request, 'index/hot_questions.html', context)

def question_page(request: WSGIRequest, id: int) -> HttpResponse:
    context = create_context(request)
    question = get_object_or_404(Question, id=id)
    context['is_author'] = request.user == question.author
    context['question'] = question
    context['is_question_liked'] = QuestionLike.is_liked(question, request.user)
    context['answers'] = Answer.get_answers_by_question(question)
    initial = {
        'question': question,
        'author': request.user,
    }
    context['form'] = CreateAnswerForm(initial=initial)
    if request.method == 'POST':
        form = CreateAnswerForm(request.POST)
        if form.is_valid():
            if form.cleaned_data['author'] != request.user:
                raise PermissionDenied()
            form.save()
            return redirect('question', id=question.id)
        else:
            context['form'] = form
    return render(request, 'question/question.html', context)


@login_required()
def ask_page(request: WSGIRequest) -> HttpResponse:
    context = create_context(request)
    context['form'] = AskForm(initial={'author': request.user})
    if request.method == 'POST':
        form = AskForm(request.POST)
        if form.is_valid():
            if form.cleaned_data['author'] != request.user:
                raise PermissionDenied()
            form.save()
            return redirect('index')
        else:
            context['form'] = form
    return render(request, 'question/ask.html', context)


def tag_page(request: WSGIRequest, tag: str) -> HttpResponse:
    context = create_context(request)
    context['tag'] = tag
    questions = paginate(Question.get_questions_by_tag(tag), request)
    context.update(get_paginated_nav_context(questions))
    return render(request, 'tag/index.html', context)


@login_required()
def settings_page(request: WSGIRequest) -> HttpResponse:
    context = create_context(request)
    initial = {
        'username': request.user.username,
        'email': request.user.email,
        'nickname': request.user.profile.nickname,
        'avatar': request.user.profile.avatar,
    }
    context['form'] = SettingsForm(initial=initial, instance=request.user)
    if request.method == 'POST':
        form = SettingsForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('index')
        else:
            context['form'] = form
    return render(request, 'profile/settings.html', context)
