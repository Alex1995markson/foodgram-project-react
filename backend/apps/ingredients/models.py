from django.conf.setting import СONST_LENGTH_MODEL
from django.db import models


class Ingredient(models.Model):
    """Ингридиенты для рецепта.
    Связано с моделью Recipe через М2М.
    Attributes:
        name(str):
            Название ингридиента.
            Установлены ограничения по длине и уникальности.
        measurement_unit(str):
            Единицы измерения ингридентов (граммы, штуки, литры и т.п.).
            Установлены ограничения по длине.
    """
    name = models.CharField(
        max_length=СONST_LENGTH_MODEL.MAX_LEN_RECIPES_CHARFIELD,
        verbose_name='Название ингридиента',
    )
    measurement_unit = models.CharField(
        max_length=СONST_LENGTH_MODEL.MAX_LEN_RECIPES_CHARFIELD,
        verbose_name='Единица измерения ингредиента',
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name', )

    def __str__(self) -> str:
        return f'{self.name} {self.measurement_unit}'
