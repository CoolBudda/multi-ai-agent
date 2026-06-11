# Orchestrator & Routing

## Purpose
Provide a single backend entry point that classifies user intent and routes requests to the correct specialist agent or combination of agents.

## Scope
Intent detection, confidence-threshold routing, multi-domain parallel invocation, fallback handling, clarification questions, and response aggregation.

## Requirements
- Classify user requests into supported domains.
- Route single-domain requests to the correct specialist agent.
- Invoke all relevant agents in parallel for multi-domain requests.
- Merge multiple agent responses into a single structured reply.
- Pass single-agent responses through unchanged.
- Fall back to the Companion Agent when no domain matches with sufficient confidence.
- Ask a targeted clarifying question when intent is ambiguous but a single domain is plausible.

## Inputs
- User message text.
- Session context (user ID, session ID).
- Configured confidence threshold.

## Outputs
- Routed agent name(s).
- Aggregated or pass-through assistant response.
- Clarifying question (when applicable).
- Routing decision metadata (intent label, confidence score).

## Business Rules
- Specialist agents are never called directly by the frontend; all requests enter through the Orchestrator.
- If confidence is below the threshold and no domain is plausible, route to Companion Agent.
- Agents must not call each other directly; cross-agent coordination goes through the Orchestrator.
- Single-agent responses are passed to the Response Builder unchanged.
- Multi-agent responses are merged before reaching the Response Builder.

## Workflow
1. Load session context.
2. Detect intent and compute confidence score.
3. Select one or more agents based on intent.
4. Invoke selected agents (in parallel for multi-domain).
5. Collect and aggregate results.
6. Pass result to the Response Builder.

## Data Model
- `IntentResult`: `{ intent, confidence, routed_agents: list[str] }`
- `AgentResponse`: `{ agent_name, response_text, requires_approval: bool }`
- `AggregatedResponse`: `{ final_response, agent_responses: dict }`

## Error Handling
- If one agent in a multi-domain request fails, surface the failure for that domain and return successful results for the others.
- If intent detection fails, fall back to the Companion Agent.
- Emit `agent.route.failed` event on routing failure.

## Acceptance Criteria
- A clear single-domain message routes to the correct agent.
- An unrecognized message routes to the Companion Agent.
- A multi-domain message invokes relevant agents in parallel.
- Single-agent responses are not transformed.
- An ambiguous message triggers a clarifying question.

## Open Questions
- None identified from the current requirements.
