import datetime

from django.contrib.auth import get_user_model

from drf_extra_fields.fields import Base64ImageField

from rest_framework import serializers
from rest_framework.generics import get_object_or_404

from ingredients.models import Ingredient
from ingredients.serializers import IngredientSerializer
from tags.models import Tag
from tags.serializers import TagSerializer
from users.serializers import UserSerializer

from .models import IngredientsList, Recipe
from utils.generalizing_functions import check_the_occurrence

User = get_user_model()


class IngredientsListSerializer(serializers.ModelSerializer):
    class Meta:
        model = IngredientsList
        fields = ('ingredients', 'amount')

    def to_representation(self, instance):
        serializer = IngredientSerializer(instance.ingredients)
        return {**serializer.data, 'amount': instance.amount}


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    author = UserSerializer(read_only=True)
    ingredients = IngredientsListSerializer(source='through_recipes',
                                            many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    publication_date = serializers.DateTimeField(write_only=True)

    class Meta:
        model = Recipe
        fields = '__all__'

    def get_is_favorited(self, obj):
        return check_the_occurrence(obj,
                                    'marked_recipes__fovorited_recipe',
                                    self)

    def get_is_in_shopping_cart(self, obj):
        return check_the_occurrence(obj,
                                    'marked_recipes__recipe_for_download',
                                    self)


class CreateRecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField(max_length=None, use_url=True)
    tags = serializers.ListField(
        child=serializers.IntegerField(),
    )
    ingredients = serializers.ListField(
        child=serializers.JSONField(),
    )
    publication_date = serializers.DateTimeField(
        write_only=True,
        default=datetime.datetime.now()
    )

    class Meta:
        model = Recipe
        exclude = ('author',)

    def validate_ingredients(self, value):
        unique_ingredients = []
        for data_ingredient in value:

            ingredient = get_object_or_404(
                Ingredient,
                id=data_ingredient.get('id')
            )

            if ingredient in unique_ingredients:
                raise serializers.ValidationError(
                    f'Дублируется {ingredient.name}, пожалуйста оставьте один'
                    ' ингредиент.'
                )

            unique_ingredients.append(ingredient)

            if int(data_ingredient.get('amount')) <= 0:
                raise serializers.ValidationError(
                    'Вы велли не корректное значение ('
                    f'{data_ingredient.get("amount")}) для {ingredient.name}'
                )

        return value

    def create(self, validated_data):
        tags = self._get_tags(validated_data)
        ingredients = self._get_ingredients(validated_data)

        recipe = Recipe.objects.create(
            author=self.context['request'].user,
            **validated_data
        )

        recipe.tags.add(*tags)

        self._add_ingredients_to_recipe(recipe, ingredients)

        return recipe

    def update(self, instance, validated_data):
        tags = self._get_tags(validated_data)
        ingredients = self._get_ingredients(validated_data)

        instance.tags.clear()
        instance.tags.add(*tags)

        instance.ingredients.clear()
        self._add_ingredients_to_recipe(instance, ingredients)

        return super().update(instance, validated_data)

    def to_representation(self, instance):
        serializer = RecipeSerializer(
            instance,
            context={'request': self.context.get('request')}
        )
        return serializer.data

    def _get_tags(self, validated_data: dict) -> list:
        """
        Сформировать список тегов.
        """
        return [get_object_or_404(Tag, pk=id_tag)
                for id_tag in validated_data.pop('tags')]

    def _get_ingredients(self, validated_data: dict) -> list:
        """
        Сформировать список ингредиентов.
        """
        return [{'object': get_object_or_404(Ingredient, pk=ingredient['id']),
                'amount': int(ingredient['amount'])}
                for ingredient in validated_data.pop('ingredients')]

    def _add_ingredients_to_recipe(self,
                                   recipe: object,
                                   ingredients: list) -> None:
        """
        Добавить в рецепт ингредиенты.
        """
        IngredientsList.objects.bulk_create([
            IngredientsList(
                recipe=recipe,
                ingredients=ingredient.get('object'),
                amount=ingredient.get('amount')
            ) for ingredient in ingredients
        ])


class ShortRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
