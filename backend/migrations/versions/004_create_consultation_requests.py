"""Create consultation_requests table."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "004_create_consultation_requests"
down_revision: Union[str, None] = "003_add_workflow_execution_state"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "consultation_requests",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("organization_name", sa.String(), nullable=False),
        sa.Column("organization_type", sa.String(), nullable=False),
        sa.Column("department", sa.String(), nullable=True),
        sa.Column("website", sa.String(), nullable=True),
        sa.Column("contact_person", sa.String(), nullable=False),
        sa.Column("job_title", sa.String(), nullable=True),
        sa.Column("business_email", sa.String(), nullable=False),
        sa.Column("phone_number", sa.String(), nullable=False),
        sa.Column("preferred_contact_method", sa.String(), nullable=True),
        sa.Column("country", sa.String(), nullable=False),
        sa.Column("state", sa.String(), nullable=False),
        sa.Column("city", sa.String(), nullable=False),
        sa.Column("vehicle_category", sa.String(), nullable=False),
        sa.Column("estimated_quantity", sa.String(), nullable=False),
        sa.Column("purchase_timeline", sa.String(), nullable=False),
        sa.Column("requirement_summary", sa.Text(), nullable=True),
        sa.Column("consent", sa.Boolean(), nullable=False),
        sa.Column("status", sa.String(), nullable=False, server_default="PENDING_VALIDATION"),
        sa.Column("lead_score", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("consultation_requests")
