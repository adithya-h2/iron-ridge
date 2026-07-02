"""
app/models/vehicle_master.py

SQLAlchemy ORM model for the `vehicle_master` table.

Source of truth: Supabase schema dump (tools/schema_dump.json)
Table name   : vehicle_master
Primary key  : vehicle_id (uuid)

Columns (exact match):
    vehicle_id    uuid       NOT NULL  PK
    vehicle_code  varchar    NULL
    vehicle_name  varchar    NULL
    category      varchar    NULL
    base_price    numeric    NULL
    description   text       NULL

Foreign keys TO this table:
    bom.vehicle_id -> vehicle_master.vehicle_id
"""

import uuid
from decimal import Decimal

from sqlalchemy import Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base


class VehicleMaster(Base):
    """ORM model for the `vehicle_master` table. Reference data for Paul."""

    __tablename__ = "vehicle_master"

    # ------------------------------------------------------------------
    # Primary Key
    # ------------------------------------------------------------------
    vehicle_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )

    # ------------------------------------------------------------------
    # Columns — exact names and types from deployed schema
    # ------------------------------------------------------------------
    vehicle_code: Mapped[str | None] = mapped_column(String, nullable=True)
    vehicle_name: Mapped[str | None] = mapped_column(String, nullable=True)
    category: Mapped[str | None] = mapped_column(String, nullable=True)
    base_price: Mapped[Decimal | None] = mapped_column(Numeric, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------
    boms: Mapped[list["BOM"]] = relationship(  # type: ignore[name-defined]
        "BOM",
        back_populates="vehicle",
        lazy="select",
    )

    def __repr__(self) -> str:
        return (
            f"<VehicleMaster id={self.vehicle_id} "
            f"code={self.vehicle_code!r} name={self.vehicle_name!r}>"
        )
