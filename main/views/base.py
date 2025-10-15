from typing import Any, Optional
from django.core.handlers.wsgi import WSGIRequest
from django.core.paginator import EmptyPage, Page
from main.models import Tag, Profile, Question, Answer


def create_base_context() -> dict[str, Any]:
    context = {
        'popular_profiles': Profile.popular.get_popular(),
        'popular_tags': Tag.popular.get_popular(),
    }
    return context


def create_context(request: WSGIRequest) -> dict[str, Any]:
    context = create_base_context()
    user = request.user
    profile = Profile.get_profile_of_user(user)
    context.update({
        'user': user,
        'profile': profile,
    })
    return context


def get_paginated_nav_context(questions: Page) -> dict[str, Any]:
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
    return context


def check_received_question(question_id: str) -> Optional[Question]:
    try:
        question_id = int(question_id)
        question = Question.get_question_by_id(question_id)
        if question is None:
            raise ValueError()
    except ValueError:
        return None
    return question


def check_received_answer(answer_id: str) -> Optional[Answer]:
    try:
        answer_id = int(answer_id)
        answer = Answer.get_answer_by_id(answer_id)
        if answer is None:
            raise ValueError()
    except ValueError:
        return None
    return answer
