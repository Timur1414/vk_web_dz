# from django.views.generic import ListView
from django.core.paginator import Paginator, EmptyPage


def paginate(objects_list, request, per_page=10) -> list:
    paginator = Paginator(objects_list, per_page)
    page_number = request.GET.get('page')
    try:
        page_number = int(page_number)
        page_obj = paginator.get_page(page_number)
        return page_obj.object_list
    except (EmptyPage, ValueError):
        return []

# class QuestionListView(ListView):
#     paginate_by = 2
#     model = Question
