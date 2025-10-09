from typing import Any
from django.contrib.auth.decorators import login_required
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.template.loader import render_to_string
from main.models import Profile, Question, Answer, Tag


def create_base_context(request) -> dict[str, Any]:
    user = request.user
    profile = Profile.get_profile_of_user(user)
    context = {
        'user': user,
        'profile': profile,
        'popular_profiles': Profile.get_popular(),
        'popular_tags': Tag.get_popular(),
    }
    return context


def render_questions(questions: list, request: WSGIRequest) -> str:
    if not questions:
        return '<p>nothing...</p>'
    html = ''
    for question in questions:
        html += render_to_string(request=request, template_name='question/card.html', context={'question': question})
    return html


def index_page(request: WSGIRequest) -> HttpResponse:
    context = create_base_context(request)
    context['questions'] = Question.new.get_new()
    return render(request, 'index/index.html', context)


def logout_view(request: WSGIRequest) -> HttpResponseRedirect:
    logout(request)
    return redirect('index')


def hot_questions_page(request: WSGIRequest) -> HttpResponse:
    context = create_base_context(request)
    context['questions'] = Question.popular.get_popular()
    return render(request, 'index/hot_questions.html', context)


def question_page(request: WSGIRequest, id: int) -> HttpResponse:
    context = create_base_context(request)
    question = get_object_or_404(Question, id=id)
    context['question'] = question
    context['answers'] = Answer.get_answers_by_question(question)
    return render(request, 'question/question.html', context)


@login_required()
def ask_page(request: WSGIRequest) -> HttpResponse:
    context = create_base_context(request)
    return render(request, 'question/ask.html', context)


def tag_page(request: WSGIRequest, tag: str) -> HttpResponse:
    context = create_base_context(request)
    context['tag'] = tag
    context['questions'] = Question.get_questions_by_tag(tag)
    return render(request, 'tag/index.html', context)


@login_required()
def settings_page(request: WSGIRequest) -> HttpResponse:
    context = create_base_context(request)
    if request.method == 'POST':
        pass
    return render(request, 'profile/settings.html', context)
