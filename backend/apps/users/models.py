from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Настроенная под приложение `Foodgram` модель пользователя.
    При создании пользователя все поля обязательны для заполнения.
    Attributes:
        first_name(str):
            Реальное имя пользователя.
        last_name(str):
            Реальная фамилия пользователя.
        email(str):
            Адрес email пользователя.
            Проверка формата производится внутри Dlango.
        subscribes(int):
            Ссылки на id связанных пользователей.
    """
    first_name = models.CharField(
        max_length=50,
        verbose_name='Имя'
        )
    last_name = models.CharField(
        max_length=50,
        verbose_name='Фамилия'
    )
    email = models.EmailField(
        max_length=255,
        unique=True,
        verbose_name='Электронная почта'
    )

    subscriptions = models.ManyToManyField(
        'self',
        symmetrical=False,
        blank=True,
        verbose_name='Подписки пользователя'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [
        'username',
        'first_name',
        'last_name',
    ]
    EMAIL_FIELD = 'email'

    class Meta(AbstractUser.Meta):
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
