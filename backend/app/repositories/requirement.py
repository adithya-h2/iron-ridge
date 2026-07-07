"""Requirement repository."""

from app.models.requirement import Requirement
from app.repositories.base import BaseRepository


class RequirementRepository(BaseRepository[Requirement]):
    model = Requirement
    pk_column = "requirement_id"
