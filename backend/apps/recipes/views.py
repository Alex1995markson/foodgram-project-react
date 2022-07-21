from django.conf import settings
from django.http import FileResponse

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from .models import MarkedUserRecipe, Recipe
from .srializers import (CreateRecipeSerializer, RecipeSerializer,
                         ShortRecipeSerializer)
from utils.file_creators import create_ingredients_list_pdf
from utils.filters import RecipeFilterSet
from utils.generalizing_functions import (check_the_occurrence,
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

    @action(detail=True, serializer_class=ShortRecipeSerializer, methods=['post'],
            url_path='favorite', permission_classes=[IsAuthenticated])
    def mark_favorite_recipe(self, request, id=None, *args, **kwargs):
        return self._mark_recipes(request, id=None, *args, **kwargs)

    @mark_favorite_recipe.mapping.delete
    def delete_favorite_recipe(self, request, id=None, *args, **kwargs):
        return self._delete_mark_recipes(request, id=None, *args, **kwargs)

    @action(detail=True, serializer_class=ShortRecipeSerializer, methods=['post'],
            url_path='shopping_cart', permission_classes=[IsAuthenticated])
    def mark_download_recipe(self, request, id=None, *args, **kwargs):
        return self._mark_recipes(request, id=None, *args, **kwargs)

    @mark_download_recipe.mapping.delete
    def delete_download_recipe(self, request, id=None, *args, **kwargs):
        return self._delete_mark_recipes(request, id=None, *args, **kwargs)

    def _mark_recipes(self, request, id=None, *args, **kwargs):
        """
        Добавить рецепт в список избранного/список загрузок

        Добавляет в нужный список выбранный рецеп, следит за наличием
        данного рецепта, в случае наличия отсылает соответсвующий ответ.
        """
        marked_recipes, _ = MarkedUserRecipe.objects.get_or_create(
                                                            user=request.user
                                                        )
        recipe = self.get_object()

        if request.resolver_match.url_name == 'favorite':
            if check_the_occurrence(recipe,
                                    'fovorited_recipe',
                                    marked_recipes):

                return send_bad_request_response(
                    settings.ERROR_MESSAGE.get('alredy_favorited')
                )

            marked_recipes.fovorited_recipe.add(recipe)
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
        """
        Удалить рецепт из списка избранного/списка загрузок

        Удаляет из нужнгого списка выбранный рецеп, следит за наличием
        данного рецепта, в случае отсутствия отсылает соответсвующий ответ.
        """
        marked_recipes, _ = MarkedUserRecipe.objects.get_or_create(
                                                            user=request.user
                                                        )
        recipe = self.get_object()

        if request.resolver_match.url_name == 'favorite':
            if not check_the_occurrence(recipe,
                                        'fovorited_recipe',
                                        marked_recipes):

                return send_bad_request_response(
                    settings.ERROR_MESSAGE.get('not_in_favorited')
                )
            marked_recipes.fovorited_recipe.remove(recipe.id)
        else:
            if not check_the_occurrence(recipe,
                                        'recipe_for_download',
                                        marked_recipes):

                return send_bad_request_response(
                    settings.ERROR_MESSAGE.get('not_in_cart')
                )

            marked_recipes.recipe_for_download.remove(recipe.id)

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, url_path='download_shopping_cart',
            permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request, *args, **kwargs):
        shopping_cart = request.user.marked_recipes.recipe_for_download.all()
        ingredient_list = self._get_ingredient_list(shopping_cart)
        return self._send_file_response(ingredient_list)

    def _get_ingredient_list(self, shopping_cart: list) -> dict:
        """
        Получить список ингредиентов.

        Сформировывает словарь из ингредиентов всех рецептов вида:
            {имя (единица измерения): колличество}
        -----
        Note:
            Одинаковые ингредиенты складываются и хранятся ввиде
            суммы под одним ключем.
        -----
        Параметры:
            shopping_cart: list - список обьектов Recipe
        -----
        выходное значение
            dict: словарь ингредиентов ввида:
                {имя (единица измерения): колличество}
        """
        ingredient_for_buy = {}

        for recipe in shopping_cart:
            ingredients = recipe.ingredients.through.objects.filter(
                                                                recipe=recipe
                                                            )
            for ingredient in ingredients:
                key = (f'{ingredient.ingredients.name} '
                       f'({ingredient.ingredients.measurement_unit})')
                try:
                    ingredient_for_buy[key] += ingredient.amount
                except KeyError:
                    ingredient_for_buy[key] = ingredient.amount

        return ingredient_for_buy

    def _send_file_response(self, ingredient_list: dict) -> object:
        """
        Отправить свормированый файл.

        Формирует файл(pdf) на онсове ingredient_list и отправляет его

        ------
        Параметры:
            ingredient_list: dict - словарь ингредиентов ввида:
                {имя (единица измерения): колличество}
        -----
        Выходное значение:
            object - FileResponse
        """
        file_with_ingredients = create_ingredients_list_pdf(ingredient_list)
        return FileResponse(
            file_with_ingredients,
            as_attachment=True,
            filename='product_list.pdf'
        )
