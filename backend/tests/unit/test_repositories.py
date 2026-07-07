"""Repository base class unit tests."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from app.repositories.base import BaseRepository
from app.models.customer import Customer


class CustomerRepo(BaseRepository[Customer]):
    model = Customer
    pk_column = "customer_id"


@pytest.fixture
def mock_session():
    session = AsyncMock()
    session.flush = AsyncMock()
    session.refresh = AsyncMock()
    return session


def test_repo_init(mock_session):
    repo = CustomerRepo(mock_session)
    assert repo.model is Customer
    assert repo.pk_column == "customer_id"
