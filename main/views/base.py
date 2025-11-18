import logging
from typing import Any, Optional
from django.core.paginator import EmptyPage, Page
from django.http import HttpRequest
from main.models import Profile, Question, Answer
from main.cached_data_service import CachedDataService


logger = logging.getLogger('default')


def create_base_context() -> dict[str, Any]:
    """
    Returns a context dictionary containing popular profiles and tags.

    Returns:
        dict[str, Any]: A context dictionary containing popular profiles and tags.
    """
    cache = CachedDataService()
    context = {
        'popular_profiles': cache.get_cached_users(),
        'popular_tags': cache.get_cached_tags(),
    }
    return context


def create_context(request: HttpRequest) -> dict[str, Any]:
    """
    Returns a context dictionary containing information about the current user.
    The context dictionary contains the current user and their profile.

    Args:
        request (HttpRequest): The request containing information about the current user.

    Returns:
        dict[str, Any]: A context dictionary containing information about the current user.
    """
    context = create_base_context()
    user = request.user
    profile = Profile.get_profile_of_user(user)
    context.update({
        'user': user,
        'profile': profile,
    })
    return context


def get_paginated_nav_context(questions: Page) -> dict[str, Any]:
    """
    Returns a context dictionary containing pagination information for the given page of questions.

    Args:
        questions (Page): The page of questions for which to generate pagination information.

    Returns:
        dict[str, Any]: A context dictionary containing pagination information for the given page of questions.
    """
    context: dict[str, Any] = {
        'questions': questions.object_list,
        'page': questions.number
    }
    try:
        context['prev'] = questions.previous_page_number()
    except EmptyPage:
        context['prev'] = None
    try:
        context['next'] = questions.next_page_number()
    except EmptyPage:
        context['next'] = None
    context['first'] = 1
    context['first_ellipsis'] = context['page'] - context['first'] > 2
    context['last'] = questions.paginator.num_pages
    context['last_ellipsis'] = context['last'] - context['page'] > 2
    return context


def check_received_question(question_id: str) -> Optional[Question]:
    """
    Returns the question with the given id if it exists, otherwise None.

    Args:
        question_id (str): The id of the question to retrieve.

    Returns:
        Optional[Question]: The question with the given id if it exists, otherwise None.
    """
    try:
        question_id = int(question_id)
        question = Question.get_question_by_id(question_id)
        if question is None:
            logger.error('user tried to use question with id=%s which does not exist.', question_id)
            raise ValueError()
    except ValueError:
        return None
    return question


def check_received_answer(answer_id: str) -> Optional[Answer]:
    """
    Returns the answer with the given id if it exists, otherwise None.

    Args:
        answer_id (str): The id of the answer to retrieve.

    Returns:
        Optional[Answer]: The answer with the given id if it exists, otherwise None.
    """
    try:
        answer_id = int(answer_id)
        answer = Answer.get_answer_by_id(answer_id)
        if answer is None:
            logger.error('user tried to use answer with id=%s which does not exist.', answer_id)
            raise ValueError()
    except ValueError:
        return None
    return answer
