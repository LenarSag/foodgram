from rest_framework import serializers

from recipes.models import Tag, Ingredient
from core.constants import MIN_AMOUNT_INGREDIENTS


def get_validated_tags(tags):
    """Валидирует теги."""
    if not tags:
        raise serializers.ValidationError("Поле теги не может быть пустым!")
    try:
        tags_id_list = [int(tag) for tag in tags]
    except ValueError:
        raise serializers.ValidationError(
            "Все значения id тегов должны быть целыми числами!"
        )
    if len(tags_id_list) != len(set(tags_id_list)):
        raise serializers.ValidationError("Теги должны быть уникальными!")

    existing_tags = Tag.objects.filter(
        id__in=tags_id_list
    ).values_list('id', flat=True)
    missing_tags = set(tags_id_list) - set(existing_tags)
    if missing_tags:
        raise serializers.ValidationError(
            f"Тег(а) с id {missing_tags} не существуют!"
        )
    return tags


def get_validated_ingredients(ingredients):
    """Валидирует ингредиенты."""
    if not ingredients:
        raise serializers.ValidationError(
            "Поле инредиенты не может быть пустым!"
        )
    try:
        ingredients_id_list = [
            int(ingredient.get("id")) for ingredient in ingredients
        ]
    except ValueError:
        raise serializers.ValidationError(
            "Все значения id ингредиентов должны быть целыми числами!"
        )
    if len(ingredients_id_list) != len(set(ingredients_id_list)):
        raise serializers.ValidationError(
            "Ингредиенты должны быть уникальными!"
        )

    try:
        ingredients_amount_list = [
            int(ingredient.get("amount")) for ingredient in ingredients
        ]
    except ValueError:
        raise serializers.ValidationError(
            "Все значения amount ингредиентов должны быть целыми числами!"
        )
    if any(
        amount < MIN_AMOUNT_INGREDIENTS for amount in ingredients_amount_list
    ):
        raise serializers.ValidationError(
            "Количество ингредиента не может быть меньше 1"
        )

    existing_ingredients = Ingredient.objects.filter(
        id__in=ingredients_id_list
    ).values_list('id', flat=True)
    missing_ingredients = set(ingredients_id_list) - set(existing_ingredients)
    if missing_ingredients:
        raise serializers.ValidationError(
            f"Ингредиент(ы) с id {missing_ingredients} не существуют!"
        )
    return ingredients
