from rest_framework import status
from rest_framework.response import Response


class NoPutUpdateMixin:
    def update(self, request, *args, **kwargs):
        if request.method == "PUT":
            return Response(
                status=status.HTTP_405_METHOD_NOT_ALLOWED,
                data={"detail": 'Метод "PUT" не разрешен.'},
            )
        return super().update(request, *args, **kwargs)
