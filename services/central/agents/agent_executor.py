from __future__ import annotations

import dataclasses
from types import MappingProxyType

from services.central.policy import SentinelPolicy
from services.central.state import GraphState

from .crew_agents import AgentRuntime


class AgentExecutor:
    def __init__(
        self,
        registry: MappingProxyType[str, AgentRuntime] | dict[str, AgentRuntime],
        policy: SentinelPolicy,
    ) -> None:
        self._registry = registry
        self._policy = policy

    def execute(
        self,
        agent_name: str,
        tool_name: str,
        state: GraphState,
        **kwargs: object,
    ) -> GraphState:
        # Note: Phase 5 LangGraph node wrappers must return a partial state dict
        # (e.g. {"audit_log": [...], "agent_result": ...}) so the graph reducer
        # merges entries correctly. This method owns state mutation for now;
        # node wrappers will extract the relevant fields at that layer.
        runtime = self._registry[agent_name]

        rejection = self._policy.check(agent_name, tool_name)
        if rejection is not None:
            state["audit_log"].append(dataclasses.asdict(rejection))
            state["error"] = rejection.reason
            return state

        tool = runtime.tools[tool_name]
        try:
            result = tool(**kwargs)
        except Exception as exc:
            state["audit_log"].append(
                {"type": "tool_error", "agent": agent_name, "tool": tool_name, "error": str(exc)}
            )
            state["error"] = str(exc)
            return state

        state["audit_log"].append({"type": "tool_call", "agent": agent_name, "tool": tool_name})
        state["agent_result"] = result
        return state
