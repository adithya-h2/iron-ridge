"""Quotation repository."""

from app.models.quotation import Quotation
from app.repositories.base import BaseRepository


class QuotationRepository(BaseRepository[Quotation]):
    model = Quotation
    pk_column = "quotation_id"
