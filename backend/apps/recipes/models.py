from django.contrib.auth import get_user_model
from django.conf.setting import СONST_LENGTH_MODEL
from django.db import models

from ingredients.models import Ingredient
from tags.models import Tag

User = get_user_model()


class Recipe(models.Model):
    """Модель для рецептов.
    Основная модель приложения описывающая рецепты.
    Attributes:
        name(str):
            Название рецепта. Установлены ограничения по длине.
        author(int):
            Автор рецепта. Связан с моделю User через ForeignKey.
        tags(int):
            Связь M2M с моделью Tag.
        ingredients(int):
            Связь M2M с моделью Ingredient. Связь создаётся посредством модели
            AmountIngredient с указанием количества ингридиента.
        pub_date(datetime):
            Дата добавления рецепта. Прописывается автоматически.
        image(str):
            Изображение рецепта. Указывает путь к изображению.
        text(str):
            Описание рецепта. Установлены ограничения по длине.
        cooking_time(int):
            Время приготовления рецепта.
            Установлены ограничения по максимальным и минимальным значениям.
    """
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор блюда'
    )
    name = models.CharField(
        max_length=СONST_LENGTH_MODEL.MAX_LEN_RECIPES_CHARFIELD,
        verbose_name='Название блюда')
    image = models.ImageField(
        upload_to='recipes/images/',
        verbose_name='Изображение блюда'
    )
    text = models.TextField(
        verbose_name='Описание рецепта',
        max_length=СONST_LENGTH_MODEL.MAX_LEN_RECIPES_TEXTFIELD
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes_tags',
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
        return f'{self.name}. Автор: {self.author.username}'


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
        related_name='through_recipe',
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
            Любимый рецепт пользователя
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='marked_recipes',
        verbose_name='Пользователь',
    )
    favorited_recipe = models.ManyToManyField(
        Recipe,
        related_name='marked_favorited_recipes',
        blank=True,
        verbose_name='Понравившиеся рецепты',
    )

    class Meta:
        verbose_name = 'Отмеченый рецепт'
        verbose_name_plural = 'Отмеченные рецепты'

    def __str__(self) -> str:
        return (f'{self.id} | {self.user} | '
                f'{self.fovorited_recipe.all()[:5]}')
