"""Agent orchestrator — routes execution to the correct agent."""

from app.agents.adam import AdamAgent
from app.agents.lisa import LisaAgent
from app.agents.marty import MartyAgent
from app.agents.neil import NeilAgent
from app.agents.paul import PaulAgent
from app.agents.sally import SallyAgent
from app.core.enums import AgentName
from app.core.exceptions import NotFoundError
from app.schemas.agent import AgentExecuteRequest, AgentExecuteResponse


class AgentOrchestrator:
    def __init__(
        self,
        marty: MartyAgent,
        lisa: LisaAgent,
        neil: NeilAgent,
        paul: PaulAgent,
        sally: SallyAgent,
        adam: AdamAgent,
    ) -> None:
        self._agents = {
            AgentName.MARTY.value.lower(): marty,
            AgentName.LISA.value.lower(): lisa,
            AgentName.NEIL.value.lower(): neil,
            AgentName.PAUL.value.lower(): paul,
            AgentName.SALLY.value.lower(): sally,
            AgentName.ADAM.value.lower(): adam,
        }

    async def execute(self, agent_name: str, input_data: AgentExecuteRequest) -> AgentExecuteResponse:
        agent = self._agents.get(agent_name.lower())
        if agent is None:
            raise NotFoundError(f"Unknown agent: {agent_name}")
        return await agent.execute(input_data)
