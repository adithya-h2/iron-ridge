"""Add workflow_execution_state table for retry tracking."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "003_add_workflow_execution_state"
down_revision: Union[str, None] = "002_add_lead_intake_columns"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "workflow_execution_state",
        sa.Column("deal_id", sa.UUID(), nullable=False),
        sa.Column("attempt_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_attempt_at", sa.DateTime(), nullable=True),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.Column("retryable", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["deal_id"], ["deals.deal_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("deal_id"),
    )


def downgrade() -> None:
    op.drop_table("workflow_execution_state")
