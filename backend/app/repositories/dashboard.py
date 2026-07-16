"""Dashboard aggregation queries."""

from decimal import Decimal

from sqlalchemy import desc, func, select

from app.core.enums import ApprovalStatus, DealStatus, PIPELINE_ORDER
from app.models.approval import Approval
from app.models.deal import Deal
from app.models.order import Order
from app.models.quotation import Quotation
from app.repositories.base import BaseRepository


class DashboardRepository(BaseRepository):
    """Aggregation queries — no single model; uses session only."""

    model = Deal  # placeholder for BaseRepository typing

    async def count_deals_by_status(self) -> list[tuple[str, int]]:
        result = await self.session.execute(
            select(Deal.status, func.count())
            .where(Deal.status.isnot(None))
            .group_by(Deal.status)
        )
        return [(row[0], row[1]) for row in result.all()]

    async def total_deals(self) -> int:
        result = await self.session.execute(select(func.count()).select_from(Deal))
        return result.scalar_one()

    async def total_revenue(self) -> Decimal:
        result = await self.session.execute(select(func.coalesce(func.sum(Quotation.grand_total), 0)))
        return Decimal(str(result.scalar_one()))

    async def pending_approvals_count(self) -> int:
        result = await self.session.execute(
            select(func.count())
            .select_from(Approval)
            .where(Approval.decision == ApprovalStatus.PENDING.value)
        )
        return result.scalar_one()

    async def active_orders_count(self) -> int:
        result = await self.session.execute(
            select(func.count())
            .select_from(Order)
            .where(Order.order_status.notin_(["DELIVERED", "CANCELLED"]))
        )
        return result.scalar_one()

    async def count_by_current_agent(self) -> list[tuple[str, int]]:
        result = await self.session.execute(
            select(Deal.current_agent, func.count())
            .where(Deal.current_agent.isnot(None))
            .group_by(Deal.current_agent)
        )
        return [(row[0], row[1]) for row in result.all()]

    async def revenue_by_month(self) -> list[tuple[str, Decimal]]:
        month_col = func.to_char(Quotation.created_at, "YYYY-MM").label("month")
        result = await self.session.execute(
            select(month_col, func.coalesce(func.sum(Quotation.grand_total), 0))
            .where(Quotation.created_at.isnot(None))
            .group_by(month_col)
            .order_by(month_col)
        )
        return [(row[0], Decimal(str(row[1]))) for row in result.all() if row[0]]

    async def orders_by_status(self) -> list[tuple[str, int]]:
        result = await self.session.execute(
            select(Order.order_status, func.count())
            .where(Order.order_status.isnot(None))
            .group_by(Order.order_status)
        )
        return [(row[0], row[1]) for row in result.all()]

    async def recent_orders(self, limit: int = 10) -> list[Order]:
        result = await self.session.execute(
            select(Order).order_by(desc(Order.created_at)).limit(limit)
        )
        return list(result.scalars().all())

    async def approvals_by_decision(self) -> list[tuple[str, int]]:
        result = await self.session.execute(
            select(Approval.decision, func.count())
            .where(Approval.decision.isnot(None))
            .group_by(Approval.decision)
        )
        return [(row[0], row[1]) for row in result.all()]

    async def pending_approvals(self, limit: int = 20) -> list[Approval]:
        result = await self.session.execute(
            select(Approval)
            .where(Approval.decision == ApprovalStatus.PENDING.value)
            .order_by(desc(Approval.approved_at))
            .limit(limit)
        )
        return list(result.scalars().all())

    def order_pipeline_stages(self, counts: list[tuple[str, int]]) -> list[tuple[str, int]]:
        count_map = dict(counts)
        ordered = []
        for stage in PIPELINE_ORDER:
            ordered.append((stage.value, count_map.get(stage.value, 0)))
        for status, count in counts:
            if status not in [s.value for s in PIPELINE_ORDER] and status != DealStatus.REJECTED.value:
                ordered.append((status, count))
        if DealStatus.REJECTED.value in count_map:
            ordered.append((DealStatus.REJECTED.value, count_map[DealStatus.REJECTED.value]))
        return ordered
