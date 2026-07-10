"""Duplicate customer detection for lead intake."""

from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import or_, select

from app.models.customer import Customer
from app.repositories.customer import CustomerRepository
from app.schemas.lead import NormalizedLead


@dataclass
class DuplicateMatch:
    customer_id: UUID
    match_reason: str


class DuplicateDetectionService:
    def __init__(self, customer_repo: CustomerRepository) -> None:
        self.customer_repo = customer_repo

    async def find_duplicate(self, lead: NormalizedLead) -> DuplicateMatch | None:
        conditions = []
        if lead.email:
            conditions.append(Customer.email.ilike(lead.email))
        if lead.phone:
            conditions.append(Customer.phone == lead.phone)
        if lead.company_name:
            conditions.append(Customer.company_name.ilike(lead.company_name))

        if not conditions:
            return None

        result = await self.customer_repo.session.execute(
            select(Customer).where(or_(*conditions)).limit(1)
        )
        existing = result.scalar_one_or_none()
        if existing is None:
            return None

        reason = "company_name"
        if lead.email and existing.email and existing.email.lower() == lead.email.lower():
            reason = "email"
        elif lead.phone and existing.phone == lead.phone:
            reason = "phone"

        return DuplicateMatch(customer_id=existing.customer_id, match_reason=reason)
