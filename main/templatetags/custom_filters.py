from django import template
from main.models import Answer

register = template.Library()

@register.filter
def count_answers_of_question(question_id):
    return len(Answer.get_answers_by_question(question_id))
