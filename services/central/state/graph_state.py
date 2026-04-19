import operator
from typing import Annotated, Literal, NotRequired, TypedDict

Intent = Literal["TRACKING", "EVENTS", "SOP"]


class GraphState(TypedDict, total=True):
    query: str
    intent: NotRequired[Intent | None]
    agent_result: NotRequired[object | None]
    audit_log: NotRequired[Annotated[list[dict[str, object]], operator.add]]
    error: NotRequired[str | None]


def make_state(query: str) -> GraphState:
    """Return a valid initial GraphState with safe defaults for all optional fields."""
    return GraphState(query=query, intent=None, agent_result=None, audit_log=[], error=None)
