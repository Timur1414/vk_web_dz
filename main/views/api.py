import json
import logging
import sys
import requests
from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from main.models import Question, QuestionLike, AnswerLike, Answer
from main.views.base import check_received_question, check_received_answer
from vk_dz import settings
from django.http import HttpResponse
from vk_dz.centrifugo import generate_centrifugo_token

logger = logging.getLogger('default')


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
        logger.error('anonymous user tried to like')
        return JsonResponse({'message': 'Log in to like.'}, status=401)
    question = check_received_question(question_id)
    if question is None:
        logger.error('%s tried to like question (id=%s) which does not exist', request.user.username, question_id)
        return JsonResponse({'message': 'This question do not exist.'}, status=404)
    QuestionLike.like(question, user)
    question.refresh_from_db()
    return JsonResponse({'count': question.rating, 'message': 'ok.'}, status=200)


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
        logger.error('anonymous user tried to like')
        return JsonResponse({'message': 'Log in to like.'}, status=401)
    answer = check_received_answer(answer_id)
    if answer is None:
        logger.error('%s tried to like answer (id=%s) which does not exist', request.user.username, answer_id)
        return JsonResponse({'message': 'This answer do not exist.'}, status=404)
    AnswerLike.like(answer, user)
    answer.refresh_from_db()
    return JsonResponse({'count': answer.rating, 'message': 'ok.'}, status=200)


def mark_answer(request: WSGIRequest) -> JsonResponse:
    """
    Make an answer as correct/incorrect.

    Args:
        request (WSGIRequest): The request containing the answer_id.
    """
    user = request.user
    answer_id = request.GET.get('answer_id')
    if not user.is_authenticated:
        logger.error('anonymous user tried to make answer correct/incorrect')
        return JsonResponse({}, status=401)
    answer = check_received_answer(answer_id)
    if answer is None:
        return JsonResponse({}, status=404)
    if user != answer.question.author:
        logger.error('%s not author of question', request.user.username)
        return JsonResponse({}, status=403)
    answer.change_correct()
    return JsonResponse({}, status=200)


def publish_answer(request: WSGIRequest, answer: Answer, is_author: bool):
    """
    Publish an answer to Centrifugo.

    Args:
        request (WSGIRequest): The request containing information about the user.
        answer (Answer): The answer to publish.
        is_author (bool): Whether the user is the author of the question.
    """
    if 'test' in sys.argv:
        return {'success': True}
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
    try:
        response = requests.post(url, headers=headers, data=json.dumps(data), timeout=5)
        if response.status_code != 200:
            logger.error('failed to publish answer')
    except requests.exceptions.ConnectionError:
        logger.critical('failed to publish answer (don\'t working centrifugo)')


@login_required
def centrifugo_token(request: WSGIRequest) -> JsonResponse:
    """
    Returns a JSON response containing a Centrifugo token.

    The token is generated with the user's id and is used to send messages to Centrifugo.

    Args:
        request (WSGIRequest): The request containing information about the user.

    Returns:
        JsonResponse: A response containing the generated Centrifugo token.
    """
    token = generate_centrifugo_token(request.user.id)
    return JsonResponse({'token': token}, status=200)


@csrf_exempt
def csp_report_view(request: WSGIRequest) -> HttpResponse:
    """
    A view for receiving CSP violation reports.

    This view is used to receive CSP violation reports from the browser.
    The report is logged with the CRITICAL level.

    Args:
        request (WSGIRequest): The request containing the CSP violation report.
    """
    if request.method == 'POST':
        report = json.loads(request.body)
        logger.critical('CSP violation: %s', report)
    return HttpResponse()


@require_POST
def toggle_theme(request: WSGIRequest) -> JsonResponse:
    try:
        data = json.loads(request.body)
        theme = data.get('theme')
        if theme in ['light', 'dark']:
            request.session['color_theme'] = theme
            return JsonResponse({}, status=200)
    except json.JSONDecodeError:
        return JsonResponse({'message': 'wrong data'}, status=400)
    return JsonResponse({}, status=400)
