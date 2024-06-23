from rest_framework import permissions


class ReadOnlyOrAuthor(permissions.BasePermission):
    """
    Класс разрешений на получение, создание, обновление, удаление контента.

    Аноним: может только смотреть; аутентифицированный пользователь: смотреть,
    создавать, менять и удалять свой контент.
    """

    def has_object_permission(self, request, view, obj):
        return request.method in permissions.SAFE_METHODS or (
            obj.author == request.user
        )