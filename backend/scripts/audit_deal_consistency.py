"""Database consistency audit for a deal (Phase 14)."""
import asyncio
import sys

sys.path.insert(0, ".")

from sqlalchemy import text
from app.database.session import AsyncSessionFactory


async def audit_deal(deal_id: str) -> None:
    async with AsyncSessionFactory() as session:
        deal = (
            await session.execute(
                text("SELECT * FROM deals WHERE deal_id = :d"), {"d": deal_id}
            )
        ).mappings().first()
        print("DEAL:", dict(deal) if deal else None)

        for table, col in [
            ("lead_validation", "deal_id"),
            ("requirements", "deal_id"),
            ("quotations", "deal_id"),
            ("approvals", "quotation_id"),
            ("orders", "deal_id"),
            ("delivery_plan", "deal_id"),
            ("audit_logs", "deal_id"),
            ("workflow_execution_state", "deal_id"),
        ]:
            if table == "approvals" and deal:
                q = await session.execute(
                    text(
                        "SELECT a.* FROM approvals a "
                        "JOIN quotations q ON q.quotation_id = a.quotation_id "
                        "WHERE q.deal_id = :d"
                    ),
                    {"d": deal_id},
                )
            else:
                q = await session.execute(
                    text(f"SELECT COUNT(*) AS c FROM {table} WHERE {col} = :d"),
                    {"d": deal_id},
                )
                if table != "approvals":
                    print(f"{table}: count={q.scalar()}")
                    continue
            rows = q.mappings().all()
            print(f"{table}: {len(rows)} row(s)")
            for row in rows[:3]:
                print(" ", dict(row))

        qi = await session.execute(
            text(
                "SELECT qi.* FROM quotation_items qi "
                "JOIN quotations q ON q.quotation_id = qi.quotation_id "
                "WHERE q.deal_id = :d"
            ),
            {"d": deal_id},
        )
        items = qi.mappings().all()
        print(f"quotation_items: {len(items)} row(s)")


if __name__ == "__main__":
    deal_id = sys.argv[1] if len(sys.argv) > 1 else "a34162d0-5920-4039-9018-d4714af170b0"
    asyncio.run(audit_deal(deal_id))
