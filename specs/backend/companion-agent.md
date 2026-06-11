# Companion Agent

## Purpose
Handle open-ended conversation, general Q&A, and brainstorming while routing sensitive content to the Safety/Policy layer.

## Scope
General conversational handling, Safety/Policy routing, fallback for unrecognized intents, and consistent tone maintenance.

## Requirements
- Engage in natural, open-ended dialogue.
- Answer general questions.
- Provide explanations, brainstorming, and casual conversation.
- Maintain consistent tone and personality.
- Route sensitive content to the Safety/Policy layer before responding.

## Inputs
- User message text.
- Conversation history context.
- Safety/Policy routing decision.

## Outputs
- Conversational response.
- Safety/Policy handoff when triggered.

## Business Rules
- Route to the Safety/Policy layer when the message contains mental health distress signals, requests for medical or legal advice, political opinion generation, or content that may violate content moderation policies.
- Handle all other requests directly without the Safety layer.
- Do not perform domain actions (booking, searching) in this agent.
- Serves as the Orchestrator's fallback when no domain matches.

## Workflow
1. Receive the user message.
2. Check for sensitive content signals.
3. Route to Safety/Policy layer if triggered.
4. Otherwise, generate a direct conversational response.
5. Maintain consistent tone throughout.

## Data Model
- `CompanionRequest`: `{ message, conversation_history }`
- `SafetyCheck`: `{ flagged: bool, category: str | None }`
- `CompanionResponse`: `{ response_text }`

## Error Handling
- If the Safety/Policy layer is unavailable, return a safe fallback response rather than bypassing the check.
- If the LLM cannot produce a confident answer, respond with a transparent limitation statement.

## Acceptance Criteria
- General questions are answered directly.
- Sensitive content is routed to the Safety/Policy layer.
- The agent does not execute domain-specific actions.
- Responses maintain a consistent tone.

## Open Questions
- None identified from the current requirements.
