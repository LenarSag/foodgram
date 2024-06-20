import base64

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from rest_framework import serializers
from django.core.files.base import ContentFile
from drf_extra_fields.fields import Base64ImageField

from .mixins import ValidateUsernameMixin
from users.models import Subscription

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
        return False
        # request = self.context.get("request")

        # if not request.user.is_authenticated:
        #     return False

        # return request.user.following.filter(following=obj).exists()


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
    pass

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
