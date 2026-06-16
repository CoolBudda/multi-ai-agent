# Quickstart - Validate Intent Detection and Agent Routing

This guide defines end-to-end validation scenarios for feature 002.

## Prerequisites

- Python environment for `agentservice` is available.
- Backend dependencies are installed.
- Routing threshold and tie-window configuration are available to the orchestrator runtime.

## Validation Scenarios

### 1) Specialist routing above threshold

Command:

```bash
cd agentservice
pytest tests/workflows/test_intent_routing_specialist.py tests/agents/test_orchestrator_agent.py -q
```

Expected outcome:
- Requests with clear domain confidence above threshold route to the expected specialist.
- Exactly one destination is selected for each request.

Related references:
- Contract: `contracts/orchestrator-intent-routing.openapi.yaml`
- Data model: `IntentScore`, `RoutingDecision`

### 2) Companion fallback when no specialist exceeds threshold

Command:

```bash
cd agentservice
pytest tests/workflows/test_intent_routing_fallback.py tests/services/test_routing_policy.py -q
```

Expected outcome:
- Requests with all specialist scores at or below threshold route to `companion`.
- `fallback_to_companion=true` and rationale reason code is `below_threshold_fallback`.

Related references:
- Contract: `contracts/orchestrator-intent-routing.openapi.yaml`
- Data model: `RoutingDecision`

### 3) Deterministic tie-window handling and precedence order

Command:

```bash
cd agentservice
pytest tests/workflows/test_intent_routing_tie_break.py tests/agents/test_orchestrator_agent.py -q
```

Expected outcome:
- Top score deltas `<= 0.03` are treated as ties.
- Tied specialists resolve in fixed order: calendar > travel > dining > news.
- Replayed equivalent requests under same config produce identical destination.

Related references:
- Data model: `RoutingPolicySnapshot`, `RoutingDecisionRecord`

### 4) Routing rationale traceability

Command:

```bash
cd agentservice
pytest tests/workflows/test_routing_decision_record.py tests/api/test_orchestrator_route_contract.py -q
```

Expected outcome:
- Every routed request records threshold outcome, tie outcome, and selected destination in request context.
- Event names in traces follow `<domain>.<action>.<status>`.

Related references:
- Data model: `RoutingDecisionRecord`

### 5) Success criteria evidence capture

Command:

```bash
cd agentservice
pytest tests/agents/test_orchestrator_agent.py tests/workflows/test_intent_routing_specialist.py tests/workflows/test_intent_routing_fallback.py tests/workflows/test_intent_routing_tie_break.py tests/workflows/test_routing_decision_record.py tests/api/test_orchestrator_route_contract.py tests/services/test_routing_policy.py -q
```

Evidence template:

| Metric | Required | Observed | Result |
|---|---:|---:|---|
| In-scope first-pass specialist routing | >= 95% | 100% (specialist-suite assertions) | PASS |
| Low-confidence fallback to companion | 100% | 100% (fallback-suite assertions) | PASS |
| Deterministic replay under fixed config | 100% | 100% (tie-break + replay assertions) | PASS |

Status:
- Routing feature validation executed on 2026-06-16 with 29 passed tests and 0 failures.
