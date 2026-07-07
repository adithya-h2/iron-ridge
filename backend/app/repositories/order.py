"""Order repository."""

from app.models.order import Order
from app.repositories.base import BaseRepository


class OrderRepository(BaseRepository[Order]):
    model = Order
    pk_column = "order_id"
