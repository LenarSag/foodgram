from rest_framework import filters, mixins, status, viewsets
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from djoser.views import UserViewSet as DjoserUserViewSet

from .serializers import AvatarSerializer, SubscriptionsSerializer, UserSerializer

User = get_user_model()


class UserViewSet(DjoserUserViewSet):
    """Вьюсет получения/создания пользователей."""

    pagination_class = PageNumberPagination

    def get_permissions(self):
        if self.action == "retrieve":
            self.permission_classes = (AllowAny,)
        elif self.action == "me":
            self.permission_classes = (IsAuthenticated,)
        return super().get_permissions()

    @action(
        detail=False,
        url_path="me/avatar",
        methods=("put",),
        permission_classes=(IsAuthenticated,),
    )
    def avatar(self, request):
        """Добавление аватара пользователя"""
        user = request.user
        serializer = AvatarSerializer(
            user, data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @avatar.mapping.delete
    def delete_avatar(self, request):
        if request.user.avatar:
            request.user.avatar.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        url_path="subscriptions",
        methods=("get",),
        permission_classes=(IsAuthenticated,),
    )
    def subscriptions(self, request):
        """Возвращает пользователей, на которых подписан текущий юзер."""
        user = self.request.user
        subscriptions = user.following_subscriptions.select_related("following").all()
        following_users = [subscription.following for subscription in subscriptions]
        page = self.paginate_queryset(following_users)
        serializer = UserSerializer(page, many=True, context={"request": request})
        return self.get_paginated_response(serializer.data)


# user = self.request.user
# subscriptions = user.followers.all()
# # Добавляем пагинацию
# page = self.paginate_queryset(subscriptions)
# serializer = SubscriptionsSerializer(
#     page, many=True, context={"request": request}
# )
# return self.get_paginated_response(serializer.data)
