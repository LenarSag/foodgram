from rest_framework import filters, mixins, status, viewsets
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from djoser.views import UserViewSet as DjoserUserViewSet

from .serializers import UserSerializer

User = get_user_model()


class UserViewSet(DjoserUserViewSet):
    """Вьюсет получения/создания пользователей."""

    pagination_class = PageNumberPagination
    # serializer_class = UserSerializer

    # def get_permissions(self):
    #     if self.action == "me":
    #         return [IsAuthenticated()]
    #     elif self.action == "list":
    #         return [AllowAny()]
    #     return super().get_permissions()


# class UserViewSet(viewsets.ModelViewSet):
#     """Вьюсет получения/создания/обновления/удаления пользователей."""

#     queryset = User.objects.all()
#     serializer_class = UserSerializer
#     permission_classes = (AllowAny,)
#     pagination_class = PageNumberPagination
#     filter_backends = (filters.SearchFilter,)
#     search_fields = ("username",)

#     @action(detail=False, url_path="me", permission_classes=(IsAuthenticated,))
#     def myself(self, request):
#         """Позволяет пользователю получить информацию о себе."""
#         serializer = self.get_serializer(request.user)
#         return Response(serializer.data, status=status.HTTP_200_OK)

#     @action(
#         detail=False,
#         url_path="me/avatar",
#         methods=("put", "delete"),
#         permission_classes=(IsAuthenticated,),
#     )
#     def edit_avatar(self, request):
#         """Позволяет пользователю добавить или удалить аватар."""
#         user = request.user

#         if request.method == "PUT":
#             avatar = request.data.get("avatar")
#             if avatar:
#                 user.avatar = avatar
#                 user.save()
#                 return Response({"status": "avatar updated"}, status=status.HTTP_200_OK)
#             else:
#                 return Response(
#                     {"error": "avatar not provided"}, status=status.HTTP_400_BAD_REQUEST
#                 )

#         elif request.method == "DELETE":
#             user.avatar = None
#             user.save()
#             return Response(
#                 {"status": "avatar deleted"}, status=status.HTTP_204_NO_CONTENT
#             )
