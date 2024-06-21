from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from djoser.views import UserViewSet as DjoserUserViewSet

from .serializers import (
    AvatarSerializer,
    SubscriptionsSerializer,
    TagSerializer,
    IngredientSerializer,
)
from users.models import Subscription
from recipes.models import Ingredient, Tag

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
        detail=True,
        methods=("post",),
        permission_classes=(IsAuthenticated,),
    )
    def subscribe(self, request, id=None):
        """Подписывает текущего пользователя на другого пользователя."""
        user_to_follow = get_object_or_404(User, pk=id)
        user = request.user
        if user == user_to_follow:
            return Response(
                {"errors": "Нельзя подписаться на самого себя."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        _, created = Subscription.objects.get_or_create(
            follower=user, following=user_to_follow
        )
        if created:
            serializer = SubscriptionsSerializer(
                user_to_follow, context={"request": request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(
                {"errors": "Вы уже подписаны!"}, status=status.HTTP_400_BAD_REQUEST
            )

    @subscribe.mapping.delete
    def unsubscribe(self, request, id=None):
        """Отписывает текущего пользователя от другого пользователя."""
        user_to_unfollow = get_object_or_404(User, pk=id)
        user = request.user
        subscription = Subscription.objects.filter(
            follower=user, following=user_to_unfollow
        ).first()
        if subscription:
            subscription.delete()
            return Response(
                status=status.HTTP_204_NO_CONTENT,
            )
        return Response(
            {"errors": "Вы не были подписаны на этого пользователя!"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    @action(
        detail=False,
        url_path="subscriptions",
        methods=("get",),
        permission_classes=(IsAuthenticated,),
    )
    def subscriptions(self, request):
        """Возвращает пользователей, на которых подписан текущий юзер."""
        user = self.request.user
        following_users = User.objects.filter(follower_subscriptions__follower=user)
        pages = self.paginate_queryset(following_users)
        serializer = SubscriptionsSerializer(
            pages, many=True, context={"request": request}
        )
        return self.get_paginated_response(serializer.data)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет получения тэгов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет получения ингредиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (filters.SearchFilter,)
    search_fields = ("name",)


class RecipeViewSet(viewsets.ModelViewSet): ...
