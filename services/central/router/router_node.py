from services.central.state import GraphState, Intent

INTENT_KEYWORDS: dict[Intent, tuple[str, ...]] = {
    "TRACKING": ("position", "location", "track", "vessel", "where", "lat", "lon"),
    "EVENTS": ("event", "alert", "alarm", "incident", "severity", "breach"),
    "SOP": ("sop", "procedure", "faq", "how to", "protocol", "guide", "runbook"),
}


def router_node(state: GraphState) -> GraphState:
    query_lower = state["query"].lower()
    for intent, keywords in INTENT_KEYWORDS.items():
        if any(kw in query_lower for kw in keywords):
            state["intent"] = intent
            state["error"] = None
            return state
    state["error"] = f"Router could not classify intent for query: {state['query']!r}"
    return state
