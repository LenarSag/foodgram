import io
import os

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics


def generate_pdf(ingredients):
    """Создает из списка ингредиентов файл pdf с поддержкой кириллицы."""
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    _, height = letter

    current_dir = os.path.dirname(__file__)
    font_path = os.path.join(current_dir, "fonts/DejaVuSans.ttf")

    pdfmetrics.registerFont(TTFont("DejaVuSans", font_path))
    pdf.setFont("DejaVuSans", 16)
    y = height - 40

    pdf.drawString(30, y, "Ваш список покупок:")
    y -= 30

    pdf.setFont("DejaVuSans", 10)

    for ingredient in ingredients:
        name = ingredient.get("name")
        measurement = ingredient.get("measurement")
        amount = ingredient.get("amount")
        pdf.drawString(30, y, f"{name}: {amount} {measurement}")
        y -= 20
        if y < 40:
            pdf.showPage()
            y = height - 40

    pdf.save()
    buffer.seek(0)
    return buffer
