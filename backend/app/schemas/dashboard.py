"""Dashboard aggregation schemas."""

from decimal import Decimal

from pydantic import BaseModel


class PipelineStageCount(BaseModel):
    status: str
    count: int


class AgentActivityCount(BaseModel):
    agent: str
    count: int


class RevenueByMonth(BaseModel):
    month: str
    total: Decimal


class OrderStatusCount(BaseModel):
    status: str
    count: int


class RecentOrderSummary(BaseModel):
    order_id: str
    deal_id: str | None = None
    order_status: str | None = None
    created_at: str | None = None


class ApprovalSummaryItem(BaseModel):
    approval_id: str
    quotation_id: str | None = None
    decision: str | None = None
    approved_at: str | None = None


class DashboardSummaryResponse(BaseModel):
    total_deals: int
    deals_by_status: list[PipelineStageCount]
    total_revenue: Decimal
    pending_approvals: int
    active_orders: int


class DashboardPipelineResponse(BaseModel):
    stages: list[PipelineStageCount]


class DashboardAgentsResponse(BaseModel):
    agents: list[AgentActivityCount]


class DashboardRevenueResponse(BaseModel):
    monthly: list[RevenueByMonth]
    total: Decimal


class DashboardOrdersResponse(BaseModel):
    by_status: list[OrderStatusCount]
    recent: list[RecentOrderSummary]


class DashboardApprovalsResponse(BaseModel):
    by_decision: list[OrderStatusCount]
    pending: list[ApprovalSummaryItem]
