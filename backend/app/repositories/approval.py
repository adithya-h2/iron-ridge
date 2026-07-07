"""Approval repository."""

from app.models.approval import Approval
from app.repositories.base import BaseRepository


class ApprovalRepository(BaseRepository[Approval]):
    model = Approval
    pk_column = "approval_id"
