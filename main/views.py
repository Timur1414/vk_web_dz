from typing import Any
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.core.exceptions import PermissionDenied
from django.core.handlers.wsgi import WSGIRequest
from django.core.paginator import EmptyPage
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django_registration.backends.one_step.views import RegistrationView
from main.forms import AskForm, SettingsForm, CreateAnswerForm
from main.models import Profile, Question, Answer, Tag, QuestionLike, AnswerLike
from main.paginators import paginate


def create_base_context() -> dict[str, Any]:
    context = {
        'popular_profiles': Profile.popular.get_popular(),
        'popular_tags': Tag.popular.get_popular(),
    }
    return context


def create_context(request) -> dict[str, Any]:
    context = create_base_context()
    user = request.user
    profile = Profile.get_profile_of_user(user)
    context.update({
        'user': user,
        'profile': profile,
    })
    return context


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
    context['questions'] = questions.object_list
    context['page'] = questions.number
    try:
        context['prev'] = questions.previous_page_number()
    except EmptyPage:
        context['prev'] = None
    try:
        context['next'] = questions.next_page_number()
    except EmptyPage:
        context['next'] = None
    return render(request, 'index/index.html', context)


def logout_view(request: WSGIRequest) -> HttpResponseRedirect:
    logout(request)
    referer = request.headers['referer']
    return redirect(referer)


def hot_questions_page(request: WSGIRequest) -> HttpResponse:
    context = create_context(request)
    questions = paginate(Question.popular.get_queryset(), request)
    context['questions'] = questions.object_list
    context['page'] = questions.number
    try:
        context['prev'] = questions.previous_page_number()
    except EmptyPage:
        context['prev'] = None
    try:
        context['next'] = questions.next_page_number()
    except EmptyPage:
        context['next'] = None
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
            form.save()
            return redirect('question', id=question.id)
        else:
            context['form'] = form
    return render(request, 'question/question.html', context)


@login_required()
def ask_page(request: WSGIRequest) -> HttpResponse:
    context = create_context(request)
    context['form'] = AskForm(initial={'author': request.user.id})
    if request.method == 'POST':
        form = AskForm(request.POST)
        if form.is_valid():
            if form.cleaned_data['author'] != request.user.id:
                raise PermissionDenied()
            title = form.cleaned_data['title']
            text = form.cleaned_data['text']
            question = Question.create(title=title, text=text, author=request.user)
            tags_text = form.cleaned_data['tags'].strip()
            while '  ' in tags_text:
                tags_text = tags_text.replace('  ', ' ')
            tags_text = tags_text.replace(', ', ',')
            tags_words = tags_text.split(',')
            for tag_text in tags_words:
                tag = Tag.get_or_create(tag_text)
                question.add_tag(tag)
            return redirect('index')
        else:
            context['form'] = form
    return render(request, 'question/ask.html', context)


def tag_page(request: WSGIRequest, tag: str) -> HttpResponse:
    context = create_context(request)
    context['tag'] = tag
    questions = paginate(Question.get_questions_by_tag(tag), request)
    context['questions'] = questions.object_list
    context['page'] = questions.number
    try:
        context['prev'] = questions.previous_page_number()
    except EmptyPage:
        context['prev'] = None
    try:
        context['next'] = questions.next_page_number()
    except EmptyPage:
        context['next'] = None
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


def search_questions(request: WSGIRequest) -> JsonResponse:
    text = request.GET.get('text', '')
    questions = Question.find_by_text(text)
    html = ''
    for question in questions:
        html += render_to_string('index/search_item.html', {'question': question})
    return JsonResponse({
        'html': html,
    }, status=200)


def question_like(request: WSGIRequest) -> JsonResponse:
    user = request.user
    question_id = request.GET.get('question_id')
    question = None
    if not user.is_authenticated:
        return JsonResponse({}, status=401)
    try:
        question_id = int(question_id)
        question = Question.get_question_by_id(question_id)
        if question is None:
            raise ValueError()
    except ValueError:
        return JsonResponse({}, status=404)
    QuestionLike.like(question, user)
    return JsonResponse({},  status=200)


def answer_like(request: WSGIRequest) -> JsonResponse:
    user = request.user
    answer_id = request.GET.get('answer_id')
    answer = None
    if not user.is_authenticated:
        return JsonResponse({}, status=401)
    try:
        answer_id = int(answer_id)
        answer = Answer.get_answer_by_id(answer_id)
        if answer is None:
            raise ValueError()
    except ValueError:
        return JsonResponse({}, status=404)
    AnswerLike.like(answer, user)
    return JsonResponse({}, status=200)


def answer_check(request: WSGIRequest) -> JsonResponse:
    user = request.user
    answer_id = request.GET.get('answer_id')
    answer = None
    if not user.is_authenticated:
        return JsonResponse({}, status=401)
    try:
        answer_id = int(answer_id)
        answer = Answer.get_answer_by_id(answer_id)
        if answer is None:
            raise ValueError()
    except ValueError:
        return JsonResponse({}, status=404)
    if user != answer.question.author:
        return JsonResponse({}, status=403)
    answer.change_correct()
    return JsonResponse({}, status=200)
