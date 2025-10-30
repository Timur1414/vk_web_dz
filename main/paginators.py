import logging
from typing import Any
from django.core.paginator import Paginator, EmptyPage, Page


logger = logging.getLogger('default')


def paginate(objects_list, request, per_page=10) -> Page[Any]:
    """
    Returns a page object from the given list of objects, based on the request.
    The function returns a page object that can be iterated over to get the objects of that page.
    """
    paginator = Paginator(objects_list, per_page)
    page_number = request.GET.get('page', '1')
    try:
        page_number = int(page_number)
        if page_number < 1:
            logger.warning('page number < 1')
            raise ValueError()
        page_obj = paginator.get_page(page_number)
        return page_obj
    except (EmptyPage, ValueError):
        return paginator.get_page(1)
