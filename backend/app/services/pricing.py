"""Pricing and quotation service."""

from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID

from app.repositories.bom import BOMRepository
from app.repositories.bom_item import BOMItemRepository
from app.repositories.discount_master import DiscountMasterRepository
from app.repositories.price_master import PriceMasterRepository
from app.repositories.quotation import QuotationRepository
from app.repositories.quotation_item import QuotationItemRepository
from app.repositories.vehicle_master import VehicleMasterRepository
from app.schemas.quotation import QuotationCreate, QuotationResponse


class PricingService:
    TAX_RATE = Decimal("0.08")

    def __init__(
        self,
        quotation_repo: QuotationRepository,
        quotation_item_repo: QuotationItemRepository,
        bom_repo: BOMRepository,
        bom_item_repo: BOMItemRepository,
        price_master_repo: PriceMasterRepository,
        discount_master_repo: DiscountMasterRepository,
        vehicle_master_repo: VehicleMasterRepository,
    ) -> None:
        self.quotation_repo = quotation_repo
        self.quotation_item_repo = quotation_item_repo
        self.bom_repo = bom_repo
        self.bom_item_repo = bom_item_repo
        self.price_master_repo = price_master_repo
        self.discount_master_repo = discount_master_repo
        self.vehicle_master_repo = vehicle_master_repo

    async def generate_quotation(
        self,
        deal_id: UUID,
        vehicle_type: str,
        quantity: int,
    ) -> QuotationResponse:
        vehicle = await self.vehicle_master_repo.get_by_name_or_type(vehicle_type)
        base_price = vehicle.base_price if vehicle and vehicle.base_price else Decimal("250000")
        unit_price = Decimal(str(base_price))
        subtotal = unit_price * quantity

        discount_pct = Decimal("0")
        discounts = await self.discount_master_repo.get_all()
        for d in discounts.items:
            min_q = d.minimum_quantity or 0
            max_q = d.maximum_quantity or 999999
            if min_q <= quantity <= max_q and d.discount_percentage:
                discount_pct = max(discount_pct, Decimal(str(d.discount_percentage)))

        discount_amount = subtotal * discount_pct / Decimal("100")
        taxable = subtotal - discount_amount
        tax = taxable * self.TAX_RATE
        grand_total = taxable + tax
        now = datetime.now(timezone.utc).replace(tzinfo=None)

        if vehicle:
            bom = await self.bom_repo.create(
                deal_id=deal_id,
                vehicle_id=vehicle.vehicle_id,
                total_cost=subtotal,
                margin=Decimal("15"),
                generated_at=now,
            )
            await self.bom_item_repo.create(
                bom_id=bom.bom_id,
                component_name=vehicle.vehicle_name or vehicle_type,
                component_type=vehicle.category,
                quantity=quantity,
                unit_price=unit_price,
                subtotal=subtotal,
            )

        quotation = await self.quotation_repo.create(
            deal_id=deal_id,
            quotation_version="1.0",
            subtotal=subtotal,
            discount=discount_amount,
            tax=tax,
            grand_total=grand_total,
            quotation_status="DRAFT",
            created_at=now,
        )
        await self.quotation_item_repo.create(
            quotation_id=quotation.quotation_id,
            component_name=vehicle_type,
            quantity=quantity,
            unit_price=unit_price,
            discount=discount_amount,
            total=grand_total,
        )
        return QuotationResponse.model_validate(quotation)

    async def get(self, quotation_id: UUID) -> QuotationResponse:
        q = await self.quotation_repo.get_by_id_or_raise(quotation_id)
        return QuotationResponse.model_validate(q)

    async def create(self, data: QuotationCreate) -> QuotationResponse:
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        q = await self.quotation_repo.create(
            **data.model_dump(exclude={"items"}, exclude_unset=True),
            created_at=now,
        )
        for item in data.items:
            await self.quotation_item_repo.create(quotation_id=q.quotation_id, **item.model_dump())
        return QuotationResponse.model_validate(q)
