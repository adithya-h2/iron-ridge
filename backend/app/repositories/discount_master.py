"""Discount master repository."""

from app.models.discount_master import DiscountMaster
from app.repositories.base import BaseRepository


class DiscountMasterRepository(BaseRepository[DiscountMaster]):
    model = DiscountMaster
    pk_column = "discount_id"
