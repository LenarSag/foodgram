from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator

from core.constants import (
    MAX_NAME_LENGTH,
    MAX_TAG_NAME_LENGTH,
    MAX_SLUG_LENGTH,
    MAX_UNIT_LENGTH,
)
from .utils import get_hashed_short_url

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        max_length=MAX_TAG_NAME_LENGTH, unique=True, verbose_name="Тэг"
    )
    slug = models.SlugField(
        max_length=MAX_SLUG_LENGTH, unique=True, verbose_name="Слаг"
    )

    class Meta:
        verbose_name = "Тэг"
        verbose_name_plural = "Тэги"
        ordering = ("name",)

    def __str__(self) -> str:
        return f"{self.name}"


class Ingredient(models.Model):
    name = models.CharField(max_length=MAX_NAME_LENGTH, verbose_name="Ингридиент")
    measurement_unit = models.CharField(
        max_length=MAX_UNIT_LENGTH, verbose_name="Единица измерения"
    )

    class Meta:
        verbose_name = "Ингридиент"
        verbose_name_plural = "Ингридиенты"
        ordering = ("name",)

    def __str__(self) -> str:
        return f"{self.name} {self.measurement_unit}"


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="recepies",
        verbose_name="Автор рецепта",
    )
    name = models.CharField(max_length=MAX_NAME_LENGTH, verbose_name="Название рецепта")
    image = models.ImageField(
        upload_to="recipes/images/",
        verbose_name="Фото блюда",
    )
    text = models.TextField(verbose_name="Описание рецепта")
    ingredients = models.ManyToManyField(
        Ingredient,
        related_name="recipes",
        through="RecipeIngredient",
        verbose_name="Ингредиенты блюда",
    )
    tags = models.ManyToManyField(Tag, related_name="recipes", verbose_name="Тэги")
    cooking_time = models.IntegerField(
        validators=[
            MinValueValidator(
                1, message="Минимальное время приготовления не может быть меньше 1"
            )
        ],
        verbose_name="Время приготовления",
    )

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"
        ordering = ("name",)
        constraints = (
            models.UniqueConstraint(
                fields=("name", "author"),
                name="unique_for_author",
            ),
        )

    def __str__(self):
        return f"{self.name}. Автор: {self.author.username}"

    @property
    def get_short_url(self):
        short_url = get_hashed_short_url(self.id)
        return short_url


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        related_name="ingredient",
        on_delete=models.CASCADE,
        verbose_name="Рецепты",
    )
    ingredient = models.ForeignKey(
        Ingredient,
        related_name="recipe",
        on_delete=models.CASCADE,
        verbose_name="Ингредиенты",
    )
    amount = models.IntegerField(
        verbose_name="Количество",
        validators=(
            MinValueValidator(
                1,
                message="Количество ингредиента не может быть меньше 1",
            ),
        ),
    )

    class Meta:
        verbose_name = "Ингредиент"
        verbose_name_plural = "Количество ингредиентов"
        ordering = ("recipe",)
        constraints = (
            models.UniqueConstraint(
                fields=(
                    "recipe",
                    "ingredient",
                ),
                name="unique_recipe_ingridient",
            ),
        )

    def __str__(self):
        return f"{self.amount} {self.ingredient.unit} {self.ingredient.name} в {self.recipe.name}"


class Favorite(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        related_name="favorites",
        on_delete=models.CASCADE,
        verbose_name="Избранные рецепты",
    )
    user = models.ForeignKey(
        User,
        related_name="favorite_recipes",
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
    )

    class Meta:
        verbose_name = "Избранный рецепт"
        verbose_name_plural = "Избранные рецепты"
        ordering = ("user",)
        constraints = (
            models.UniqueConstraint(
                fields=(
                    "recipe",
                    "user",
                ),
                name="unique_favorite_recipe",
            ),
        )

    def __str__(self):
        return f"{self.user.username} любит {self.recipe.name}"


class Cart(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        related_name="in_carts",
        on_delete=models.CASCADE,
        verbose_name="Рецепт в списке",
    )

    user = models.ForeignKey(
        User,
        related_name="cart",
        on_delete=models.CASCADE,
        verbose_name="Владлец списка",
    )

    constraints = (
        models.UniqueConstraint(
            fields=(
                "recipe",
                "user",
            ),
            name="unique_recipe_in_cart",
        ),
    )

    def __str__(self):
        return f"У {self.user.username} в корзине {self.recipe.name}"
