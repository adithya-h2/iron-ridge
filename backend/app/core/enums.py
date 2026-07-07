"""Domain enumerations for Iron Ridge backend."""

from enum import StrEnum


class DealStatus(StrEnum):
    LEAD = "LEAD"
    QUALIFICATION = "QUALIFICATION"
    QUALIFIED = "QUALIFIED"
    REQUIREMENTS = "REQUIREMENTS"
    REQUIREMENTS_COLLECTED = "REQUIREMENTS_COLLECTED"
    PRICING = "PRICING"
    PRICED = "PRICED"
    APPROVAL_PENDING = "APPROVAL_PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    ORDER_CREATED = "ORDER_CREATED"
    PRODUCTION = "PRODUCTION"
    DELIVERED = "DELIVERED"


class AgentName(StrEnum):
    MARTY = "MARTY"
    LISA = "LISA"
    NEIL = "NEIL"
    PAUL = "PAUL"
    SALLY = "SALLY"
    ADAM = "ADAM"
    VICTOR = "VICTOR"


class UserRole(StrEnum):
    ADMIN = "admin"
    SALES = "sales"
    MANAGER = "manager"
    AGENT = "agent"


class ApprovalStatus(StrEnum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


# Valid pipeline transitions: from_status -> set of allowed to_statuses
PIPELINE_TRANSITIONS: dict[DealStatus, set[DealStatus]] = {
    DealStatus.LEAD: {DealStatus.QUALIFICATION, DealStatus.REJECTED},
    DealStatus.QUALIFICATION: {DealStatus.QUALIFIED, DealStatus.REJECTED},
    DealStatus.QUALIFIED: {DealStatus.REQUIREMENTS},
    DealStatus.REQUIREMENTS: {DealStatus.REQUIREMENTS_COLLECTED},
    DealStatus.REQUIREMENTS_COLLECTED: {DealStatus.PRICING},
    DealStatus.PRICING: {DealStatus.PRICED},
    DealStatus.PRICED: {DealStatus.APPROVAL_PENDING},
    DealStatus.APPROVAL_PENDING: {DealStatus.APPROVED, DealStatus.REJECTED},
    DealStatus.APPROVED: {DealStatus.ORDER_CREATED},
    DealStatus.ORDER_CREATED: {DealStatus.PRODUCTION},
    DealStatus.PRODUCTION: {DealStatus.DELIVERED},
    DealStatus.REJECTED: set(),
    DealStatus.DELIVERED: set(),
}
