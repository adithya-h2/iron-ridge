"""Customer business service."""

from datetime import datetime, timezone
from uuid import UUID

from app.repositories.customer import CustomerRepository
from app.schemas.common import PaginatedResponse, PaginationParams
from app.schemas.customer import CustomerCreate, CustomerResponse, CustomerUpdate


class CustomerService:
    def __init__(self, customer_repo: CustomerRepository) -> None:
        self.customer_repo = customer_repo

    async def create(self, data: CustomerCreate) -> CustomerResponse:
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        customer = await self.customer_repo.create(
            **data.model_dump(exclude_unset=True),
            created_at=now,
            updated_at=now,
        )
        return CustomerResponse.model_validate(customer)

    async def get(self, customer_id: UUID) -> CustomerResponse:
        customer = await self.customer_repo.get_by_id_or_raise(customer_id)
        return CustomerResponse.model_validate(customer)

    async def list(
        self, pagination: PaginationParams | None = None
    ) -> PaginatedResponse[CustomerResponse]:
        result = await self.customer_repo.get_all(pagination)
        return PaginatedResponse(
            items=[CustomerResponse.model_validate(i) for i in result.items],
            total=result.total,
            page=result.page,
            page_size=result.page_size,
            pages=result.pages,
        )

    async def search(
        self, term: str, pagination: PaginationParams | None = None
    ) -> PaginatedResponse[CustomerResponse]:
        result = await self.customer_repo.search(
            term, ["company_name", "email", "city", "country"], pagination
        )
        return PaginatedResponse(
            items=[CustomerResponse.model_validate(i) for i in result.items],
            total=result.total,
            page=result.page,
            page_size=result.page_size,
            pages=result.pages,
        )

    async def update(self, customer_id: UUID, data: CustomerUpdate) -> CustomerResponse:
        customer = await self.customer_repo.update(
            customer_id,
            **data.model_dump(exclude_unset=True),
            updated_at=datetime.now(timezone.utc).replace(tzinfo=None),
        )
        return CustomerResponse.model_validate(customer)

    async def delete(self, customer_id: UUID) -> None:
        await self.customer_repo.delete(customer_id)
