from django.conf import settings

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from .models import MarkedUserRecipes, Recipe
from .serializers import (CreateRecipeSerializer, RecipeSerializer,
                          ShortRecipeSerializer)
from utils.file_creators import create_ingredients_list_pdf
from utils.filters import RecipeFilterSet
from utils.fun_setting import (check_the_occurrence,
                                          send_bad_request_response)
from utils.permissions import IsOwnerOrReadOnly


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilterSet
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def get_serializer_class(self):
        if (self.action == 'create'
                or self.action == 'update' or self.action == 'partial_update'):
            return CreateRecipeSerializer
        return super().get_serializer_class()

    @action(detail=True, serializer_class=ShortRecipeSerializer,
            methods=['post'], url_path='favorite',
            permission_classes=[IsAuthenticated])
    def mark_favorite_recipe(self, request, id=None, *args, **kwargs):
        return self._mark_recipes(request, id=None, *args, **kwargs)

    @mark_favorite_recipe.mapping.delete
    def delete_favorite_recipe(self, request, id=None, *args, **kwargs):
        return self._delete_mark_recipes(request, id=None, *args, **kwargs)

    def _mark_recipes(self, request, id=None, *args, **kwargs):
        marked_recipes, _ = MarkedUserRecipes.objects.get_or_create(
                                                            user=request.user
                                                        )
        recipe = self.get_object()

        if request.path.split('/')[-2] == 'favorite':
            if check_the_occurrence(recipe,
                                    'favorited_recipe',
                                    marked_recipes):

                return send_bad_request_response(
                    settings.ERROR_MESSAGE.get('alredy_favorited')
                )

            marked_recipes.favorited_recipe.add(recipe)
        else:
            if check_the_occurrence(recipe,
                                    'recipe_for_download',
                                    marked_recipes):

                return send_bad_request_response(
                    settings.ERROR_MESSAGE.get('alredy_in_cart')
                )

            marked_recipes.recipe_for_download.add(recipe)

        serializer = self.get_serializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def _delete_mark_recipes(self, request, id=None, *args, **kwargs):
        marked_recipes, _ = MarkedUserRecipes.objects.get_or_create(
                                                            user=request.user
                                                        )
        recipe = self.get_object()

        if request.path.split('/')[-2] == 'favorite':
            if not check_the_occurrence(recipe,
                                        'favorited_recipe',
                                        marked_recipes):

                return send_bad_request_response(
                    settings.ERROR_MESSAGE.get('not_in_favorited')
                )
            marked_recipes.favorited_recipe.remove(recipe.id)
        else:
            if not check_the_occurrence(recipe,
                                        'recipe_for_download',
                                        marked_recipes):

                return send_bad_request_response(
                    settings.ERROR_MESSAGE.get('not_in_cart')
                )

            marked_recipes.recipe_for_download.remove(recipe.id)

        return Response(status=status.HTTP_204_NO_CONTENT)

    def _get_ingredient_list(self, shopping_cart: list) -> dict:
        ingredient_list = {}

        for recipe in shopping_cart:
            ingredients = recipe.ingredients.through.objects.filter(
                                                                recipe=recipe
                                                            )
            for ingredient in ingredients:
                key = (f'{ingredient.ingredients.name} '
                       f'({ingredient.ingredients.measurement_unit})')
                try:
                    ingredient_list[key] += ingredient.amount
                except KeyError:
                    ingredient_list[key] = ingredient.amount

        return ingredient_list
