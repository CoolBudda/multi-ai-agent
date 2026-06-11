# Frontend Error Handling

## Purpose
Ensure the UI remains usable and informative when backend API calls fail or streams terminate unexpectedly.

## Scope
Inline error display, input recovery, retry affordance, and degraded state prevention for all API-driven surfaces.

## Requirements
- When a backend API call fails, display an inline error message in the relevant component.
- The error message suggests retrying.
- The UI does not become unresponsive or show a blank state after an error.
- The chat input is re-enabled after an error so the user can try again.

## Inputs
- Error responses from backend API calls.
- Unexpected stream termination events.
- TanStack Query error state.

## Outputs
- Inline error message in the chat or relevant component.
- Restored input state.
- Retry affordance (button or instruction).

## Business Rules
- No `any` types; use `unknown` with type guards at API boundaries.
- All errors surface through the TanStack Query error state or explicit catch handlers — not console-only.
- Never leave the user with a blank page or an unresponsive input.

## Workflow
1. API call or stream terminates with an error.
2. TanStack Query or the error handler catches the failure.
3. Inline error message renders in the affected component.
4. Input is re-enabled.
5. User can retry the action.

## Data Model
- `ApiError`: `{ message: string, statusCode?: number, retryable: boolean }`

## Error Handling
- All surfaces that call the backend must handle both network errors and non-2xx responses.
- Streaming errors must restore the input and show a message.
- Preference save errors must preserve the user's in-progress edits.

## Acceptance Criteria
- A failed API call shows an inline error message.
- The error message includes a retry suggestion.
- The chat input is re-enabled after any error.
- No surface becomes blank or unresponsive after an error.

## Open Questions
- None identified from the current requirements.
