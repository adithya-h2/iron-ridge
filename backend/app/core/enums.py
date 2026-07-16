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


class LeadSource(StrEnum):
    WEBSITE = "WEBSITE"
    DASHBOARD = "DASHBOARD"
    API = "API"
    EMAIL = "EMAIL"
    CSV = "CSV"
    WHATSAPP = "WHATSAPP"
    VOICE = "VOICE"
    TRADE_SHOW = "TRADE_SHOW"
    PHONE = "PHONE"
    OTHER = "OTHER"


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

# Ordered pipeline stages for progress calculation (excludes REJECTED terminal)
PIPELINE_ORDER: list[DealStatus] = [
    DealStatus.LEAD,
    DealStatus.QUALIFICATION,
    DealStatus.QUALIFIED,
    DealStatus.REQUIREMENTS,
    DealStatus.REQUIREMENTS_COLLECTED,
    DealStatus.PRICING,
    DealStatus.PRICED,
    DealStatus.APPROVAL_PENDING,
    DealStatus.APPROVED,
    DealStatus.ORDER_CREATED,
    DealStatus.PRODUCTION,
    DealStatus.DELIVERED,
]


def pipeline_progress_percentage(status: str | None) -> int:
    """Compute workflow progress (0-100) from deal status."""
    if not status:
        return 0
    if status == DealStatus.DELIVERED.value:
        return 100
    if status == DealStatus.REJECTED.value:
        return 0
    try:
        current = DealStatus(status)
    except ValueError:
        return 0
    if current not in PIPELINE_ORDER:
        return 0
    index = PIPELINE_ORDER.index(current)
    return round((index + 1) / len(PIPELINE_ORDER) * 100)
