from django.http import HttpResponseNotFound
from django.shortcuts import redirect
from django.urls import reverse

from .utils import get_decoded_short_url


def handle_short_url(request, short_url):
    """Перенаправляет запрос с короткого URL."""
    try:
        decoded_values = get_decoded_short_url(short_url)
        if decoded_values:
            recipe_id = decoded_values[0]
            recipe_detail_url = reverse(
                "api:recipes-detail", args=(recipe_id,)
            )
            return redirect(recipe_detail_url)
        return HttpResponseNotFound(
            "URL-адрес недействителен или срок его действия истек."
        )
    except Exception as e:
        return HttpResponseNotFound(
            f"Произошла ошибка {e} при обработке URL-адреса."
        )
