from django.contrib.auth import get_user_model
from django.db.models import F
from django.db.transaction import atomic
from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField

from .validators import get_validated_tags, get_validated_ingredients
from recipes.models import (
    Cart, Favorite, Ingredient, Recipe, RecipeIngredient, Tag
)


User = get_user_model()


class UserCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания пользователей."""

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "password",
        )
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        """Создаёт нового пользователя c хешированием пароля."""
        user = User(
            email=validated_data.get("email"),
            username=validated_data.get("username"),
            first_name=validated_data.get("first_name"),
            last_name=validated_data.get("last_name"),
        )
        user.set_password(validated_data.get("password"))
        user.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор пользователей."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "avatar",
            "is_subscribed",
        )

    def get_is_subscribed(self, obj):
        """Проверяет подписку текущего пользователя на объект запроса."""
        request = self.context.get("request")
        return (
            request.user.is_authenticated
            and request.user.following_subscriptions.filter(
                following=obj
            ).exists()
        )


class AvatarSerializer(serializers.ModelSerializer):
    """Сериализатор для аватара."""

    avatar = Base64ImageField(required=True)

    class Meta:
        model = User
        fields = ("avatar",)

    def validate_avatar(self, value):
        """Проверяет, что поле аватар не пустое."""
        if not value:
            raise serializers.ValidationError(
                "Поле не может быть пустым, загрузите файл."
            )
        return value


class ShortRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Recipe для списка подписок."""

    class Meta:
        model = Recipe
        fields = (
            "id",
            "name",
            "image",
            "cooking_time",
        )


class SubscriptionsSerializer(UserSerializer):
    """Сериализатор пользователей на которых подписан текущий пользователь."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "avatar",
            "is_subscribed",
            "recipes",
            "recipes_count",
        )

    def get_is_subscribed(self, obj):
        """Переопределяет метод родительского класса."""
        return True

    def get_recipes_count(self, obj):
        """Подсчитывает кол-во рецептов у пользователя на которго подписан."""
        return obj.recipes.count()

    def get_recipes(self, obj):
        """Возращает рецепты согласно параметру "recipes_limit" в запросе."""
        request = self.context.get("request")
        recipes_limit = request.query_params.get("recipes_limit")

        if recipes_limit:
            try:
                recipes_limit = int(recipes_limit)
                recipes = obj.recipes.all()[:recipes_limit]
            except ValueError:
                recipes = obj.recipes.all()
        else:
            recipes = obj.recipes.all()
        return ShortRecipeSerializer(
            recipes, many=True, context=self.context
        ).data


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тегов."""

    class Meta:
        model = Tag
        fields = "__all__"


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингридиентов."""

    class Meta:
        model = Ingredient
        fields = "__all__"


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для рецептов."""

    ingredients = serializers.SerializerMethodField()
    tags = TagSerializer(many=True, read_only=True)
    image = Base64ImageField(required=True)
    author = UserSerializer(
        read_only=True, default=serializers.CurrentUserDefault()
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        )
        read_only_fields = (
            "is_favorited",
            "is_in_shopping_cart",
        )

    def get_ingredients(self, recipe):
        """Возвращает список ингредиентов для рецепта."""
        ingredients = recipe.ingredients.values(
            "id", "name", "measurement_unit", amount=F("recipe__amount")
        )
        return ingredients

    def get_is_favorited(self, recipe):
        """Проверяет есть ли рецепт в избранном."""
        user = self.context.get("view").request.user
        return (
            user.is_authenticated
            and user.favorite_recipes.filter(recipe=recipe).exists()
        )

    def get_is_in_shopping_cart(self, recipe):
        """Проверяет есть ли рецепт в корзине."""
        user = self.context.get("view").request.user
        return (
            user.is_authenticated
            and user.cart.filter(recipe=recipe).exists()
        )

    def validate_image(self, value):
        """Проверяет, что поле изображение не пустое."""
        if not value:
            raise serializers.ValidationError(
                "Поле не может быть пустым, загрузите файл."
            )
        return value

    def validate(self, data):
        """Проверяет поле тегов и ингредиентов."""
        ingredients = self.initial_data.get("ingredients")
        tags = self.initial_data.get("tags")
        user = self.context.get("request").user

        validated_tags = get_validated_tags(tags)
        validated_ingredients = get_validated_ingredients(ingredients)

        data.update(
            {
                "tags": validated_tags,
                "ingredients": validated_ingredients,
                "author": user,
            }
        )
        return data

    def _set_ingredients(self, recipe, ingredients):
        """Добавляет ингредиенты в промежуточную модель."""
        RecipeIngredient.objects.bulk_create(
            [
                RecipeIngredient(
                    ingredient_id=ingredient.get("id"),
                    amount=ingredient.get("amount"),
                    recipe=recipe,
                )
                for ingredient in ingredients
            ]
        )

    @atomic
    def create(self, validated_data):
        """Создает новый рецепт."""
        ingredients = validated_data.pop("ingredients")
        tags = validated_data.pop("tags")

        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self._set_ingredients(recipe, ingredients)

        return recipe

    @atomic
    def update(self, recipe, validated_data):
        """Обновляет рецепт."""
        new_ingredients = validated_data.pop("ingredients")
        new_tags = validated_data.pop("tags")

        recipe.tags.clear()
        recipe.tags.set(new_tags)
        recipe.ingredients.clear()
        self._set_ingredients(recipe, new_ingredients)

        return super().update(recipe, validated_data)


class AddToCartSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления рецептов в список покупок."""

    class Meta:
        model = Cart
        fields = ("user", "recipe")


class AddToFavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления рецептов в список избранных."""

    class Meta:
        model = Favorite
        fields = ("user", "recipe")
