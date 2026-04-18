import operator
from typing import Annotated, Literal, NotRequired, TypedDict


class GraphState(TypedDict, total=True):
    query: str
    intent: NotRequired[Literal["TRACKING", "EVENTS", "SOP"] | None]
    agent_result: NotRequired[dict[str, object] | None]
    audit_log: NotRequired[Annotated[list[dict[str, object]], operator.add]]
    error: NotRequired[str | None]


def make_state(query: str) -> GraphState:
    """Return a valid initial GraphState with safe defaults for all optional fields."""
    return GraphState(query=query, intent=None, agent_result=None, audit_log=[], error=None)
