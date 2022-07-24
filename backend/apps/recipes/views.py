from django.conf import settings
from django.db.models import Sum
from django.http import FileResponse

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from .models import MarkedUserRecipe, Recipe
from .serializers import (CreateRecipeSerializer, RecipeSerializer,
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

    @action(detail=True, serializer_class=ShortRecipeSerializer,
            methods=['post'],
            url_path='favorite', permission_classes=[IsAuthenticated])
    def mark_favorite_recipe(self, request, id=None, *args, **kwargs):
        return self._mark_recipes(request, id=None, *args, **kwargs)

    @mark_favorite_recipe.mapping.delete
    def delete_favorite_recipe(self, request, id=None, *args, **kwargs):
        return self._delete_mark_recipes(request, id=None, *args, **kwargs)

    @action(detail=True, serializer_class=ShortRecipeSerializer,
            methods=['post'],
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

        if request.resolver_match.url_name == 'recipes_api-favorite':
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

        if request.path.split('/')[-2] == 'favorite':
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
        ingredients = self._get_ingredient_list(shopping_cart)
        return self._send_file_response(ingredients)

    def _get_ingredient_list(self, shopping_cart: list) -> dict:
        """Получить список ингредиентов.

            Сформировывает словарь из ингредиентов всех рецептов вида:
                имя (единица измерения): колличество
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
                    имя (единица измерения): колличество
        """

        return {
            f'{ingredient} ({measurement_unit})': amount
                for ingredient, measurement_unit, amount in
                    (Recipe.ingredients.through.objects
                        .filter(recipe__in=shopping_cart)
                        .values_list('ingredients__name',
                                     'ingredients__measurement_unit')
                        .annotate(count_ingredient=Sum('amount')))
        }

    def _send_file_response(self, ingredients: dict) -> object:
        """
        Отправить свормированый файл.

        Формирует файл(pdf) на онсове ingredients и отправляет его

        ------
        Параметры:
            ingredients: dict - словарь ингредиентов ввида:
                {имя (единица измерения): колличество}
        -----
        Выходное значение:
            object - FileResponse
        """
        file_with_ingredients = create_ingredients_list_pdf(ingredients)
        return FileResponse(
            file_with_ingredients,
            as_attachment=True,
            filename='product_list.pdf'
        )
