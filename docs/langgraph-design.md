# LangGraph Design

## Overview

This document describes the LangGraph implementation of the Personal Assistant Multi-Agent System. All agents run inside a single ECS Fargate service as Python modules and LangGraph subgraphs.

---

## State Schema

All nodes in the main graph and specialist subgraphs share a single typed state object.

```python
from typing import Literal
from typing_extensions import TypedDict


class AssistantState(TypedDict):
    # Request context
    user_id: str
    session_id: str
    user_input: str

    # Routing
    intent: Literal["calendar", "travel", "dining", "news", "companion", "multi"]
    routed_agents: list[str]               # one or more agent names
    confidence: float                      # intent detection score

    # Memory
    retrieved_preferences: dict            # loaded at agent start via Memory Service

    # Agent outputs
    agent_responses: dict[str, str]        # keyed by agent name

    # Approval
    approval_required: bool
    approval_status: Literal["pending", "approved", "rejected"] | None

    # Final output
    final_response: str
```

---

## Main Graph

The main graph is the single entry point for all user requests.

```
START
  │
  ▼
load_context          ← loads session + auth context
  │
  ▼
detect_intent         ← classifies domain, produces intent + confidence
  │
  ▼
route_request         ← selects one or more specialist subgraphs
  │
  ▼
run_agents            ← executes subgraphs (parallel when multi-domain)
  │
  ▼
approval_gate         ← conditional: skip if approval_required=False
  │
 ┌┴────────────────┐
No                Yes
 │                 │
 │          approval_node   ← pauses graph, awaits user confirmation
 │                 │
 └────────┬────────┘
          │
          ▼
  build_response            ← merges agent_responses into final_response
          │
          ▼
         END
```

### Graph Definition

```python
from langgraph.graph import StateGraph, END
from .state import AssistantState

def build_main_graph() -> StateGraph:
    graph = StateGraph(AssistantState)

    graph.add_node("load_context", load_context_node)
    graph.add_node("detect_intent", detect_intent_node)
    graph.add_node("route_request", route_request_node)
    graph.add_node("run_agents", run_agents_node)
    graph.add_node("approval_gate", approval_gate_node)
    graph.add_node("approval_node", approval_node)
    graph.add_node("build_response", build_response_node)

    graph.set_entry_point("load_context")
    graph.add_edge("load_context", "detect_intent")
    graph.add_edge("detect_intent", "route_request")
    graph.add_edge("route_request", "run_agents")
    graph.add_edge("run_agents", "approval_gate")
    graph.add_conditional_edges(
        "approval_gate",
        lambda s: "approval_node" if s["approval_required"] else "build_response",
    )
    graph.add_edge("approval_node", "build_response")
    graph.add_edge("build_response", END)

    return graph.compile()
```

---

## Node Definitions

### `load_context_node`

Loads session and auth context. Pure — no external I/O.

```python
def load_context_node(state: AssistantState) -> AssistantState:
    # Populate session_id, user_id from incoming request context.
    # No external calls here.
    return state
```

### `detect_intent_node`

Classifies the user request into one or more domains using the LLM.

```python
def detect_intent_node(state: AssistantState) -> AssistantState:
    # Returns intent (highest-confidence single domain) or "multi".
    # Sets confidence score.
    # Falls back to "companion" if no domain exceeds the threshold.
    ...
    return {**state, "intent": intent, "confidence": score}
```

### `route_request_node`

Maps intent to one or more agent names.

```python
ROUTING_TABLE = {
    "calendar": ["calendar_agent"],
    "travel":   ["travel_agent"],
    "dining":   ["dining_agent"],
    "news":     ["news_agent"],
    "companion": ["companion_agent"],
    "multi":    [],   # populated dynamically per detected domains
}

def route_request_node(state: AssistantState) -> AssistantState:
    agents = ROUTING_TABLE[state["intent"]]
    return {**state, "routed_agents": agents}
```

### `run_agents_node`

Executes the routed specialist subgraphs. Invokes multiple subgraphs in parallel for multi-domain requests.

```python
from concurrent.futures import ThreadPoolExecutor

def run_agents_node(state: AssistantState) -> AssistantState:
    subgraphs = {name: AGENT_REGISTRY[name] for name in state["routed_agents"]}
    responses: dict[str, str] = {}

    with ThreadPoolExecutor() as executor:
        futures = {name: executor.submit(graph.invoke, state) for name, graph in subgraphs.items()}
        for name, future in futures.items():
            result = future.result()
            responses[name] = result["agent_responses"].get(name, "")

    return {**state, "agent_responses": responses}
```

### `approval_gate_node`

Checks whether any agent response requires human approval before proceeding.

```python
def approval_gate_node(state: AssistantState) -> AssistantState:
    # Inspect agent_responses for write-operation flags.
    requires = any(needs_approval(r) for r in state["agent_responses"].values())
    return {**state, "approval_required": requires, "approval_status": "pending" if requires else None}
```

### `approval_node`

Pauses the graph and waits for user confirmation via the Approval Service.

- On **approved**: sets `approval_status = "approved"`, continues to `build_response`.
- On **rejected**: sets `approval_status = "rejected"`, emits `<domain>.<action>.rejected` event, proceeds to `build_response` which returns a cancellation message.

```python
def approval_node(state: AssistantState) -> AssistantState:
    result = approval_service.request(state["user_id"], state["agent_responses"])
    return {**state, "approval_status": result.status}
```

### `build_response_node`

Merges agent outputs into a single user-facing response.

- Single agent → passes the response through unchanged.
- Multiple agents → merges into a structured response.
- Rejected approval → returns a cancellation confirmation message.

```python
def build_response_node(state: AssistantState) -> AssistantState:
    if state.get("approval_status") == "rejected":
        final = "Your request was cancelled. No changes were made."
    elif len(state["agent_responses"]) == 1:
        final = next(iter(state["agent_responses"].values()))
    else:
        final = response_merger.merge(state["agent_responses"])
    return {**state, "final_response": final}
```

---

## Specialist Agent Subgraphs

Each specialist agent is a self-contained `StateGraph` subgraph. All subgraphs share the same `AssistantState`.

### Common Subgraph Pattern

```
START
  │
  ▼
load_memory          ← retrieves user preferences via Memory Service (only side effect in agent node)
  │
  ▼
reason               ← LLM reasoning with retrieved preferences
  │
  ▼
call_tools           ← external API calls via tool layer only
  │
  ▼
compose_response     ← formats agent output into agent_responses[agent_name]
  │
  ▼
END
```

### Calendar Agent

```python
from langgraph.graph import StateGraph, END
from .state import AssistantState
from .tools import OutlookCalendarTool

def build_calendar_agent() -> StateGraph:
    graph = StateGraph(AssistantState)

    graph.add_node("load_memory", calendar_load_memory)   # Memory Service call
    graph.add_node("reason", calendar_reason_node)
    graph.add_node("call_tools", calendar_tools_node)     # OutlookCalendarTool
    graph.add_node("compose_response", calendar_compose)

    graph.set_entry_point("load_memory")
    graph.add_edge("load_memory", "reason")
    graph.add_edge("reason", "call_tools")
    graph.add_edge("call_tools", "compose_response")
    graph.add_edge("compose_response", END)

    return graph.compile()
```

**Memory defaults**: if `meeting_start_time` is absent, defaults to `"09:00"`.

### Travel Agent

Tools: `FlightSearchTool`

**Memory defaults**: if `preferred_airline` is absent, searches all airlines. If `seat_preference` is absent, defaults to `"Aisle"`.

Cross-domain coordination: availability checks are sent to the Orchestrator, which routes to the Calendar Agent. The Travel Agent does not call the Calendar Agent directly.

### Dining Agent

Tools: `RestaurantSearchTool`

**Memory defaults**: if `favorite_cuisine` is absent, omits cuisine filter and returns diverse results.

### News Agent

Tools: `NewsSearchTool`

**Memory defaults**: if `news_topics` is absent or empty, returns general top headlines.

### Companion Agent

Tools: LLM only (no external tools by default).

Requests are routed to the Safety/Policy layer before LLM reasoning when the message contains: mental health distress signals, medical or legal advice requests, political opinion generation, or content that may violate content moderation policies.

---

## Tool Layer

All external I/O goes through tool nodes. Agent reasoning nodes never call external APIs directly.

```python
from langchain_core.tools import tool
from .services import microsoft_graph_service

@tool
def OutlookCalendarTool(user_id: str, query: str) -> dict:
    """Check or modify Outlook calendar via Microsoft Graph API."""
    return microsoft_graph_service.calendar_query(user_id, query)
```

If a tool call fails, the agent node must:
1. Emit a `<domain>.<action>.failed` event with the error code.
2. Return a user-facing message explaining the failure and suggesting a retry.
3. Never return partial results without indicating degradation.

```python
def calendar_tools_node(state: AssistantState) -> AssistantState:
    try:
        result = OutlookCalendarTool.invoke(...)
    except ServiceError as e:
        event_bus.emit(f"calendar.availability.failed", {"error_code": e.code})
        return {**state, "agent_responses": {"calendar_agent": "Unable to check your calendar right now. Please try again."}}
    return {**state, ...}
```

---

## Memory Service Integration

Memory is loaded once at the start of each specialist subgraph via a dedicated `load_memory` node. This is the only permitted side effect in an agent node; all other I/O must occur in tool nodes.

```python
def calendar_load_memory(state: AssistantState) -> AssistantState:
    prefs = memory_service.get(state["user_id"])
    return {**state, "retrieved_preferences": prefs or {}}
```

Missing fields are handled per-agent with sensible defaults (see each agent above). Agents must not block execution or raise errors on absent fields.

---

## Event Schema

All events follow the `<domain>.<action>.<status>` naming convention and are emitted to Amazon EventBridge.

| Event | Emitted by |
|---|---|
| `agent.request.received` | Orchestrator — `load_context` |
| `agent.intent.detected` | Orchestrator — `detect_intent` |
| `agent.route.completed` | Orchestrator — `route_request` |
| `calendar.availability.checked` | Calendar Agent |
| `calendar.event.created` | Calendar Agent |
| `calendar.availability.failed` | Calendar Agent |
| `travel.search.completed` | Travel Agent |
| `travel.booking.requested` | Travel Agent |
| `travel.search.failed` | Travel Agent |
| `dining.search.completed` | Dining Agent |
| `dining.reservation.requested` | Dining Agent |
| `dining.search.failed` | Dining Agent |
| `news.fetch.completed` | News Agent |
| `news.fetch.failed` | News Agent |
| `approval.required` | Approval Service |
| `approval.completed` | Approval Service |
| `<domain>.<action>.rejected` | Approval Service |
| `memory.preference.loaded` | Memory Service |

---

## File Structure

```
src/
  agents/
    orchestrator/
      graph.py          # Main StateGraph definition
      nodes.py          # load_context, detect_intent, route_request, run_agents, build_response
      state.py          # AssistantState TypedDict
    calendar/
      graph.py
      nodes.py
      tools.py          # OutlookCalendarTool
    travel/
      graph.py
      nodes.py
      tools.py          # FlightSearchTool
    dining/
      graph.py
      nodes.py
      tools.py          # RestaurantSearchTool
    news/
      graph.py
      nodes.py
      tools.py          # NewsSearchTool
    companion/
      graph.py
      nodes.py
  services/
    memory_service.py
    approval_service.py
    event_service.py
    microsoft_graph_service.py
tests/
  agents/
    orchestrator/
    calendar/
    travel/
    dining/
    news/
    companion/
  services/
```

---

## Testing Conventions

- Use Pytest fixtures to construct `AssistantState` instances.
- Mock all service layer calls; never hit live APIs in unit tests.
- Test each node function in isolation before testing full subgraph execution.

```python
import pytest
from src.agents.state import AssistantState

@pytest.fixture
def base_state() -> AssistantState:
    return AssistantState(
        user_id="test-user",
        session_id="test-session",
        user_input="",
        intent="companion",
        routed_agents=[],
        confidence=1.0,
        retrieved_preferences={},
        agent_responses={},
        approval_required=False,
        approval_status=None,
        final_response="",
    )
```
