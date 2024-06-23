from django.contrib.auth import get_user_model
from django.db.models import F
from django.db.transaction import atomic
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from drf_extra_fields.fields import Base64ImageField

from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для пользователей."""

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
            "password",
            "is_subscribed",
        )
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        """Создаёт нового пользователя."""
        user = User(
            email=validated_data.get("email"),
            username=validated_data.get("username"),
            first_name=validated_data.get("first_name"),
            last_name=validated_data.get("last_name"),
        )
        user.set_password(validated_data.get("password"))
        user.save()
        return user

    def get_is_subscribed(self, obj):
        """Проверяет подписку текущего пользователя на объект запроса."""
        request = self.context.get("request")
        if not request.user.is_authenticated:
            return False
        return request.user.following_subscriptions.filter(following=obj).exists()


class AvatarSerializer(serializers.ModelSerializer):
    """Сериализатор для аватара."""

    avatar = Base64ImageField(required=True)

    class Meta:
        model = User
        fields = ("avatar",)

    def validate_avatar(self, value):
        if not value:
            raise serializers.ValidationError(
                "Поле не может быть пустым, загрузите файл."
            )
        return value


class SubscriptionsSerializer(UserSerializer):
    """Сериализатор пользователей, на которых подписан текущий пользователь."""

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
        read_only_fields = ("__all__",)

    def get_is_subscribed(self, obj):
        """Переопределяем метод родительского класса."""
        return True


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
    image = Base64ImageField()
    author = UserSerializer(read_only=True, default=serializers.CurrentUserDefault())
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
        validators = [
            UniqueTogetherValidator(
                queryset=Recipe.objects.all(),
                fields=("name", "author"),
                message="У одного автора не может быть более"
                " одного рецепта с одинаковым названием!",
            )
        ]

    def get_ingredients(self, recipe):
        """Возвращает список ингредиентов для рецепта."""
        ingredients = recipe.ingredients.values(
            "id", "name", "measurement_unit", amount=F("recipe__amount")
        )
        return ingredients

    def get_is_favorited(self, recipe):
        """Проверяет есть ли рецепт в избранном."""
        user = self.context.get("view").request.user
        if user.is_anonymous:
            return False
        return user.favorite_recipes.filter(recipe=recipe).exists()

    def get_is_in_shopping_cart(self, recipe):
        """Проверяет есть ли рецепт в корзине."""
        user = self.context.get("view").request.user
        if user.is_anonymous:
            return False
        return user.cart.filter(recipe=recipe).exists()

    def validate(self, data):
        """Проверяет входные данные."""
        ingredients = self.initial_data.get("ingredients")
        tags = self.initial_data.get("tags")
        user = self.context.get("request").user

        if not tags:
            raise serializers.ValidationError("Поле теги не может быть пустым!")
        if len(tags) != len(set(tags)):
            raise serializers.ValidationError("Теги должны быть уникальными!")

        if not ingredients:
            raise serializers.ValidationError("Поле инредиенты не может быть пустым!")
        ingredients_list = [ingredient.get("id") for ingredient in ingredients]
        if len(ingredients_list) != len(set(ingredients_list)):
            raise serializers.ValidationError("Ингредиенты должны быть уникальными!")

        data.update(
            {
                "tags": tags,
                "ingredients": ingredients,
                "author": user,
            }
        )
        return data

    def _set_ingredients(self, recipe, ingredients):
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
        ingredients = validated_data.pop("ingredients")
        tags = validated_data.pop("tags")

        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self._set_ingredients(recipe, ingredients)

        return recipe

    @atomic
    def update(self, recipe, validated_data):
        new_ingredients = validated_data.pop("ingredients")
        new_tags = validated_data.pop("tags")

        recipe.tags.clear()
        recipe.tags.set(new_tags)
        recipe.ingredients.clear()
        self._set_ingredients(recipe, new_ingredients)

        return super().update(recipe, validated_data)
