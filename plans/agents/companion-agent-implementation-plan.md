# Companion Agent Implementation Plan

## 1. Goal
Direct restatement of the spec purpose: handle open-ended conversation, general Q&A, and brainstorming while routing sensitive content to the Safety/Policy layer.

## 2. Scope Mapping
- Included: General conversational handling, Safety/Policy routing, fallback for unrecognized intents, consistent tone maintenance.
- Excluded: Domain actions (booking, searching).

## 3. File Changes
- backend/agentservice/src/agents/companion_agent.py
- backend/agentservice/src/models/state.py
- backend/agentservice/tests/agents/test_companion_agent.py

## 4. LangGraph Nodes (if applicable)
- receive_message
- check_sensitive_content
- route_to_safety_policy
- generate_conversational_response
- enforce_consistent_tone

## 5. Tools
- Safety/Policy layer

## 6. State Updates
- message
- conversation_history
- flagged
- category
- response_text

## 7. Implementation Steps (strict order)
1. Implement message intake and conversation history mapping into CompanionRequest state.
2. Implement sensitive-content check for the defined categories.
3. Route flagged messages to Safety/Policy layer before response generation.
4. Generate direct conversational responses for non-flagged messages.
5. Enforce consistent tone and personality in all responses.
6. Enforce domain-action restriction so booking/searching actions are not executed in this agent.
7. Return safe fallback response when Safety/Policy layer is unavailable.
8. Return transparent limitation statement when confident answer cannot be produced.

## 8. Dependencies
- Safety/Policy layer

## 9. Test Plan
- Unit tests: Sensitive-content category detection, fallback response selection, tone consistency checks.
- Integration tests: Safety/Policy handoff path and unavailable-safety fallback behavior.
- Workflow tests: End-to-end non-sensitive conversation path and flagged-content routing path.

## 10. Acceptance Criteria Mapping
- FR-001 Engage in natural, open-ended dialogue. -> Validate direct conversational outputs for open-ended inputs.
- FR-002 Answer general questions. -> Validate general-question responses are returned without specialist routing.
- FR-003 Provide explanations, brainstorming, and casual conversation. -> Validate coverage across explanation/brainstorm/casual intents.
- FR-004 Maintain consistent tone and personality. -> Validate response tone consistency across multi-turn tests.
- FR-005 Route sensitive content to the Safety/Policy layer before responding. -> Validate flagged content is routed and not answered directly.

## 11. Open Questions
- None identified from the current requirements.
