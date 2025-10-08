# from django.views.generic import ListView
from django.core.paginator import Paginator


def paginate(objects_list, request, per_page=10):
    paginator = Paginator(objects_list, per_page)
    page_number = request.GET.get('page')
    try:
        page_number = int(page_number)
    except ValueError:
        return
    page_obj = paginator.get_page(page_number)
    return page_obj.object_list

# class QuestionListView(ListView):
#     paginate_by = 2
#     model = Question
