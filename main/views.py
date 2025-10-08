from django.shortcuts import render


def index_page(request):
    context = {
        'title': 'AskPupkin',
    }
    return render(request, 'index/index.html', context)


def question_page(request):
    context = {
        'title': 'Question',
    }
    return render(request, 'question/question.html', context)


def ask_page(request):
    context = {
        'title': 'Ask',
    }
    return render(request, 'question/ask.html', context)


def tag_page(request):
    context = {
        'title': 'Tag',
    }
    return render(request, 'tag/index.html', context)


def settings_page(request):
    context = {
        'title': 'Settings',
    }
    return render(request, 'profile/settings.html', context)
