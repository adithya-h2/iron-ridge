"""Price master repository."""

from app.models.price_master import PriceMaster
from app.repositories.base import BaseRepository


class PriceMasterRepository(BaseRepository[PriceMaster]):
    model = PriceMaster
    pk_column = "price_id"
