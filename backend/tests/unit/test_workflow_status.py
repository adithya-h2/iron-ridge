"""Pipeline progress and workflow status unit tests."""

from app.core.enums import DealStatus, pipeline_progress_percentage


def test_pipeline_progress_lead():
    assert pipeline_progress_percentage(DealStatus.LEAD.value) > 0


def test_pipeline_progress_delivered():
    assert pipeline_progress_percentage(DealStatus.DELIVERED.value) == 100


def test_pipeline_progress_rejected():
    assert pipeline_progress_percentage(DealStatus.REJECTED.value) == 0
