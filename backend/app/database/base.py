"""
app/database/base.py

Single import point for the SQLAlchemy declarative Base and ALL models.

Purpose:
    Alembic's env.py imports Base.metadata from here.
    Every model must be imported in this file so SQLAlchemy registers
    all table definitions with Base.metadata before Alembic reads it.

    THIS IS THE ONLY FILE alembic/env.py should import from.

Tables registered (all 16 from deployed Supabase schema):
    customers, deals, lead_validation, requirements,
    vehicle_master, bom, bom_items, price_master,
    discount_master, quotations, quotation_items,
    approvals, orders, delivery_plan, agent_memory, audit_logs
"""

from app.database.database import Base  # noqa: F401 — re-export for Alembic

# ---------------------------------------------------------------------------
# Import all models so SQLAlchemy registers them with Base.metadata.
# Order matters for forward references — parents before children.
# ---------------------------------------------------------------------------

from app.models.customer import Customer              # noqa: F401
from app.models.deal import Deal                      # noqa: F401
from app.models.lead_validation import LeadValidation # noqa: F401
from app.models.requirement import Requirement        # noqa: F401
from app.models.vehicle_master import VehicleMaster   # noqa: F401
from app.models.bom import BOM                        # noqa: F401
from app.models.bom_items import BOMItem              # noqa: F401
from app.models.price_master import PriceMaster       # noqa: F401
from app.models.discount_master import DiscountMaster # noqa: F401
from app.models.quotation import Quotation            # noqa: F401
from app.models.quotation_items import QuotationItem  # noqa: F401
from app.models.approval import Approval              # noqa: F401
from app.models.order import Order                    # noqa: F401
from app.models.delivery_plan import DeliveryPlan     # noqa: F401
from app.models.agent_memory import AgentMemory       # noqa: F401
from app.models.audit_log import AuditLog             # noqa: F401
