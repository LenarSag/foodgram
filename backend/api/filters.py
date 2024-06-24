from django_filters import (
    ModelMultipleChoiceFilter,
    NumberFilter,
    FilterSet,
)

from recipes.models import Recipe, Tag


class RecipeFilter(FilterSet):
    """Список фильтров для рецептов."""

    author = NumberFilter(field_name="author__id")
    tags = ModelMultipleChoiceFilter(
        field_name="tags__slug",
        queryset=Tag.objects.all(),
        to_field_name="slug",
    )
    is_favorited = NumberFilter(method="filter_is_favorited")
    is_in_shopping_cart = NumberFilter(method="filter_is_in_shopping_cart")

    def filter_is_favorited(self, queryset, name, value):
        """Возвращает рецепты по фильтру "в избранном"."""
        value = bool(value)
        if self.request.user.is_authenticated and value:
            return queryset.filter(favorites__user=self.request.user)
        elif self.request.user.is_authenticated and not value:
            return queryset.exclude(favorites__user=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        """Возвращает рецепты по фильтру "в корзине"."""
        value = bool(value)
        if self.request.user.is_authenticated and value:
            return queryset.filter(in_carts__user=self.request.user)
        elif self.request.user.is_authenticated and not value:
            return queryset.exclude(in_carts__user=self.request.user)
        return queryset

    class Meta:
        model = Recipe
        fields = ("author", "tags", "is_favorited", "is_in_shopping_cart")
