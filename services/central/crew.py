from typing import Any, Hashable

from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from services.central.agents import events_node, faq_node, tracking_node
from services.central.router import router_node
from services.central.state import GraphState

__all__ = ["SENTINEL_GRAPH", "build_graph"]

# Single source of truth: intent value → LangGraph node name.
# Update here when adding a new specialist agent.
_INTENT_NODE_MAP: dict[str, str] = {
    "TRACKING": "tracking",
    "EVENTS": "events",
    "SOP": "faq",
}


def build_graph() -> CompiledStateGraph[GraphState, None, Any, Any]:
    def _route(state: GraphState) -> str:
        intent = state.get("intent")
        if intent is not None and intent in _INTENT_NODE_MAP:
            return intent
        return "__error__"

    graph: StateGraph[GraphState] = StateGraph(GraphState)

    graph.add_node("router", router_node)
    graph.add_node("tracking", tracking_node)
    graph.add_node("events", events_node)
    graph.add_node("faq", faq_node)

    graph.add_edge(START, "router")
    routing_edges: dict[Hashable, str] = {k: v for k, v in _INTENT_NODE_MAP.items()}
    routing_edges["__error__"] = END
    graph.add_conditional_edges("router", _route, routing_edges)
    graph.add_edge("tracking", END)
    graph.add_edge("events", END)
    graph.add_edge("faq", END)

    return graph.compile()


SENTINEL_GRAPH: CompiledStateGraph[GraphState, None, Any, Any] = build_graph()
