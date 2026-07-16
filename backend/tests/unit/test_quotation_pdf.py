"""Quotation PDF generation tests."""

from decimal import Decimal
from uuid import uuid4

from app.schemas.quotation import QuotationItemResponse, QuotationResponse
from app.services.quotation_pdf import QuotationPdfService


def test_generate_pdf_returns_valid_bytes():
    quotation_id = uuid4()
    quotation = QuotationResponse(
        quotation_id=quotation_id,
        deal_id=uuid4(),
        subtotal=Decimal("250000"),
        discount=Decimal("0"),
        tax=Decimal("20000"),
        grand_total=Decimal("270000"),
        items=[
            QuotationItemResponse(
                quotation_item_id=uuid4(),
                quotation_id=quotation_id,
                component_name="Ambulance",
                quantity=1,
                unit_price=Decimal("250000"),
                total=Decimal("270000"),
            )
        ],
    )
    pdf_bytes = QuotationPdfService().generate(quotation, "City Fire Dept")
    assert pdf_bytes.startswith(b"%PDF")
    assert len(pdf_bytes) > 100
