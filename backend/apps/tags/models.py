from django.core.validators import RegexValidator
from django.db import models


class Tag(models.Model):
    """Тэги для рецептов.
    Связано с моделью Recipe через М2М.
    Attributes:
        name(str):
            Название тэга.
        color(str):
            Цвет тэга в HEX-кодировке.
        slug(str):
            Те же правила, что и для атрибута `name`, но для корректной работы
            с фронтэндом следует заполнять латинскими буквами.
    Example:
        Tag('Завтрак', '#01AB89', 'breakfirst')
        Tag('Завтрак', '#01AB89', 'zavtrak')
    """
    name = models.CharField(
        max_length=200,
        unique=True,
        verbose_name='Имя тега'
    )
    color = models.CharField(
        max_length=7,
        validators=[
            RegexValidator(
                regex=r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$',
                message='Введите корректное значение HEX кода цвета')
        ],
        verbose_name='Цвет тега',
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        verbose_name='Отображаемое имя тега'
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self) -> str:
        return f'{self.name} | {self.slug}'
