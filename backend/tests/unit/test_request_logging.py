"""Request logging context tests."""

from app.core.log_context import get_log_context, set_log_context


def test_set_log_context():
    set_log_context(request_id="req-1", deal_id="deal-1", agent="MARTY")
    ctx = get_log_context()
    assert ctx["request_id"] == "req-1"
    assert ctx["deal_id"] == "deal-1"
    assert ctx["agent"] == "MARTY"
