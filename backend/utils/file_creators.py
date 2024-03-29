import io
from typing import Dict

import reportlab
from django.conf import settings
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


def create_ingredients_list_pdf(ingredients: Dict[str, int]):
    """Создать пдф файл со списком ингредиентов.

     Формирует файл(pdf) на онсове ingredients.

        ------
        Параметры:
               ingredients:  Dict[str, int] - словарь ингредиентов ввида:
                {имя (единица измерения): колличество}
        -----
        Выходное значение:
            указатель на буфер с фалом
    """
    reportlab.rl_config.TTFSearchPath.append(
        str(settings.BASE_DIR) + '/utils/fonts/'
    )
    pdfmetrics.registerFont(TTFont('Roboto', 'Roboto.ttf'))

    buffer = io.BytesIO()
    p = canvas.Canvas(
        buffer,
        pagesize=A4,
        initialFontName='Roboto',
        initialFontSize=18
    )

    margin_top = 27 * cm
    margint_top_header = margin_top - 3 * cm
    left_margin = 1 * cm

    p.drawString(6.5 * cm, margin_top, 'Общий список ингредиентов!')
    p.setFontSize(16)

    page_spliter = 0
    for ingredient, amount in ingredients.items():
        p.drawString(
            left_margin,
            margint_top_header,
            f'{ingredient} - {amount}'
        )
        margint_top_header -= cm
        page_spliter += 1

        if page_spliter % 24 == 0:
            p.showPage()
            p.drawString(3 * cm, margin_top, 'Продолжение списка ингредиентов')
            margint_top_header = margin_top - 3 * cm

    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer
