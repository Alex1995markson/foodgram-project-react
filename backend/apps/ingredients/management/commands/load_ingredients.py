"""Загрузка ингредиентов в базу данных.

Определена дополнительная django команда ./manage.py load_ingredients.
Необходима для загрузки даннах из файла data/ingredients.csv
(содержитсписок ингредиентов проекта) в базу данных проекта.
Используется при сборке docker образа.

Использование:
    Cоздать структура проекта ввида:
        project
        |______backend(этот проект)
        |
        |______data/ingredients.csv

    Cтуктура файла ingredients.csv:
        product_name,measurement_unit

    Команда запуска:
        ./manage.py load_ingredients
"""
import csv

from django.core.management.base import BaseCommand

from ingredients.models import Ingredient


class Command(BaseCommand):
    help = 'Загругзка тестовых данных'

    def handle(self, *args, **kwargs) -> None:
        if self._is_empty_data_base():
            self._record_data_in_db('../data/ingredients.csv')

    def _is_empty_data_base(self) -> bool:
        """Проверить заполненость таблицы ингредиентов в базе данных."""
        return False if Ingredient.objects.all().count() else True

    def _record_data_in_db(self, file_path: str) -> None:
        """Записать данные в таблицу ингридиентов."""
        with open(file_path, newline='') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                name, measurement_unit = row
                Ingredient.objects.create(
                    name=name,
                    measurement_unit=measurement_unit
                )
