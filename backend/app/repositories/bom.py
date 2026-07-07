"""BOM repository."""

from app.models.bom import BOM
from app.repositories.base import BaseRepository


class BOMRepository(BaseRepository[BOM]):
    model = BOM
    pk_column = "bom_id"
