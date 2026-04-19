from dataclasses import dataclass
from types import MappingProxyType
from typing import Callable


@dataclass
class AgentRuntime:
    llm_model: str
    llm_temperature: float
    system_prompt: str
    tools: dict[str, Callable[..., object]]


def _get_position(**kwargs: object) -> dict[str, object]:
    return {"lat": 0.0, "lon": 0.0, "vessel": "stub"}


def _query_events(**kwargs: object) -> list[dict[str, object]]:
    return [{"event": "stub", "severity": "low"}]


def _search_sop(**kwargs: object) -> dict[str, object]:
    return {"answer": "stub SOP response"}


AGENT_REGISTRY: MappingProxyType[str, AgentRuntime] = MappingProxyType({
    "tracking": AgentRuntime(
        llm_model="gpt-4o-mini",
        llm_temperature=0.0,
        system_prompt="You are a vessel tracking agent.",
        tools={"get_position": _get_position},
    ),
    "events": AgentRuntime(
        llm_model="gpt-4o-mini",
        llm_temperature=0.0,
        system_prompt="You are a security events agent.",
        tools={"query_events": _query_events},
    ),
    "faq": AgentRuntime(
        llm_model="gpt-4o-mini",
        llm_temperature=0.0,
        system_prompt="You are a SOPs and procedures agent.",
        tools={"search_sop": _search_sop},
    ),
})

# Single source of truth for which tools each agent is authorised to call.
# Import this in subgraph_nodes.py and tests — never duplicate.
DEFAULT_POLICY_MAP: dict[str, set[str]] = {
    "tracking": {"get_position"},
    "events": {"query_events"},
    "faq": {"search_sop"},
}
