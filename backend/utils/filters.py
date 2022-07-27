from django.conf import settings
from django_filters.rest_framework import FilterSet, filters
from rest_framework.exceptions import ValidationError
from rest_framework.filters import SearchFilter

from recipes.models import Recipe
from tags.models import Tag


class DoubleSearchBackend(SearchFilter):
    """
    Бекенд для фильтрации с выводом в заданой последовательности.

    Поддерживает примущества базавого фильтра, но выводит
    результаты в последовательности указанной в search_fields
    """
    def filter_queryset(self, request, queryset, view):
        search_fields = self.get_search_fields(view, request)
        search_terms = self.get_search_terms(request)

        if not search_fields or not search_terms:
            return queryset

        orm_lookups = [
            self.construct_search(str(search_field))
            for search_field in search_fields
        ]

        filtered_queryset = []
        for search_term in search_terms:
            for orm_lookup in orm_lookups:
                ingredients = (queryset.filter(
                    **{orm_lookup: search_term}
                ))
                for ingredient in ingredients:
                    if ingredient not in filtered_queryset:
                        filtered_queryset.append(ingredient)

        return filtered_queryset


class RecipeFilterSet(FilterSet):
    """
    Фильтерсет для кастомной фильтрации.
    Фильтрация идет по следующим query праметрам:
    - author: указывается id автора рецепта
    - tags: указывается slug тега(ов)
    - is_favorited: true, выводит список рецептов из избранного
    - is_in_shopping_cart: true, выводит список рецептов из корзины
    Note:
    --------
    is_favorited и is_in_shopping_cart - самостоятельные параметры, совместное
    использование, в том числе с author приводит к возвращениее HTTP404_BAD_REQUEST
    """
    tags = filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        to_field_name='slug',
        field_name='tags__slug'
    )
    is_favorited = filters.CharFilter(
        method='check_is_in_favorited'
    )
    is_in_shopping_cart = filters.CharFilter(
        method='check_is_in_shopping_cart'
    )

    def check_is_in_favorited(self, queryset, name, value):
        is_favorited = self.request.query_params.get('is_favorited')
        if is_favorited == '1' or is_favorited == 'true':
            try:
                favorite_recipes = (self.request.user.
                                    marked_recipes.
                                    fovorited_recipe.values_list('id'))
                return queryset.filter(
                    id__in=favorite_recipes
                )
            except AttributeError:
                return queryset.none()
        return queryset

    def check_is_in_shopping_cart(self, queryset, name, value):
        is_in_shopping_cart = (self.
                               request.query_params.get('is_in_shopping_cart'))
        if is_in_shopping_cart == '1' or is_in_shopping_cart == 'true':
            try:
                recipes_for_download = (self.request.user.
                                        marked_recipes.
                                        recipe_for_download.values_list('id'))
                return queryset.filter(
                    id__in=recipes_for_download
                )
            except AttributeError:
                return queryset.none()
        return queryset

    def is_valid(self):
        shopping_cart = self.request.query_params.get('is_in_shopping_cart')
        favorited = self.request.query_params.get('is_favorited')

        if shopping_cart and favorited:
            raise ValidationError({'error': settings.ERROR_MESSAGE.get('both_query_params')})
        elif (shopping_cart or favorited) and self.request.query_params.get('author'):
            raise ValidationError({'error': settings.ERROR_MESSAGE.get('unique_query_params')})

        return super().is_valid()

    class Meta:
        model = Recipe
        fields = ['author', 'tags']
