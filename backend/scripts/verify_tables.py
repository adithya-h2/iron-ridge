"""Verify required tables exist (Phase 3)."""
import asyncio
import sys

sys.path.insert(0, ".")

from sqlalchemy import text
from app.database.session import AsyncSessionFactory

TABLES = [
    "customers",
    "deals",
    "lead_validation",
    "requirements",
    "quotations",
    "quotation_items",
    "approvals",
    "orders",
    "delivery_plan",
    "agent_memory",
    "audit_logs",
    "workflow_execution_state",
]


async def main() -> None:
    async with AsyncSessionFactory() as session:
        for table in TABLES:
            r = await session.execute(
                text(
                    "SELECT EXISTS (SELECT 1 FROM information_schema.tables "
                    "WHERE table_schema = 'public' AND table_name = :t)"
                ),
                {"t": table},
            )
            exists = r.scalar()
            print(f"{table}: {'OK' if exists else 'MISSING'}")


if __name__ == "__main__":
    asyncio.run(main())
