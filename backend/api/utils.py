import io
import os

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

from core.constants import (FONT_SIZE_HEADER,
                            FONT_SIZE_INGREDIENTS,
                            INDENT_REGULAR
)

def generate_pdf(ingredients):
    """Создает из списка ингредиентов файл pdf с поддержкой кириллицы."""
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    _, height = letter

    current_dir = os.path.dirname(__file__)
    font_path = os.path.join(current_dir, "fonts/DejaVuSans.ttf")

    pdfmetrics.registerFont(TTFont("DejaVuSans", font_path))
    pdf.setFont("DejaVuSans", FONT_SIZE_HEADER)
    y = height - INDENT_REGULAR

    pdf.drawString(30, y, "Ваш список покупок:")
    y -= 30

    pdf.setFont("DejaVuSans", FONT_SIZE_INGREDIENTS)

    for ingredient in ingredients:
        name = ingredient.get("name")
        measurement = ingredient.get("measurement")
        amount = ingredient.get("amount")
        pdf.drawString(30, y, f"{name}: {amount} {measurement}")
        y -= 20
        if y < INDENT_REGULAR:
            pdf.showPage()
            y = height - INDENT_REGULAR

    pdf.save()
    buffer.seek(0)
    return buffer
