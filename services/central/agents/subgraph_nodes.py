from dataclasses import dataclass
from typing import Callable

from services.central.policy import SentinelPolicy
from services.central.state import GraphState, Intent

from .agent_executor import AgentExecutor
from .crew_agents import AGENT_REGISTRY, DEFAULT_POLICY_MAP

_default_policy: SentinelPolicy = SentinelPolicy(DEFAULT_POLICY_MAP)
_default_executor: AgentExecutor = AgentExecutor(AGENT_REGISTRY, _default_policy)


@dataclass(frozen=True)
class AgentNode:
    executor: AgentExecutor
    agent_name: str
    tool_name: str

    def __call__(self, state: GraphState, **kwargs: object) -> GraphState:
        return self.executor.execute(self.agent_name, self.tool_name, state, **kwargs)


tracking_node: AgentNode = AgentNode(_default_executor, "tracking", "get_position")
events_node: AgentNode = AgentNode(_default_executor, "events", "query_events")
faq_node: AgentNode = AgentNode(_default_executor, "faq", "search_sop")

NODE_MAP: dict[Intent, Callable[[GraphState], GraphState]] = {
    "TRACKING": tracking_node,
    "EVENTS": events_node,
    "SOP": faq_node,
}
