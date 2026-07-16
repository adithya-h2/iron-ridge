"""Request-scoped logging context via contextvars."""

from contextvars import ContextVar

request_id_var: ContextVar[str | None] = ContextVar("request_id", default=None)
deal_id_var: ContextVar[str | None] = ContextVar("deal_id", default=None)
workflow_id_var: ContextVar[str | None] = ContextVar("workflow_id", default=None)
agent_var: ContextVar[str | None] = ContextVar("agent", default=None)


def set_log_context(
    *,
    request_id: str | None = None,
    deal_id: str | None = None,
    workflow_id: str | None = None,
    agent: str | None = None,
) -> None:
    if request_id is not None:
        request_id_var.set(request_id)
    if deal_id is not None:
        deal_id_var.set(deal_id)
    if workflow_id is not None:
        workflow_id_var.set(workflow_id)
    if agent is not None:
        agent_var.set(agent)


def get_log_context() -> dict[str, str | None]:
    return {
        "request_id": request_id_var.get(),
        "deal_id": deal_id_var.get(),
        "workflow_id": workflow_id_var.get(),
        "agent": agent_var.get(),
    }
