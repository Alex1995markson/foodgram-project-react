from django.conf.setting import СONST_LENGTH_MODEL
from django.db import models


class Tag(models.Model):
    name = models.CharField(
        max_length=СONST_LENGTH_MODEL.MAX_LEN_RECIPES_CHARFIELD,
        unique=True,
        verbose_name='Тег'
    )
    color = models.CharField(
        verbose_name='Цветовой HEX-код',
        max_length=6,
        blank=True,
        null=True,
        default='FF',
    )
    slug = models.SlugField(
        max_length=СONST_LENGTH_MODEL.MAX_LEN_RECIPES_CHARFIELD,
        unique=True,
        verbose_name='Слаг тэга'
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('name', )

    def __str__(self) -> str:
        return f'{self.name} {self.slug}'
