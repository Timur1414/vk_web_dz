from django import template
from main.models import Answer, AnswerLike

register = template.Library()


@register.filter
def count_answers_of_question(question_id):
    return len(Answer.get_answers_by_question(question_id))


@register.filter
def is_answer_liked(answer, user):
    is_liked = AnswerLike.is_liked(answer, user)
    return is_liked
