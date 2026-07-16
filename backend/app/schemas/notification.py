"""Notification schemas."""

from enum import StrEnum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class NotificationChannel(StrEnum):
    SLACK = "slack"
    EMAIL = "email"
    SMS = "sms"


class NotificationTemplate(StrEnum):
    LEAD_CREATED = "lead_created"
    LEAD_VALIDATED = "lead_validated"
    APPROVAL_REQUEST = "approval_request"
    APPROVAL_DECIDED = "approval_decided"
    ORDER_CREATED = "order_created"
    PIPELINE_FAILURE = "pipeline_failure"
    GENERIC = "generic"


class NotificationRequest(BaseModel):
    template: NotificationTemplate = NotificationTemplate.GENERIC
    channels: list[NotificationChannel] = Field(default_factory=lambda: [NotificationChannel.SLACK])
    deal_id: UUID | None = None
    workflow_id: UUID | None = None
    context: dict[str, Any] = Field(default_factory=dict)


class ChannelDeliveryResult(BaseModel):
    channel: NotificationChannel
    success: bool
    detail: str | None = None


class NotificationResult(BaseModel):
    template: NotificationTemplate
    deliveries: list[ChannelDeliveryResult]
