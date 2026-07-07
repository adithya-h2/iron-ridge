"""Customer repository."""

from app.models.customer import Customer
from app.repositories.base import BaseRepository


class CustomerRepository(BaseRepository[Customer]):
    model = Customer
    pk_column = "customer_id"
