"""Order business service."""

from datetime import date, datetime, timezone
from uuid import UUID

from app.repositories.delivery_plan import DeliveryPlanRepository
from app.repositories.order import OrderRepository
from app.schemas.order import OrderCreate, OrderResponse, OrderUpdate


class OrderService:
    def __init__(
        self,
        order_repo: OrderRepository,
        delivery_plan_repo: DeliveryPlanRepository,
    ) -> None:
        self.order_repo = order_repo
        self.delivery_plan_repo = delivery_plan_repo

    async def create(self, data: OrderCreate) -> OrderResponse:
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        order = await self.order_repo.create(
            **data.model_dump(exclude_unset=True),
            created_at=now,
        )
        return OrderResponse.model_validate(order)

    async def get(self, order_id: UUID) -> OrderResponse:
        order = await self.order_repo.get_by_id_or_raise(order_id)
        return OrderResponse.model_validate(order)

    async def update(self, order_id: UUID, data: OrderUpdate) -> OrderResponse:
        order = await self.order_repo.update(order_id, **data.model_dump(exclude_unset=True))
        return OrderResponse.model_validate(order)

    async def create_from_quotation(
        self, deal_id: UUID, quotation_id: UUID
    ) -> OrderResponse:
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        order = await self.order_repo.create(
            deal_id=deal_id,
            quotation_id=quotation_id,
            order_status="CONFIRMED",
            erp_reference=f"ERP-{deal_id.hex[:8].upper()}",
            production_start=date.today(),
            created_at=now,
        )
        return OrderResponse.model_validate(order)

    async def create_delivery_plan(
        self,
        order_id: UUID,
        delivery_month: str,
        planned_quantity: int,
        planned_date: date | None = None,
    ) -> None:
        await self.delivery_plan_repo.create(
            order_id=order_id,
            delivery_month=delivery_month,
            planned_quantity=planned_quantity,
            planned_date=planned_date or date.today(),
            delivery_status="PLANNED",
        )
