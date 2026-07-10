"""Lead field validation and normalization."""

import re

from app.core.enums import LeadSource
from app.core.exceptions import ValidationAppError
from app.schemas.lead import LeadIntakeRequest, NormalizedLead


class LeadValidator:
    """Validates and normalizes lead intake requests."""

    @staticmethod
    def _clean_str(value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned or None

    @staticmethod
    def _normalize_phone(phone: str | None) -> str | None:
        if not phone:
            return None
        digits = re.sub(r"\D", "", phone.strip())
        return digits or None

    def validate_and_normalize(self, request: LeadIntakeRequest) -> NormalizedLead:
        company = self._clean_str(request.company_name) or self._clean_str(request.org_name)
        if not company:
            raise ValidationAppError(
                "company_name or org_name is required",
                details={"fields": ["company_name", "org_name"]},
            )

        channel = self._clean_str(request.submission_channel)
        if not channel:
            raise ValidationAppError("submission_channel is required")

        try:
            source = (
                request.source
                if isinstance(request.source, LeadSource)
                else LeadSource(str(request.source).upper())
            )
        except ValueError as exc:
            valid = [s.value for s in LeadSource]
            raise ValidationAppError(
                f"Invalid source. Must be one of: {valid}",
                details={"allowed": valid},
            ) from exc

        qty: int | None = None
        if request.required_quantity is not None:
            try:
                qty = int(request.required_quantity)
            except (ValueError, TypeError) as exc:
                raise ValidationAppError(
                    "required_quantity must be an integer",
                    details={"value": str(request.required_quantity)},
                ) from exc

        email = str(request.email).lower().strip() if request.email else None

        return NormalizedLead(
            source=source,
            submission_channel=channel,
            company_name=company,
            contact_person=self._clean_str(request.contact_person),
            email=email,
            phone=self._normalize_phone(request.phone),
            website=self._clean_str(request.website),
            city=self._clean_str(request.city),
            state=self._clean_str(request.state),
            country=self._clean_str(request.country),
            industry=self._clean_str(request.industry),
            vehicle_type=self._clean_str(request.vehicle_type),
            required_quantity=qty,
            notes=self._clean_str(request.notes),
        )
