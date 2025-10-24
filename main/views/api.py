import json
import requests
from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string
from main.models import Question, QuestionLike, AnswerLike, Answer
from main.views.base import check_received_question, check_received_answer
from vk_dz import settings
from vk_dz.centrifugo import generate_centrifugo_token


def search_questions(request: WSGIRequest) -> JsonResponse:
    """
    Returns a JSON response containing HTML of search results.

    Queries the database for questions containing the given text
    and renders each result as a search item template.

    Args:
        request (WSGIRequest): The request containing the search text.

    Returns:
        JsonResponse: A response containing the rendered HTML of search results.
    """
    text = request.GET.get('text', '')
    questions = Question.find_by_text(text)
    html = ''
    for question in questions:
        html += render_to_string('index/search_item.html', {'question': question})
    return JsonResponse({
        'html': html,
    }, status=200)


def question_like(request: WSGIRequest) -> JsonResponse:
    """
    Returns a JSON response containing no content.

    Queries the database for the given question and increments/decrements its rating
    depending on whether the user has liked the question before.

    Args:
        request (WSGIRequest): The request containing the question_id.
    """
    user = request.user
    question_id = request.GET.get('question_id')
    if not user.is_authenticated:
        return JsonResponse({}, status=401)
    question = check_received_question(question_id)
    if question is None:
        return JsonResponse({}, status=404)
    QuestionLike.like(question, user)
    return JsonResponse({}, status=200)


def answer_like(request: WSGIRequest) -> JsonResponse:
    """
    Returns a JSON response containing no content.

    Queries the database for the given answer and increments/decrements its rating
    depending on whether the user has liked the answer before.

    Args:
        request (WSGIRequest): The request containing the answer_id.
    """
    user = request.user
    answer_id = request.GET.get('answer_id')
    if not user.is_authenticated:
        return JsonResponse({}, status=401)
    answer = check_received_answer(answer_id)
    if answer is None:
        return JsonResponse({}, status=404)
    AnswerLike.like(answer, user)
    return JsonResponse({}, status=200)


def answer_check(request: WSGIRequest) -> JsonResponse:
    """
    Make an answer as correct/incorrect.

    Args:
        request (WSGIRequest): The request containing the answer_id.
    """
    user = request.user
    answer_id = request.GET.get('answer_id')
    if not user.is_authenticated:
        return JsonResponse({}, status=401)
    answer = check_received_answer(answer_id)
    if answer is None:
        return JsonResponse({}, status=404)
    if user != answer.question.author:
        return JsonResponse({}, status=403)
    answer.change_correct()
    return JsonResponse({}, status=200)


def publish_answer(request: WSGIRequest, answer: Answer, is_author: bool):
    context = {
        'answer': answer,
        'request': request,
        'is_author': is_author,
    }
    data = {
        'method': 'publish',
        'params': {
            'channel': str(answer.question.id),
            'data': {
                'text': answer.text,
                'html': render_to_string('question/answer.html', context)
            },
        }
    }
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'apikey {settings.CENTRIFUGO_API_KEY}'
    }
    url = f'{settings.CENTRIFUGO_URL}/api'
    requests.post(url, headers=headers, data=json.dumps(data))

@login_required
def centrifugo_token(request):
    token = generate_centrifugo_token(request.user.id)
    return JsonResponse({'token': token}, status=200)
