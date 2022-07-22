from django.core.exceptions import ObjectDoesNotExist

from rest_framework import status
from rest_framework.response import Response


def check_the_occurrence(ckecked_obj: object,
                         related_field: str,
                         obj: object) -> bool:
    """
    Проверить вхождение объекта.

    Функция проверяет объекты находятся ли они
    в различных списках избранного пользователя.

    ------
    Note!!!!!:
        Функция используется только совместно с SerializerMethodField
        related_field допускает использование __ снитаксиса для доступа
            к другим сылочным полям.
        Ловит исключение если передано не корректное related_field
    ------
    Параметры:
        obj - обьект в котором будет произведен поиск на наличие объекта
        ckecked_obj - Проверяемый на вхождение объект
        related_field - поле в котором находятся подписки и т.д.
    ------
    Выходное значение:
        bool - находится ли обьъект в списке или нет.
    """
    try:
        user = obj.context.get('request').user
        if user.is_anonymous:
            return False
        object_for_search = user
    except AttributeError:
        object_for_search = obj

    try:
        for field in related_field.split('__'):
            object_for_search = getattr(object_for_search, field)
    except object_for_search.DoesNotExist:
        return False

    data = getattr(object_for_search, 'all')()

    return ckecked_obj in data


def send_bad_request_response(message: str) -> object:
    return Response(
        {'errors': message},
        status=status.HTTP_400_BAD_REQUEST
    )
