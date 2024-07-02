from rest_framework.pagination import PageNumberPagination

from core.constants import OBJ_PER_PAGE


class CustomPaginatorWithLimit(PageNumberPagination):
    """Пагинатор с атрибутом лимита количества выведенных страниц."""

    page_size_query_param = "limit"
    page_size = OBJ_PER_PAGE
