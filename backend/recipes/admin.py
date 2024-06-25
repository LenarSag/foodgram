from django.contrib import admin

from .models import Ingredient, Recipe, Tag
from core.constants import INGREDIENTS_PER_PAGE, POSTS_PER_PAGE


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "measurement_unit",
    )
    search_fields = ("name",)
    list_per_page = INGREDIENTS_PER_PAGE


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        "author",
        "name",
        "image",
        "text",
        "get_ingredients",
        "get_tags",
        "cooking_time",
        "favorites_count",
    )
    list_editable = ("name", "text", "image")
    search_fields = ("author__username", "name")
    list_filter = ("tags__name",)
    list_per_page = POSTS_PER_PAGE

    @admin.display(description="Ингредиенты")
    def get_ingredients(self, obj):
        """Возвращает название ингредиентов."""
        return ", ".join([ingredient.name for ingredient in obj.ingredients.all()])

    @admin.display(description="Теги")
    def get_tags(self, obj):
        """Возвращает название тегов."""
        return ", ".join([tag.name for tag in obj.tags.all()])

    @admin.display(description="Добавлений в избранное")
    def favorites_count(self, obj):
        """Возвращает кол-во добавлений рецепта в избранное."""
        return obj.favorites.count()


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "slug",
    )
    search_fields = ("name",)
    list_per_page = POSTS_PER_PAGE
