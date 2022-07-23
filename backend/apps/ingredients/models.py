from django.db import models


class Ingredient(models.Model):
    """Ингридиенты для рецепта.
    Связано с моделью Recipe через М2М (AmountIngredient).
    Attributes:
        name(str):
            Название ингридиента.
        measurement_unit(str):
            Единицы измерения ингридентов (граммы, штуки, литры и т.п.).
            Установлены ограничения по длине.
    """
    name = models.CharField(
        max_length=200,
        verbose_name='Наименование',
    )
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name='Единица измерения',
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self) -> str:
        return f'{self.name} | {self.measurement_unit}'
