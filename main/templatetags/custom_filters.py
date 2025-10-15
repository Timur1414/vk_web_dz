from django import template
from main.models import Answer, AnswerLike

register = template.Library()


@register.filter
def count_answers_of_question(question_id):
    """
    Returns the number of answers to a question with the given id.
    """
    return len(Answer.get_answers_by_question(question_id))


@register.filter
def is_answer_liked(answer, user):
    """
    Returns True if the given user has liked the given answer, False otherwise.
    """
    is_liked = AnswerLike.is_liked(answer, user)
    return is_liked
