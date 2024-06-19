import base64

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from rest_framework import serializers
from django.core.files.base import ContentFile
from drf_extra_fields.fields import Base64ImageField

from .mixins import ValidateUsernameMixin

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для пользователей."""

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
            # "is_subscribed",
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


class AvatarSerializer(serializers.ModelSerializer):
    """Сериализатор для аватаров."""

    avatar = Base64ImageField(required=True)

    class Meta:
        model = User
        fields = ("avatar",)

    def validate_avatar(self, value):
        """Проверяем, что передано не пустое поле."""
        if value is None:
            raise ValidationError("Передано пустое поле avatar")
        return value
