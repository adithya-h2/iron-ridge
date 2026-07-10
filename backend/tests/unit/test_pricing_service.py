"""PricingService quotation serialization tests."""

from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.services.pricing import PricingService


def _make_service(quotation_repo: AsyncMock) -> PricingService:
    return PricingService(
        quotation_repo,
        AsyncMock(),
        AsyncMock(),
        AsyncMock(),
        AsyncMock(),
        AsyncMock(),
        AsyncMock(),
    )


@pytest.mark.asyncio
async def test_to_response_eager_loads_items_before_validation():
    quotation_id = uuid4()
    item = MagicMock()
    item.quotation_item_id = uuid4()
    item.quotation_id = quotation_id
    item.component_name = "Ambulance"
    item.quantity = 1
    item.unit_price = Decimal("250000")
    item.discount = Decimal("0")
    item.total = Decimal("270000")

    quotation = MagicMock()
    quotation.quotation_id = quotation_id
    quotation.deal_id = uuid4()
    quotation.quotation_version = "1.0"
    quotation.subtotal = Decimal("250000")
    quotation.discount = Decimal("0")
    quotation.tax = Decimal("20000")
    quotation.grand_total = Decimal("270000")
    quotation.quotation_status = "DRAFT"
    quotation.created_at = None
    quotation.items = [item]

    quotation_repo = AsyncMock()
    quotation_repo.get_with_items_or_raise = AsyncMock(return_value=quotation)

    service = _make_service(quotation_repo)
    response = await service._to_response(quotation_id)

    quotation_repo.get_with_items_or_raise.assert_awaited_once_with(quotation_id)
    assert response.quotation_id == quotation_id
    assert len(response.items) == 1
    assert response.items[0].component_name == "Ambulance"


@pytest.mark.asyncio
async def test_generate_quotation_returns_response_via_eager_load():
    deal_id = uuid4()
    quotation_id = uuid4()

    vehicle = MagicMock()
    vehicle.vehicle_id = uuid4()
    vehicle.base_price = Decimal("250000")
    vehicle.vehicle_name = "Type III Ambulance"
    vehicle.category = "Ambulance"

    created_quotation = MagicMock()
    created_quotation.quotation_id = quotation_id

    loaded_quotation = MagicMock()
    loaded_quotation.quotation_id = quotation_id
    loaded_quotation.deal_id = deal_id
    loaded_quotation.quotation_version = "1.0"
    loaded_quotation.subtotal = Decimal("250000")
    loaded_quotation.discount = Decimal("0")
    loaded_quotation.tax = Decimal("20000")
    loaded_quotation.grand_total = Decimal("270000")
    loaded_quotation.quotation_status = "DRAFT"
    loaded_quotation.created_at = None
    loaded_quotation.items = [
        MagicMock(
            quotation_item_id=uuid4(),
            quotation_id=quotation_id,
            component_name="Ambulance",
            quantity=1,
            unit_price=Decimal("250000"),
            discount=Decimal("0"),
            total=Decimal("270000"),
        )
    ]

    quotation_repo = AsyncMock()
    quotation_repo.create = AsyncMock(return_value=created_quotation)
    quotation_repo.get_with_items_or_raise = AsyncMock(return_value=loaded_quotation)

    bom_repo = AsyncMock()
    bom_repo.create = AsyncMock(return_value=MagicMock(bom_id=uuid4()))

    service = PricingService(
        quotation_repo,
        AsyncMock(),
        bom_repo,
        AsyncMock(),
        AsyncMock(),
        AsyncMock(),
        AsyncMock(get_by_name_or_type=AsyncMock(return_value=vehicle)),
    )
    service.discount_master_repo.get_all = AsyncMock(return_value=MagicMock(items=[]))

    response = await service.generate_quotation(deal_id, "Ambulance", 1)

    quotation_repo.get_with_items_or_raise.assert_awaited_once_with(quotation_id)
    assert response.quotation_id == quotation_id
    assert len(response.items) == 1
