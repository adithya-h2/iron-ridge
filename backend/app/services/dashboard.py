"""Dashboard aggregation service."""

from app.repositories.dashboard import DashboardRepository
from app.schemas.dashboard import (
    AgentActivityCount,
    ApprovalSummaryItem,
    DashboardAgentsResponse,
    DashboardApprovalsResponse,
    DashboardOrdersResponse,
    DashboardPipelineResponse,
    DashboardRevenueResponse,
    DashboardSummaryResponse,
    OrderStatusCount,
    PipelineStageCount,
    RecentOrderSummary,
    RevenueByMonth,
)


class DashboardService:
    def __init__(self, dashboard_repo: DashboardRepository) -> None:
        self.dashboard_repo = dashboard_repo

    async def get_summary(self) -> DashboardSummaryResponse:
        status_counts = await self.dashboard_repo.count_deals_by_status()
        return DashboardSummaryResponse(
            total_deals=await self.dashboard_repo.total_deals(),
            deals_by_status=[
                PipelineStageCount(status=s, count=c) for s, c in status_counts
            ],
            total_revenue=await self.dashboard_repo.total_revenue(),
            pending_approvals=await self.dashboard_repo.pending_approvals_count(),
            active_orders=await self.dashboard_repo.active_orders_count(),
        )

    async def get_pipeline(self) -> DashboardPipelineResponse:
        counts = await self.dashboard_repo.count_deals_by_status()
        ordered = self.dashboard_repo.order_pipeline_stages(counts)
        return DashboardPipelineResponse(
            stages=[PipelineStageCount(status=s, count=c) for s, c in ordered]
        )

    async def get_agents(self) -> DashboardAgentsResponse:
        counts = await self.dashboard_repo.count_by_current_agent()
        return DashboardAgentsResponse(
            agents=[AgentActivityCount(agent=a, count=c) for a, c in counts]
        )

    async def get_revenue(self) -> DashboardRevenueResponse:
        from decimal import Decimal

        monthly = await self.dashboard_repo.revenue_by_month()
        total = sum((m[1] for m in monthly), Decimal("0"))
        return DashboardRevenueResponse(
            monthly=[RevenueByMonth(month=m, total=t) for m, t in monthly],
            total=total,
        )

    async def get_orders(self) -> DashboardOrdersResponse:
        by_status = await self.dashboard_repo.orders_by_status()
        recent = await self.dashboard_repo.recent_orders()
        return DashboardOrdersResponse(
            by_status=[OrderStatusCount(status=s, count=c) for s, c in by_status],
            recent=[
                RecentOrderSummary(
                    order_id=str(o.order_id),
                    deal_id=str(o.deal_id) if o.deal_id else None,
                    order_status=o.order_status,
                    created_at=o.created_at.isoformat() if o.created_at else None,
                )
                for o in recent
            ],
        )

    async def get_approvals(self) -> DashboardApprovalsResponse:
        by_decision = await self.dashboard_repo.approvals_by_decision()
        pending = await self.dashboard_repo.pending_approvals()
        return DashboardApprovalsResponse(
            by_decision=[OrderStatusCount(status=d, count=c) for d, c in by_decision],
            pending=[
                ApprovalSummaryItem(
                    approval_id=str(a.approval_id),
                    quotation_id=str(a.quotation_id) if a.quotation_id else None,
                    decision=a.decision,
                    approved_at=a.approved_at.isoformat() if a.approved_at else None,
                )
                for a in pending
            ],
        )
