# Orchestrator & Routing Implementation Plan

## 1. Goal
Direct restatement of the spec purpose: provide a single backend entry point that classifies user intent and routes requests to the correct specialist agent or combination of agents.

## 2. Scope Mapping
- Included: Intent detection, confidence-threshold routing, multi-domain parallel invocation, fallback handling, clarification questions, response aggregation.
- Excluded: TBD.

## 3. File Changes
- backend/agentservice/src/agents/orchestrator_agent.py
- backend/agentservice/src/graph/main_graph.py
- backend/agentservice/src/api/routes/chat.py
- backend/agentservice/src/models/state.py
- backend/agentservice/src/models/events.py
- backend/agentservice/tests/agents/test_orchestrator_agent.py
- backend/agentservice/tests/workflows/test_orchestrator_routing.py

## 4. LangGraph Nodes (if applicable)
- load_session_context
- detect_intent
- select_routed_agents
- invoke_agents_parallel
- collect_agent_results
- aggregate_or_passthrough_response
- return_clarifying_question_or_response

## 5. Tools
- Companion Agent
- Response Builder

## 6. State Updates
- user_id
- session_id
- intent
- confidence
- routed_agents
- agent_name
- response_text
- requires_approval
- final_response
- agent_responses

## 7. Implementation Steps (strict order)
1. Implement session context load from request metadata.
2. Implement intent detection and confidence scoring.
3. Implement routing selection for single-agent and multi-agent cases.
4. Implement fallback route to Companion Agent for low-confidence no-domain matches.
5. Implement targeted clarifying-question path for ambiguous but plausible single-domain requests.
6. Implement parallel invocation of selected specialist agents for multi-domain requests.
7. Implement response collection and merge behavior for multi-agent results.
8. Implement pass-through behavior for single-agent responses.
9. Emit agent.route.failed event on routing failure and preserve partial successful domain outputs on partial multi-domain failures.

## 8. Dependencies
- Companion Agent
- Response Builder

## 9. Test Plan
- Unit tests: Intent classification, confidence-threshold decisions, route selection, aggregation logic.
- Integration tests: Specialist-agent invocation wiring, fallback routing, clarifying-question handling, partial failure behavior.
- Workflow tests: End-to-end single-domain, multi-domain parallel, unknown-domain fallback, and ambiguous-message clarification flows.

## 10. Acceptance Criteria Mapping
- FR-001 Classify user requests into supported domains. -> Validate classification output includes intent and confidence.
- FR-002 Route single-domain requests to the correct specialist agent. -> Validate deterministic single-domain route selection.
- FR-003 Invoke all relevant agents in parallel for multi-domain requests. -> Validate concurrent multi-agent invocation and response collection.
- FR-004 Merge multiple agent responses into a single structured reply. -> Validate merged AggregatedResponse for multi-agent requests.
- FR-005 Pass single-agent responses through unchanged. -> Validate no transformation for single-agent response path.
- FR-006 Fall back to the Companion Agent when no domain matches with sufficient confidence. -> Validate fallback routing condition and route target.
- FR-007 Ask a targeted clarifying question when intent is ambiguous but a single domain is plausible. -> Validate clarifying-question response path condition.

## 11. Open Questions
- None identified from the current requirements.
