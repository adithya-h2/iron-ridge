"""Quotation item repository."""

from app.models.quotation_items import QuotationItem
from app.repositories.base import BaseRepository


class QuotationItemRepository(BaseRepository[QuotationItem]):
    model = QuotationItem
    pk_column = "quotation_item_id"
