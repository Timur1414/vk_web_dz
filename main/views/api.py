from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse
from django.template.loader import render_to_string
from main.models import Question, QuestionLike, AnswerLike
from main.views.base import check_received_question, check_received_answer


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
