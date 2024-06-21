from django.contrib.auth import get_user_model
from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField

from recipes.models import Ingredient, Recipe, Tag

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
    author = UserSerializer(read_only=True)
    # is_favorited = serializers.SerializerMethodField()
    # is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            # "is_favorited",
            # "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        )
        # read_only_fields = (
        #     "is_favorite",
        #     "is_shopping_cart",
        # )

    def get_ingredients(self, recipe):
        return None
