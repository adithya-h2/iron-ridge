"""Quotation PDF generation using reportlab."""

import io
from decimal import Decimal

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

from app.core.config import settings
from app.schemas.quotation import QuotationResponse


class QuotationPdfService:
    def generate(
        self,
        quotation: QuotationResponse,
        company_name: str | None = None,
    ) -> bytes:
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter
        y = height - inch

        c.setFont("Helvetica-Bold", 16)
        c.drawString(inch, y, settings.pdf_company_name)
        y -= 0.25 * inch
        c.setFont("Helvetica", 10)
        c.drawString(inch, y, settings.pdf_company_address)
        y -= 0.5 * inch

        c.setFont("Helvetica-Bold", 14)
        c.drawString(inch, y, "Quotation")
        y -= 0.35 * inch
        c.setFont("Helvetica", 11)
        c.drawString(inch, y, f"Quotation ID: {quotation.quotation_id}")
        y -= 0.2 * inch
        if quotation.deal_id:
            c.drawString(inch, y, f"Deal ID: {quotation.deal_id}")
            y -= 0.2 * inch
        if company_name:
            c.drawString(inch, y, f"Customer: {company_name}")
            y -= 0.2 * inch
        if quotation.created_at:
            c.drawString(inch, y, f"Date: {quotation.created_at.strftime('%Y-%m-%d')}")
            y -= 0.4 * inch

        c.setFont("Helvetica-Bold", 11)
        c.drawString(inch, y, "Line Items")
        y -= 0.25 * inch
        c.setFont("Helvetica", 10)
        for item in quotation.items:
            line = (
                f"{item.component_name or 'Item'} x{item.quantity or 1} "
                f"@ {_fmt(item.unit_price)} = {_fmt(item.total)}"
            )
            c.drawString(inch, y, line[:90])
            y -= 0.2 * inch
            if y < inch:
                c.showPage()
                y = height - inch

        y -= 0.2 * inch
        c.drawString(inch, y, f"Subtotal: {_fmt(quotation.subtotal)}")
        y -= 0.2 * inch
        c.drawString(inch, y, f"Discount: {_fmt(quotation.discount)}")
        y -= 0.2 * inch
        c.drawString(inch, y, f"Tax: {_fmt(quotation.tax)}")
        y -= 0.25 * inch
        c.setFont("Helvetica-Bold", 12)
        c.drawString(inch, y, f"Grand Total: {_fmt(quotation.grand_total)}")

        c.showPage()
        c.save()
        return buffer.getvalue()


def _fmt(value: Decimal | None) -> str:
    if value is None:
        return "$0.00"
    return f"${Decimal(value):,.2f}"
