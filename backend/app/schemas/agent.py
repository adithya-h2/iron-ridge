"""Agent execution Pydantic schemas."""

from pydantic import BaseModel, ConfigDict, Field


class AgentExecuteRequest(BaseModel):
    """JSON body for agent execution."""

    deal_id: str | None = None
    org_name: str | None = None
    vehicle_type: str | None = None
    required_quantity: int | str | None = None
    city: str | None = None
    country: str | None = None
    lead_score: int | str | None = None
    requirements: str | None = None
    quotation_id: str | None = None
    approval_status: str | None = None
    order_id: str | None = None
    customer_name: str | None = None

    model_config = ConfigDict(extra="allow")


class AgentExecuteResponse(BaseModel):
    deal_id: str | None = None
    status: str | None = None
    current_agent: str | None = None
    lead_score: int | None = None
    qualified: bool | None = None
    quotation_id: str | None = None
    quotation_generated: str | None = None
    order_id: str | None = None
    approval_status: str | None = None
    requirements: str | None = None
    reason: str | None = None
    org_name: str | None = None

    model_config = ConfigDict(extra="allow")
