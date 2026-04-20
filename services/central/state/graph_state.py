from __future__ import annotations

import operator
import sys
from typing import Annotated, Literal, Optional, TypedDict

if sys.version_info >= (3, 11):
    from typing import NotRequired
else:
    from typing_extensions import NotRequired

Intent = Literal["TRACKING", "EVENTS", "SOP"]


class GraphState(TypedDict, total=True):
    query: str
    intent: NotRequired[Optional[Intent]]
    agent_result: NotRequired[Optional[object]]
    audit_log: NotRequired[Annotated[list[dict[str, object]], operator.add]]
    error: NotRequired[Optional[str]]


def make_state(query: str) -> GraphState:
    return GraphState(query=query, intent=None, agent_result=None, audit_log=[], error=None)
