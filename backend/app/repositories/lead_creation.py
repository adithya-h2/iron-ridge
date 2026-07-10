"""Atomic customer + deal creation for lead intake."""

from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import AgentName, DealStatus, LeadSource
from app.models.customer import Customer
from app.models.deal import Deal
from app.schemas.lead import LeadCreationResult, NormalizedLead


class LeadCreationRepository:
    """Persists customer and deal in a single session transaction."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_lead(
        self,
        lead: NormalizedLead,
        workflow_id: UUID,
        existing_customer_id: UUID | None = None,
    ) -> LeadCreationResult:
        now = datetime.now(timezone.utc).replace(tzinfo=None)

        if existing_customer_id:
            customer_id = existing_customer_id
        else:
            customer = Customer(
                company_name=lead.company_name,
                contact_person=lead.contact_person,
                email=lead.email,
                phone=lead.phone,
                website=lead.website,
                city=lead.city,
                state=lead.state,
                country=lead.country,
                industry=lead.industry or "Healthcare",
                created_at=now,
                updated_at=now,
            )
            self.session.add(customer)
            await self.session.flush()
            await self.session.refresh(customer)
            customer_id = customer.customer_id

        deal = Deal(
            customer_id=customer_id,
            status=DealStatus.LEAD.value,
            current_agent=AgentName.MARTY.value,
            lead_source=lead.source.value if isinstance(lead.source, LeadSource) else str(lead.source),
            workflow_id=workflow_id,
            submission_channel=lead.submission_channel,
            created_at=now,
            updated_at=now,
        )
        self.session.add(deal)
        await self.session.flush()
        await self.session.refresh(deal)

        return LeadCreationResult(
            customer_id=customer_id,
            deal_id=deal.deal_id,
            workflow_id=workflow_id,
            lead_source=deal.lead_source or lead.source.value,
            submission_channel=lead.submission_channel,
            status=DealStatus.LEAD.value,
        )

    @staticmethod
    def new_workflow_id() -> UUID:
        return uuid4()
