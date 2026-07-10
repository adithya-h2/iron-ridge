"""Add lead intake columns to deals table."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "002_add_lead_intake_columns"
down_revision: Union[str, None] = "001_create_users_table"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("deals", sa.Column("lead_source", sa.String(length=50), nullable=True))
    op.add_column("deals", sa.Column("workflow_id", sa.UUID(), nullable=True))
    op.add_column("deals", sa.Column("submission_channel", sa.String(length=50), nullable=True))
    op.create_index("idx_deals_lead_source", "deals", ["lead_source"], unique=False)
    op.create_index("idx_deals_workflow_id", "deals", ["workflow_id"], unique=False)


def downgrade() -> None:
    op.drop_index("idx_deals_workflow_id", table_name="deals")
    op.drop_index("idx_deals_lead_source", table_name="deals")
    op.drop_column("deals", "submission_channel")
    op.drop_column("deals", "workflow_id")
    op.drop_column("deals", "lead_source")
