"""FastAPI dependency injection factories."""

from typing import Annotated, Callable
from uuid import UUID

from fastapi import Depends, Header, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.adam import AdamAgent
from app.agents.llm_client import LLMClient
from app.agents.lisa import LisaAgent
from app.agents.marty import MartyAgent
from app.agents.neil import NeilAgent
from app.agents.paul import PaulAgent
from app.agents.sally import SallyAgent
from app.core.config import settings
from app.core.enums import UserRole
from app.core.exceptions import ForbiddenError, UnauthorizedError
from app.core.security import decode_access_token
from app.database.session import get_db_session
from app.repositories.agent_memory import AgentMemoryRepository
from app.repositories.approval import ApprovalRepository
from app.repositories.audit_log import AuditLogRepository
from app.repositories.bom import BOMRepository
from app.repositories.bom_item import BOMItemRepository
from app.repositories.customer import CustomerRepository
from app.repositories.deal import DealRepository
from app.repositories.delivery_plan import DeliveryPlanRepository
from app.repositories.discount_master import DiscountMasterRepository
from app.repositories.lead_validation import LeadValidationRepository
from app.repositories.order import OrderRepository
from app.repositories.price_master import PriceMasterRepository
from app.repositories.quotation import QuotationRepository
from app.repositories.quotation_item import QuotationItemRepository
from app.repositories.requirement import RequirementRepository
from app.repositories.user import UserRepository
from app.repositories.vehicle_master import VehicleMasterRepository
from app.schemas.auth import UserResponse
from app.services.agent_orchestrator import AgentOrchestrator
from app.services.approval import ApprovalService
from app.services.audit import AuditService
from app.services.auth import AuthService
from app.services.customer import CustomerService
from app.services.deal import DealService
from app.services.order import OrderService
from app.services.pipeline import PipelineService
from app.services.pricing import PricingService
from app.services.slack import SlackService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)


async def get_audit_service(db: AsyncSession = Depends(get_db_session)) -> AuditService:
    return AuditService(AuditLogRepository(db))


async def get_pipeline_service(
    db: AsyncSession = Depends(get_db_session),
    audit_service: AuditService = Depends(get_audit_service),
) -> PipelineService:
    return PipelineService(DealRepository(db), audit_service)


async def get_customer_service(db: AsyncSession = Depends(get_db_session)) -> CustomerService:
    return CustomerService(CustomerRepository(db))


async def get_deal_service(
    db: AsyncSession = Depends(get_db_session),
    audit_service: AuditService = Depends(get_audit_service),
    pipeline_service: PipelineService = Depends(get_pipeline_service),
) -> DealService:
    return DealService(DealRepository(db), audit_service, pipeline_service)


async def get_pricing_service(db: AsyncSession = Depends(get_db_session)) -> PricingService:
    return PricingService(
        QuotationRepository(db),
        QuotationItemRepository(db),
        BOMRepository(db),
        BOMItemRepository(db),
        PriceMasterRepository(db),
        DiscountMasterRepository(db),
        VehicleMasterRepository(db),
    )


async def get_approval_service(
    db: AsyncSession = Depends(get_db_session),
    audit_service: AuditService = Depends(get_audit_service),
    pipeline_service: PipelineService = Depends(get_pipeline_service),
) -> ApprovalService:
    return ApprovalService(
        ApprovalRepository(db),
        QuotationRepository(db),
        pipeline_service,
        audit_service,
    )


async def get_order_service(db: AsyncSession = Depends(get_db_session)) -> OrderService:
    return OrderService(OrderRepository(db), DeliveryPlanRepository(db))


async def get_auth_service(db: AsyncSession = Depends(get_db_session)) -> AuthService:
    return AuthService(UserRepository(db))


async def get_slack_service(
    db: AsyncSession = Depends(get_db_session),
    approval_service: ApprovalService = Depends(get_approval_service),
) -> SlackService:
    return SlackService(ApprovalRepository(db), QuotationRepository(db), approval_service)


async def get_agent_orchestrator(
    db: AsyncSession = Depends(get_db_session),
    audit_service: AuditService = Depends(get_audit_service),
    pipeline_service: PipelineService = Depends(get_pipeline_service),
    pricing_service: PricingService = Depends(get_pricing_service),
    approval_service: ApprovalService = Depends(get_approval_service),
    order_service: OrderService = Depends(get_order_service),
) -> AgentOrchestrator:
    llm = LLMClient()
    memory_repo = AgentMemoryRepository(db)
    return AgentOrchestrator(
        marty=MartyAgent(llm, memory_repo, audit_service, CustomerRepository(db), DealRepository(db)),
        lisa=LisaAgent(llm, memory_repo, audit_service, DealRepository(db), LeadValidationRepository(db), pipeline_service),
        neil=NeilAgent(llm, memory_repo, audit_service, RequirementRepository(db), pipeline_service),
        paul=PaulAgent(llm, memory_repo, audit_service, pricing_service, pipeline_service, approval_service),
        sally=SallyAgent(llm, memory_repo, audit_service, order_service, pipeline_service),
        adam=AdamAgent(llm, memory_repo, audit_service, order_service, pipeline_service),
    )


async def get_current_user(
    request: Request,
    token: Annotated[str | None, Depends(oauth2_scheme)] = None,
    x_api_key: Annotated[str | None, Header()] = None,
    db: AsyncSession = Depends(get_db_session),
) -> UserResponse | None:
    if x_api_key and settings.agent_api_key and x_api_key == settings.agent_api_key:
        request.state.agent_name = "n8n"
        return UserResponse(
            user_id=UUID("00000000-0000-0000-0000-000000000001"),
            email="agent@ironridge.com",
            role=UserRole.AGENT.value,
            is_active=True,
        )
    if not token:
        return None
    payload = decode_access_token(token)
    user_id = UUID(payload["user_id"])
    auth_service = AuthService(UserRepository(db))
    user = await auth_service.get_user(user_id)
    request.state.user_email = user.email
    return user


def require_auth(user: UserResponse | None = Depends(get_current_user)) -> UserResponse:
    if user is None:
        raise UnauthorizedError("Authentication required")
    return user


def require_roles(*roles: UserRole) -> Callable:
    async def _checker(user: UserResponse = Depends(require_auth)) -> UserResponse:
        if user.role not in [r.value for r in roles] and user.role != UserRole.ADMIN.value:
            raise ForbiddenError(f"Requires one of roles: {[r.value for r in roles]}")
        return user

    return _checker
