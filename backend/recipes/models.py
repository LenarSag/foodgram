from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator

from core.constants import (
    MAX_AMOUNT_INGREDIENTS,
    MAX_COOKING_TIME,
    MAX_NAME_LENGTH,
    MAX_TAG_NAME_LENGTH,
    MAX_SLUG_LENGTH,
    MAX_UNIT_LENGTH,
    MIN_AMOUNT_INGREDIENTS,
    MIN_COOKING_TIME,
)
from .utils import get_hashed_short_url


User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        max_length=MAX_TAG_NAME_LENGTH, unique=True, verbose_name="Тег"
    )
    slug = models.SlugField(
        max_length=MAX_SLUG_LENGTH, unique=True, verbose_name="Слаг"
    )

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"
        ordering = ("name",)
        unique_together = ("name", "slug")

    def __str__(self) -> str:
        return f"{self.name}"


class Ingredient(models.Model):
    name = models.CharField(
        max_length=MAX_NAME_LENGTH, verbose_name="Ингредиент"
    )
    measurement_unit = models.CharField(
        max_length=MAX_UNIT_LENGTH, verbose_name="Единица измерения"
    )

    class Meta:
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"
        ordering = ("name",)
        unique_together = ("name", "measurement_unit")

    def __str__(self) -> str:
        return f"{self.name} {self.measurement_unit}"


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="recipes",
        verbose_name="Автор рецепта",
    )
    name = models.CharField(
        max_length=MAX_NAME_LENGTH, verbose_name="Название рецепта"
    )
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
    tags = models.ManyToManyField(
        Tag, related_name="recipes", verbose_name="Теги"
    )
    cooking_time = models.IntegerField(
        verbose_name="Время приготовления",
        validators=[
            MinValueValidator(
                MIN_COOKING_TIME,
                message=(
                    "Минимальное время приготовления "
                    f"не может быть меньше {MIN_COOKING_TIME}"
                ),
            ),
            MaxValueValidator(
                MAX_COOKING_TIME,
                message=(
                    "Максимальное время приготовления "
                    f"не может быть больше {MAX_COOKING_TIME}"
                ),
            )
        ],
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Время добавления"
    )

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"
        ordering = ("-created_at",)
        unique_together = ("name", "author")

    def __str__(self):
        return f"{self.name}. Автор: {self.author.username}"

    @property
    def short_url(self):
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
                MIN_AMOUNT_INGREDIENTS,
                message=(
                    "Количество ингредиента не может быть "
                    f"меньше {MIN_AMOUNT_INGREDIENTS}"
                ),
            ),
            MaxValueValidator(
                MAX_AMOUNT_INGREDIENTS,
                message=(
                    "Количество ингредиента не может быть "
                    f"больше {MAX_AMOUNT_INGREDIENTS}"
                ),
            )
        ),
    )

    class Meta:
        verbose_name = "Ингредиент"
        verbose_name_plural = "Количество ингредиентов"
        ordering = ("recipe",)
        unique_together = ("recipe", "ingredient")

    def __str__(self):
        return (
            f"{self.amount} {self.ingredient.measurement_unit} "
            f"{self.ingredient.name} в {self.recipe.name}"
        )


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
        unique_together = ("recipe", "user")

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

    class Meta:
        verbose_name = "Рецепт в корзине"
        verbose_name_plural = "Рецепты в корзине"
        ordering = ("user",)
        unique_together = ("recipe", "user")

    def __str__(self):
        return f"У {self.user.username} в корзине {self.recipe.name}"
