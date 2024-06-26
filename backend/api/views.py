from django.contrib.auth import get_user_model
from django.db.models import Sum, F
from django_filters.rest_framework import DjangoFilterBackend
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from djoser.views import UserViewSet as DjoserUserViewSet

from .filters import RecipeFilter, IngredientFilter
from .serializers import (
    AddToFavoriteSerializer,
    AvatarSerializer,
    AddToCartSerializer,
    RecipeSerializer,
    ShortRecipeSerializer,
    SubscriptionsSerializer,
    TagSerializer,
    IngredientSerializer,
)
from .paginators import CustomPaginatorWithLimit
from .permissions import ReadOnlyOrIsAuthenticatedOrAuthor
from .mixins import NoPutUpdateMixin
from .utils import generate_pdf
from users.models import Subscription
from recipes.models import Cart, Favorite, Ingredient, Recipe, Tag
from core.constants import PDF_FILENAME, SHORT_LINK_URL_PATH


User = get_user_model()


class UserViewSet(DjoserUserViewSet):
    """Вьюсет получения/создания пользователей."""

    pagination_class = CustomPaginatorWithLimit

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
        """Добавляет аватар пользователя."""
        user = request.user
        serializer = AvatarSerializer(
            user, data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @avatar.mapping.delete
    def delete_avatar(self, request):
        """Удаляет аватар пользователя."""
        if request.user.avatar:
            request.user.avatar.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        url_path="subscribe",
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
        return Response(
            {"errors": "Вы уже подписаны на этого пользователя!"},
            status=status.HTTP_400_BAD_REQUEST
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
        permission_classes=(IsAuthenticated,),
    )
    def subscriptions(self, request):
        """Возвращает пользователей, на которых подписан текущий юзер."""
        user = self.request.user
        following_users = User.objects.filter(
            follower_subscriptions__follower=user
        )
        pages = self.paginate_queryset(following_users)
        serializer = SubscriptionsSerializer(
            pages, many=True, context={"request": request}
        )
        return self.get_paginated_response(serializer.data)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет получения тэгов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет получения ингредиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class RecipeViewSet(NoPutUpdateMixin, viewsets.ModelViewSet):
    """Вьюсет получения/добавления/удаления рецептов."""

    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (ReadOnlyOrIsAuthenticatedOrAuthor,)
    pagination_class = CustomPaginatorWithLimit
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    @action(detail=True, url_path="get-link")
    def get_short_link(self, request, pk=None):
        """Формируем короткую ссылку на рецепт."""
        recipe = get_object_or_404(Recipe, pk=pk)
        short_url = recipe.get_short_url
        url = request.build_absolute_uri(
            f"/{SHORT_LINK_URL_PATH}/{short_url}/"
        )
        return Response(
            {"short-link": url},
            status=status.HTTP_200_OK,
        )

    @action(
        detail=False,
        url_path="download_shopping_cart",
        permission_classes=(IsAuthenticated,),
    )
    def download_shopping_cart(self, request):
        """Возвращает список покупок в формате PDF."""
        user = request.user
        ingredients = (
            Ingredient.objects.filter(recipe__recipe__in_carts__user=user)
            .values("name", measurement=F("measurement_unit"))
            .annotate(amount=Sum("recipe__amount"))
        )

        pdf_buffer = generate_pdf(ingredients)

        response = HttpResponse(pdf_buffer, content_type="application/pdf")
        response["Content-Disposition"] = (
            f"attachment; filename={PDF_FILENAME}"
        )
        return response

    @action(
        detail=True,
        url_path="shopping_cart",
        methods=("post",),
        permission_classes=(IsAuthenticated,),
    )
    def shopping_cart(self, request, pk=None):
        """Добавляет рецепт в список покупок."""
        user_id = request.user.id
        recipe = get_object_or_404(Recipe, pk=pk)
        data = {"user": user_id, "recipe": recipe.pk}
        serializer = AddToCartSerializer(
            data=data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        recipe_serializer = ShortRecipeSerializer(
            recipe, context={"request": request}
        )
        return Response(recipe_serializer.data, status=status.HTTP_201_CREATED)

    @shopping_cart.mapping.delete
    def delete_recipe_from_shopping_cart(self, request, pk=None):
        """Удаляет рецепт из списка покупок."""
        recipe = get_object_or_404(Recipe, pk=pk)
        deleted = Cart.objects.filter(
            user=request.user, recipe=recipe
        ).delete()
        if not deleted[0]:
            return Response(
                {"errors": "Этого рецепта нет в указанном списке"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        url_path="favorite",
        methods=("post",),
        permission_classes=(IsAuthenticated,),
    )
    def favorite(self, request, pk=None):
        """Добавляет рецепт в список избранного."""
        user_id = request.user.id
        recipe = get_object_or_404(Recipe, pk=pk)
        data = {"user": user_id, "recipe": recipe.pk}
        serializer = AddToFavoriteSerializer(
            data=data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        recipe_serializer = ShortRecipeSerializer(
            recipe, context={"request": request}
        )
        return Response(recipe_serializer.data, status=status.HTTP_201_CREATED)

    @favorite.mapping.delete
    def delete_recipe_from_favorite(self, request, pk=None):
        """Удаляет рецепт из списка избранного."""
        recipe = get_object_or_404(Recipe, pk=pk)
        deleted = Favorite.objects.filter(
            user=request.user, recipe=recipe
        ).delete()
        if not deleted[0]:
            return Response(
                {"errors": "Этого рецепта нет в указанном списке"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)
