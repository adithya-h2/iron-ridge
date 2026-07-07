"""Delivery plan repository."""

from app.models.delivery_plan import DeliveryPlan
from app.repositories.base import BaseRepository


class DeliveryPlanRepository(BaseRepository[DeliveryPlan]):
    model = DeliveryPlan
    pk_column = "delivery_id"
