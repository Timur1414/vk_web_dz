from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.template.loader import render_to_string


def render_questions(questions: list, request: WSGIRequest) -> str:
    if not questions:
        return '<p>nothing...</p>'
    html = ''
    for question in questions:
        html += render_to_string(request=request, template_name='question/card.html', context={'question': question})
    return html

def index_page(request: WSGIRequest) -> HttpResponse:
    context = {
        'title': 'AskPupkin',
    }
    return render(request, 'index/index.html', context)


def logout_view(request: WSGIRequest) -> HttpResponseRedirect:
    logout(request)
    return redirect('index')


def hot_questions_page(request: WSGIRequest) -> HttpResponse:
    context = {
        'title': 'Hot',
    }
    return render(request, 'question/hot_questions.html', context)


def question_page(request: WSGIRequest) -> HttpResponse:
    context = {
        'title': 'Question',
    }
    return render(request, 'question/question.html', context)


def ask_page(request: WSGIRequest) -> HttpResponse:
    context = {
        'title': 'Ask',
    }
    return render(request, 'question/ask.html', context)


def tag_page(request: WSGIRequest) -> HttpResponse:
    context = {
        'title': 'Tag',
    }
    return render(request, 'tag/index.html', context)


def settings_page(request: WSGIRequest) -> HttpResponse:
    context = {
        'title': 'Settings',
    }
    return render(request, 'profile/settings.html', context)
