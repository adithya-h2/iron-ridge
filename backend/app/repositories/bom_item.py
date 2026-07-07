"""BOM item repository."""

from app.models.bom_items import BOMItem
from app.repositories.base import BaseRepository


class BOMItemRepository(BaseRepository[BOMItem]):
    model = BOMItem
    pk_column = "item_id"
