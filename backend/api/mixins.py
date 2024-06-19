from rest_framework import serializers


class ValidateUsernameMixin:
    def validate_username(self, username):
        if username and username.lower() == "me":
            raise serializers.ValidationError("Имя не может быть <me>")
        return username
