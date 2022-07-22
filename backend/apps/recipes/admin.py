from django.contrib import admin

from .models import IngredientsList, MarkedUserRecipes, Recipe


class IngredientsListInline(admin.TabularInline):
    model = IngredientsList
    can_delete = False
    autocomplete_fields = ['ingredients']
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'total_number_of_additions')
    filter_horizontal = ('tags',)
    list_filter = ('author', 'tags', 'name')
    inlines = (IngredientsListInline,)
    search_fields = ['name', 'author']

    def total_number_of_additions(self, obj):
        return obj.marked_favorited_recipes.all().count()
    total_number_of_additions.short_description = ('Общее количесвто '
                                                   'добавлений в избранное')


@admin.register(MarkedUserRecipes)
class MarkedRecipeAdmin(admin.ModelAdmin):
    list_display = ('user',)
    filter_horizontal = ('fovorited_recipe', 'recipe_for_download')
