"""Lead validation repository."""

from app.models.lead_validation import LeadValidation
from app.repositories.base import BaseRepository


class LeadValidationRepository(BaseRepository[LeadValidation]):
    model = LeadValidation
    pk_column = "validation_id"
