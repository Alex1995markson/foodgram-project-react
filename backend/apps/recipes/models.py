from django.contrib.auth import get_user_model
from django.db import models

from ingredients.models import Ingredient
from tags.models import Tag

User = get_user_model()


class Recipe(models.Model):
    """Модель для рецептов.
    Основная модель приложения описывающая рецепты.
    Attributes:
        author(int):
            Автор рецепта. Связан с моделю User через ForeignKey.
        name(str):
            Название рецепта. Установлены ограничения по длине.
        image(str):
            Изображение рецепта. Указывает путь к изображению.
        text(str):
            Описание рецепта. Установлены ограничения по длине.
        cooking_time(int):
            Время приготовления рецепта.
        tags(int):
            Связь M2M с моделью Tag.
        ingredients(int):
            Связь M2M с моделью IngredientsList.
            Связь создаётся посредством модели
            IngredientsList с указанием количества ингридиента.
        pub_date(datetime):
            Дата добавления рецепта. Прописывается автоматически.
    """
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта'
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Название рецепта')
    image = models.ImageField(
        upload_to='recipes/images/',
        verbose_name='Картинка рецепта'
    )
    text = models.TextField(
        verbose_name='Описание рецепта'
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        blank=True,
        verbose_name='Теги рецепта'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientsList',
        verbose_name='Ингредиенты'
    )
    publication_date = models.DateTimeField(
        auto_now_add=True,
        editable=False,
    )

    class Meta:
        ordering = ('-publication_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self) -> str:
        return (f'{self.id} | {self.name} | '
                f'{self.tags.all()[:5]} |{self.ingredients.all()[:5]}')


class IngredientsList(models.Model):
    """Количество ингридиентов в блюде.
    Модель связывает Recipe и Ingredient с указанием количества ингридиента.
    Attributes:
        recipe(int):
            Связаный рецепт. Связь через ForeignKey.
        ingredients(int):
            Связаный ингридиент. Связь через ForeignKey.
        amount(int):
            Количиства ингридиента в рецепте.
    """
    recipe = models.ForeignKey(
        Recipe,
        related_name='through_recipes',
        on_delete=models.CASCADE
    )
    ingredients = models.ForeignKey(
        Ingredient,
        related_name='through_ingredients',
        on_delete=models.CASCADE,
    )
    amount = models.PositiveSmallIntegerField()


class MarkedUserRecipes(models.Model):
    """Отмеченные пользователем рецепты
    Attributes:
        user(int):
            Пользователь, который добавил рецепт.
        favorited_recipe(int):
            Любимый рецепт пользователя через M2M
        recipe_for_download(int):
            Рецепты для скачивания через M2M
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='marked_recipes',
        verbose_name='Пользователь',
    )
    fovorited_recipe = models.ManyToManyField(
        Recipe,
        related_name='marked_favorited_recipes',
        blank=True,
        verbose_name='Понравившиеся рецепты',
    )
    recipe_for_download = models.ManyToManyField(
        Recipe,
        related_name='marked_download_recipes',
        blank=True,
        verbose_name='Рецепты для скачивания'
    )

    class Meta:
        verbose_name = 'Отмеченый рецепт'
        verbose_name_plural = 'Отмеченные рецепты'

    def __str__(self) -> str:
        return (f'{self.id} | {self.user} | '
                f'{self.recipe_for_download.all()[:5]} | '
                f'{self.fovorited_recipe.all()[:5]}')
